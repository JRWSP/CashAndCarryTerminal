from datetime import datetime
import numpy as np
import pandas as pd
import ccxt
from CaC_functions import DeliveryTimeFromTicker,CreateDataFrame

def FetchTickersBybit(Tickers: list[str], exchange:ccxt, ex_name:str):
    market = exchange.markets if exchange.markets else exchange.load_markets()
    timestamp = datetime.fromtimestamp(exchange.milliseconds()/1000)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        markPrice = float(ticker['info']['markPrice'])
        indexPrice = float(ticker['info']['indexPrice'])
        DeliveryTime = datetime.fromtimestamp(int(ticker['info']['deliveryTime'])/1000)
        df = CreateDataFrame(DeliveryTime,timestamp,markPrice,indexPrice,ex_name,symbol)
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersDeribit(Tickers: list[str], exchange:ccxt, ex_name:str):
    market = exchange.markets if exchange.markets else exchange.load_markets()
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
            df = CreateDataFrame(DeliveryTime,timestamp,markPrice,SpotPrice,ex_name,symbol)
            SpreadData = pd.concat([SpreadData, df], ignore_index=True) 
    return SpreadData

def FetchTickersKucoin(Tickers: list[str], exchange:ccxt, ex_name:str):
    market = exchange.markets if exchange.markets else exchange.load_markets()
    timestamp = datetime.fromtimestamp(exchange.milliseconds()/1000)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        markPrice = float(ticker['info']['markPrice'])
        indexPrice = float(ticker['info']['indexPrice'])
        DeliveryTime = datetime.fromtimestamp(ticker['info']['settleDate']/1000)
        df = CreateDataFrame(DeliveryTime,timestamp,markPrice,indexPrice,ex_name,symbol)
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersOKX(Tickers: list[str], exchange:ccxt, ex_name:str):
    market = exchange.markets if exchange.markets else exchange.load_markets()
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
        df = CreateDataFrame(DeliveryTime,timestamp,markPrice,indexPrice,ex_name,symbol)
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersBinance(Tickers: list[str], exchange:ccxt, ex_name:str):
    #For Binance, exchange contains (future_exchange, spot_exchange). 
    def GroupedSpotSymbol(Tickers):
        grouped_tickers = []
        for Ticker in Tickers:
            key = Ticker[:3]
            if key not in grouped_tickers:
                grouped_tickers.append(key)
        return grouped_tickers
    
    (future_ex, spot_ex) = exchange
    market = future_ex.markets if future_ex.markets else future_ex.load_markets()
    market_s = spot_ex.markets if spot_ex.markets else spot_ex.load_markets()
    grouped_tickers = GroupedSpotSymbol(Tickers)
    grouped_tickers = [ticker+"/USDT" for ticker in grouped_tickers]
    FetchSpot = spot_ex.fetch_tickers(grouped_tickers)
    FetchedTickers = future_ex.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        Spot = FetchSpot[symbol[:3]+"/USDT"]
        timestamp = datetime.fromtimestamp(Spot['timestamp']/1000)
        markPrice = float(ticker['last'])
        indexPrice = float(Spot['last'])
        DeliveryTime = market[symbol]['expiry']
        DeliveryTime = datetime.fromtimestamp(int(DeliveryTime)/1000)
        df = CreateDataFrame(DeliveryTime,timestamp,markPrice,indexPrice,ex_name,symbol)
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData

def FetchTickersBitget(Tickers: list[str], exchange:ccxt, ex_name:str):
    market = exchange.markets if exchange.markets else exchange.load_markets()
    timestamp = datetime.fromtimestamp(exchange.milliseconds()/1000)
    FetchedTickers = exchange.fetch_tickers(Tickers)
    SpreadData = pd.DataFrame()
    for ticker in FetchedTickers.values():
        symbol = ticker['symbol']
        markPrice = float(ticker['info']['markPrice'])
        indexPrice = float(ticker['info']['indexPrice'])
        DeliveryTime = datetime.fromtimestamp(int(ticker['info']['deliveryTime'])/1000)
        df = CreateDataFrame(DeliveryTime,timestamp,markPrice,indexPrice,ex_name,symbol)
        SpreadData = pd.concat([SpreadData, df], ignore_index=True)
    return SpreadData