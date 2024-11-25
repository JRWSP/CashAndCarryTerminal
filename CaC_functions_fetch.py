from datetime import datetime
import numpy as np
import pandas as pd
import ccxt


def DeliveryTimeFromTicker(ticker:str):
    yymmdd = ticker[-6:]
    return datetime.strptime(yymmdd,'%y%m%d')  #Date code, e.g. yymmdd.

def FindDaysUntilExpire(APY:float, Spread:float) -> float:
    return np.log(1+APY/100)/np.log(1+Spread/100)

def FindAPY(Spread:float, Days:float) -> float:
    return ((1+Spread/100)**Days - 1)*100

def FetchTickersBybit(Tickers: list[str]):
    exchange = ccxt.bybit()
    market = exchange.load_markets()
    timestamp = datetime.fromtimestamp(exchange.milliseconds()/1000)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        markPrice = float(ticker['info']['markPrice'])
        indexPrice = float(ticker['info']['indexPrice'])
        DeliveryTime = datetime.fromtimestamp(int(ticker['info']['deliveryTime'])/1000)
        RemainingDay = (DeliveryTime - timestamp).total_seconds()/60/60/24
        Days = 365/RemainingDay
        Spread = (markPrice/indexPrice - 1.0)*100
        APY = FindAPY(Spread, Days)
        df = pd.DataFrame({'Exchange':['Bybit'], 'Symbol': [symbol], 
                               'Spread': Spread, 
                               'APY': APY, 
                               'Spot': indexPrice, 
                               'Future': markPrice})
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersDeribit(Tickers: list[str]):
    exchange = ccxt.deribit()
    market = exchange.load_markets()
    SpreadData = pd.DataFrame()
    """
    Deribit's fetch_tickers need same currency code to fetch multiple symbols.
    Hence preprocess the symbols are needed.
    """
    # Dictionary to hold the grouped elements
    grouped_tickers = {}
    # Iterate through each element in the list
    for Ticker in Tickers:
        # Extract the first three letters
        key = Ticker[:3]
        # If the key doesn't exist in the dictionary, create a new list
        if key not in grouped_tickers:
            grouped_tickers[key] = []
        # Append the element to the corresponding list
        grouped_tickers[key].append(Ticker)
    for code, grouped_ticker in grouped_tickers.items():
        """Start loops over currency codes."""
        #Get Spot prices.
        SpotSymbol = code+"/USDT"
        if SpotSymbol not in market: 
            raise ValueError(f"{exchange.name} does not have {SpotSymbol} in spot.")
        SpotPrice = float(exchange.fetch_ticker(SpotSymbol)['info']['mark_price'])
        FetchedTickers = exchange.fetch_tickers(grouped_ticker, params={'code':code})
        for ticker in FetchedTickers.values():
            timestamp = datetime.fromtimestamp(ticker['timestamp']/1000)
            symbol = ticker['symbol']
            markPrice = float(ticker['info']['mark_price'])
            DeliveryTime = datetime.strptime(ticker['symbol'][-6:],'%y%m%d')  #Date code, e.g. yymmdd.
            RemainingDay = (DeliveryTime - timestamp).total_seconds()/60/60/24
            Days = 365/RemainingDay
            Spread = (markPrice/SpotPrice - 1.0)*100
            APY = FindAPY(Spread, Days)
            df = pd.DataFrame({'Exchange':[exchange.name], 'Symbol': [symbol], 
                                'Spread': Spread, 
                                'APY': APY, 
                                'Spot': SpotPrice, 
                                'Future': markPrice})
            SpreadData = pd.concat([SpreadData, df], ignore_index=True) 
    return SpreadData

def FetchTickersKucoin(Tickers: list[str]):
    exchange = ccxt.kucoinfutures()
    market = exchange.load_markets()
    timestamp = datetime.fromtimestamp(exchange.milliseconds()/1000)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        markPrice = float(ticker['info']['markPrice'])
        indexPrice = float(ticker['info']['indexPrice'])
        DeliveryTime = datetime.fromtimestamp(ticker['info']['settleDate']/1000)
        RemainingDay = (DeliveryTime - timestamp).total_seconds()/60/60/24
        Days = 365/RemainingDay
        Spread = (markPrice/indexPrice - 1.0)*100
        APY = FindAPY(Spread, Days)
        df = pd.DataFrame({'Exchange':['Kucoin'], 'Symbol': [symbol], 
                               'Spread': Spread, 
                               'APY': APY, 
                               'Spot': indexPrice, 
                               'Future': markPrice})
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersOKX(Tickers: list[str]):
    exchange = ccxt.okx()
    market = exchange.load_markets()
    #Get Spot prices.
    for ticker in Tickers:
        SpotSymbol = list(set([ticker[:3]+"/USDT" for ticker in Tickers])) #Get unique spot ticker from future ticker.
    if all(spot in market for spot in SpotSymbol):
        FetchedSpot = exchange.fetch_tickers(SpotSymbol) #Get spot price from 'ask' spot symbol.
    else:
        raise ValueError(f"OKX does not have {SpotSymbol} in spot.")
    FetchedTickers = exchange.fetch_tickers(Tickers)
    
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        timestamp = datetime.fromtimestamp(ticker['timestamp']/1000)
        markPrice = float(ticker['ask'])
        indexPrice = float(FetchedSpot[symbol[:3]+"/USDT"]['ask'])
        DeliveryTime = DeliveryTimeFromTicker(symbol)
        RemainingDay = (DeliveryTime - timestamp).total_seconds()/60/60/24
        Days = 365/RemainingDay
        Spread = (markPrice/indexPrice - 1.0)*100
        APY = FindAPY(Spread, Days)
        df = pd.DataFrame({'Exchange':['OKX'], 'Symbol': [symbol], 
                               'Spread': Spread, 
                               'APY': APY, 
                               'Spot': indexPrice, 
                               'Future': markPrice})
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersBinance(Tickers: list[str]):

    def GroupedSpotSymbol(Tickers):
        grouped_tickers = []
        for Ticker in Tickers:
            key = Ticker[:3]
            if key not in grouped_tickers:
                grouped_tickers.append(key)
        return grouped_tickers
    
    exchange = ccxt.binancecoinm()
    market = exchange.load_markets()
    grouped_tickers = GroupedSpotSymbol(Tickers)
    grouped_tickers = [ticker+"/USDT" for ticker in grouped_tickers]
    SpotPriceDict = {}
    FetchSpot = ccxt.binance().fetch_tickers(grouped_tickers)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        Spot = FetchSpot[symbol[:3]+"/USDT"]
        timestamp = datetime.fromtimestamp(Spot['timestamp']/1000)
        markPrice = float(ticker['last'])
        indexPrice = float(Spot['last'])
        DeliveryTime = market[symbol]['expiry']
        DeliveryTime = datetime.fromtimestamp(int(DeliveryTime)/1000)
        RemainingDay = (DeliveryTime - timestamp).total_seconds()/60/60/24
        Days = 365/RemainingDay
        Spread = (markPrice/indexPrice - 1.0)*100
        APY = FindAPY(Spread, Days)
        df = pd.DataFrame({'Exchange':["Binance"], 'Symbol': [symbol], 
                               'Spread': Spread, 
                               'APY': APY, 
                               'Spot': indexPrice, 
                               'Future': markPrice})
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def ComputeAPYwithFee(df:pd.DataFrame, df_fee:pd.DataFrame) -> pd.DataFrame:
    """    
    Return a dataframe with computed spread and APY after fees.
    APY is computed using remaining days till expiration.
    Args:
        df (pd.DataFrame): main table
        df_fee (pd.DataFrame): table containing information about CEX's fee.

    Returns:
        pd.DataFrame: main table with fee-adjusted APY.
    """
    merge_fee = pd.merge(df, df_fee, on="Exchange")
    N = FindDaysUntilExpire(merge_fee.APY, merge_fee.Spread)
    merge_fee['Spr.-f'] = merge_fee['Spread'] - merge_fee['TotalFee']
    #merge_fee['SpreadTaker'] = merge_fee['Spread'] - merge_fee['Taker']
    merge_fee['APY-f'] = FindAPY((merge_fee["Spr.-f"]), N)
    #merge_fee['APY_Taker'] = FindAPY((merge_fee.SpreadTaker), N)
    return merge_fee.loc[:, ['Symbol', 'Exchange', 'Spr.-f','APY-f']]