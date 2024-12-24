import ccxt
from CaC_fetch_functions import *
from logo import btc_logo

RefreshTime=60 #in second.
Base = ['BTC','ETH']#,'SOL'] #Ticker of crypto to monitor.
logo = btc_logo # Bitcoin logo in ASCII art. For screen decoration :)
Base = [Base] if type(Base)==str else Base
Type = 'future'#Keep this for compatibility.
Inverse = True #True for Coin-M, False for USD-M. Note that only Coin-M has been test.
ExchangeName = {}
ExchangeFee = {} #(%total fee) assuming no token-holder discount and lowest fee tier. we use fee=maker_buy(spot)+taker_short(future)+maker_long(future)+taker_sell(spot).
filter_kwargs = {} #certain CEX need filtering kw. Use {} if unknown or not needed.
FetchTickersFucntion = {} #fetching function for individual CEXs.
WhichTickersIndex = {} #Used for slicing out unwanted futures. 
exchange_colors = {}# Unique colors for each exchanges
exchangeConfig = {'Kucoin':{ 'ExchangeName': ccxt.kucoinfutures,
                            'ExchangeFee': 0.28, 
                            'filter_kwargs': {},
                            'FetchTickersFucntion': FetchTickersKucoin,
                            'WhichTickersIndex':(None,None),
                            'exchange_colors': 'green'},
                    'Bybit': { 'ExchangeName': ccxt.bybit,
                            'ExchangeFee': 0.275, 
                            'filter_kwargs': {},
                            'FetchTickersFucntion': FetchTickersBybit,
                            'WhichTickersIndex':(None,None),
                            'exchange_colors': 'light_yellow'},
                    'Deribit': { 'ExchangeName': ccxt.deribit,
                            'ExchangeFee': 0.05, 
                            'filter_kwargs': {'info__kind':'future'},
                            'FetchTickersFucntion': FetchTickersDeribit,
                            'WhichTickersIndex':(None,None), #(-4, -2),
                            'exchange_colors': 'light_green'},
                    'OKX': { 'ExchangeName': ccxt.okx,
                            'ExchangeFee': 0.19, 
                            'filter_kwargs': {},
                            'FetchTickersFucntion': FetchTickersOKX,
                            'WhichTickersIndex':(None,None), # (-2,None)
                            'exchange_colors': 'white'},
                    'Binance': { 'ExchangeName': ccxt.binancecoinm,
                            'ExchangeFee': 0.27, 
                            'filter_kwargs': {},
                            'FetchTickersFucntion': FetchTickersBinance,
                            'WhichTickersIndex':(None,None),
                            'exchange_colors': 'yellow'},
                    'Bitget': { 'ExchangeName': ccxt.bitget,
                            'ExchangeFee': 0.28, 
                            'filter_kwargs': {},
                            'FetchTickersFucntion': FetchTickersBitget,
                            'WhichTickersIndex':(None,None),
                            'exchange_colors': 'blue'}
                }
for key, info in exchangeConfig.items():
    ExchangeName[key] = info['ExchangeName']
    ExchangeFee[key] = info['ExchangeFee']
    filter_kwargs[key] = info['filter_kwargs']
    FetchTickersFucntion[key] = info['FetchTickersFucntion']
    WhichTickersIndex[key] = info['WhichTickersIndex']
    exchange_colors[key] = info['exchange_colors']