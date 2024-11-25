import nest_asyncio
nest_asyncio.apply()
from CaC_open_position import my_position
import numpy as np
import pandas as pd
import ccxt
import concurrent.futures
import os
from termcolor import colored
from CaC_functions_fetch import *
import logging

def colorize_dataframe(df, exchange_column, color_mapping):
    # Function to colorize the DataFrame based on the exchange column
    df_colored = df.copy().round(2)
    for index, row in df_colored.iterrows():
        color = color_mapping[row[exchange_column]]
        df_colored.loc[index] = [colored(str(value), color) for value in row]
    return df_colored

def colorize_PnL(df, PnL_column:str='PnL'):
    # Function to colorize the DataFrame based on the PnL
    df_colored = df.copy().round(2).astype(object) #astype is needed to suppress Pandas depreciation warning.
    for index, row in df_colored.iterrows():
        color = 'red' if row[PnL_column] <= 0.0 else 'green'
        df_colored.loc[index] = [colored(str(value), color) for value in row]
    return df_colored

def get_terminal_size():
    try:
        # Unix-based systems
        return os.get_terminal_size()
    except OSError:
        # Default to some reasonable size if it fails
        return os.terminal_size((80, 24))

def FilterTickers(exchange:ccxt, Base:str='BTC', Type:str='future', Inverse:bool=True, start:int=None, stop:int=None, **kwargs) -> list[str]:
    #Load the whole market and filter out for all future tickers in the exchange.
    #May use only once for each exchanges as it can be slower than fetch the known tickers.
    #Return symbols
    markets = exchange.load_markets()
    def matches_conditions(market):
        """
        Function to check if all conditions in kwargs are met, including nested keys
        Example, base='BTC', type='future', info__kind='future'. 
        """
        for key, value in kwargs.items():
            keys = key.split('__')
            data = market
            for k in keys:
                if k in data:
                    data = data[k]
                else:
                    return False
            if data != value:
                return False
        return True
    # Filter markets based on base currency and any additional kwargs
    Base = [Base] if type(Base)==str else Base
    ExchangeTickers = []
    for base in Base:
        filtered_markets = [
            market for market in markets.values()
            if market['base'] == base and market['type'] == Type and market['inverse'] == Inverse and matches_conditions(market)
        ]
        logging.info(f"Found {len(filtered_markets)} symbols for {base} on {exchange.name}.")
        #Discard some expired soon futures if there to many.
        ExchangeTickers += filtered_markets[start:stop] if len(filtered_markets) > 4 else filtered_markets
    # Fetch ticker information for each BTC future
    tickers = []
    for future in ExchangeTickers:
        tickers.append(future['symbol'])
    return tickers 
def filter_multi_threads(ExchangeName:dict=None, Base:str|list[str]='BTC', Type:str='future', Inverse:bool=True, WhichTickersIndex:dict[str,tuple]=None, filter_kwargs:dict[str,dict]=None):
    """Calling FilterTickers using multithread can be faster when go over multiple exchanges.

    Args:
        ExchangeName (dict, optional): _description_. Defaults to None.
        Base (str | list[str], optional): _description_. Defaults to 'BTC'.
        Type (str, optional): _description_. Defaults to 'future'.
        Inverse (bool, optional): _description_. Defaults to True.
        WhichTickersIndex (dict[str,tuple], optional): _description_. Defaults to None.
        filter_kwargs (dict[str,dict], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if ExchangeName==None and WhichTickersIndex==None and filter_kwargs==None:
        raise ValueError(f"ExchangeName, WhichTickersIndex, filter_kwargs must be given.")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its exchange name
        future_to_func = {}
        for ExName, ExCCXT in ExchangeName.items():
            if True:
                (start, stop) = WhichTickersIndex[ExName]
                kwargs = filter_kwargs[ExName]
                future_to_func.update({ executor.submit(FilterTickers, ExCCXT(), Base, Type, Inverse, start, stop, **kwargs): ExName})
        results = {}
        for future in concurrent.futures.as_completed(future_to_func):
            ExName = future_to_func[future]
            try:
                data = future.result()
                results[ExName] = data
            except Exception as exc:
                print(f'{ExName.__name__} generated an exception: {exc}')
    return results


#Read my position and find PnL.
def PnL_Frame(combined_df: pd.DataFrame, df_fee:pd.DataFrame) -> pd.DataFrame:
    #Filter for matched Exchange and Symbol between my position and monitored.
    if len(my_position)==0:
        return None
    PositionFrame = pd.DataFrame(my_position)
    PositionFrame = pd.merge(PositionFrame, combined_df, on=['Exchange','Symbol'])
    if len(PositionFrame.index) == 0:
        PositionFrame["Entry Spr."] = None
        PositionFrame["PnL"] = None
    else:
        PositionFrame = pd.merge(PositionFrame, df_fee, on='Exchange')
        PositionFrame.rename(columns={"Spr.-f":"Current Spr."}, inplace=True)
        for index in PositionFrame.index:
            PositionFrame.loc[index,'SpotBuy'] = np.average(PositionFrame.loc[index]['SpotBuy']['AvgPrice'], weights=PositionFrame.loc[index]['SpotBuy']['Amount']).astype(float)
        MySpread = ( (PositionFrame["FutureShortPrice"]/PositionFrame["SpotBuy"] - 1)*100 ).astype(float)
        PositionFrame["Entry Spr."] = MySpread - PositionFrame["TotalFee"]
        PositionFrame["PnL"] = PositionFrame["Entry Spr."] - PositionFrame["Current Spr."]
    PositionFrame = PositionFrame.loc[:, ['Symbol','Exchange', 'Entry Spr.', "Current Spr.", 'PnL']]
    return PositionFrame

def fetch_concurrent(ExchangeTickers:dict, FetchTickersFucntion:dict):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its function
        future_to_func = {}
        for ExchangeName, TickersList in ExchangeTickers.items():
            if len(TickersList) != 0:
                future_to_func.update({ executor.submit(FetchTickersFucntion[ExchangeName], TickersList): FetchTickersFucntion[ExchangeName]})
        results = []
        for future in concurrent.futures.as_completed(future_to_func):
            func = future_to_func[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print(f'{func.__name__} generated an exception: {exc}')
    # Combine all DataFrames
    combined_df = pd.concat(results, ignore_index=True)
    return combined_df.loc[:, ['Symbol', 'APY','Spread', 'Exchange','Spot', 'Future']]

def fetch_main(ExchangeTickers:dict, FetchTickersFucntion:dict, ExchangeFee:dict):
    if len(ExchangeTickers) == 1:
        raise ValueError(f"This function does not work when len(ExchangeTickers) == 1. Might need flag to handle this.")
    #Create dataframe of exchange fee.
    df_fee = [(CEX_name, TotalFee) for CEX_name, TotalFee in ExchangeFee.items()]
    df_fee = pd.DataFrame(df_fee, columns=['Exchange', 'TotalFee'])
    #Fetch for a future table, use multithread for multiple exchanges.
    df_future = fetch_concurrent(ExchangeTickers, FetchTickersFucntion) 
    #Compute returns after exchange fees and sort by APY.
    df_future = pd.merge(df_future, ComputeAPYwithFee(df_future, df_fee), on=['Symbol', 'Exchange']).sort_values(by=['Symbol','APY-f'], ascending=False)
    df_future = df_future.loc[:, ['Symbol','Exchange','Spot','Future','Spr.-f','APY-f']]
    df_position = PnL_Frame(df_future, df_fee)
    return df_future, df_position