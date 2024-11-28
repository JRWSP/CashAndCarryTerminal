import ccxt
from CaC_fetch_functions import *
from logo import btc_logo

RefreshTime=15 #in second.
Base = ['BTC','ETH']#,'SOL'] #Ticker of crypto to monitor.
Type = 'future'#Keep this for compatibility.
Inverse = True #True for Coin-M, False for USD-M. Note that only Coin-M has been test.
ExchangeName = {'Kucoin': ccxt.kucoinfutures,
                'Bybit': ccxt.bybit, 
                #'Deribit' : ccxt.deribit, 
                'OKX' : ccxt.okx, 
                'Binance': ccxt.binancecoinm}
ExchangeFee = { #(%total fee) assuming no token-holder discount and lowest fee tier.
    # we use fee=maker_buy(spot)+taker_short(future)+maker_long(future)+taker_sell(spot).
    'Kucoin': 0.28,
    'Bybit': 0.275, 
    'Deribit': 0.05, #Too cheap, high risk?
    'OKX': 0.19, #USDC pairs
    'Binance': 0.27,
    'Bitget': 0.28 #Not available yet.
}
filter_kwargs = { #certain CEX need filering. Use {} if unknown.
                    'Kucoin': {},
                    'Bybit': {},
                    'Deribit': {'info__kind':'future'}, 
                    'OKX': {},
                    'Binance': {} }        
FetchTickersFucntion = { #fetching function for individual CEXs.
                "Kucoin": FetchTickersKucoin, 
                #"Deribit": FetchTickersDeribit,
                "Bybit": FetchTickersBybit,
                "OKX": FetchTickersOKX,
                 "Binance": FetchTickersBinance }  
WhichTickersIndex = { #Used for filtering out unwanted futures. 
                'Kucoin': (None,None),
                'Bybit': (None, None), 
                'Deribit' : (None,None), #(-4, -2),
                'OKX' : (None,None),# (-2,None)
                'Binance' : (None,None)} 

color_options = [# Unique colors for each exchanges
                    'green',
                    'yellow',
                    'magenta', 
                    'blue', 
                    'cyan'] #'red', ]

logo = btc_logo # Bitcoin logo in ASCII art. For screen decoration :)

exchange_colors = {exchange: color_options[i % len(color_options)] for i, exchange in enumerate(ExchangeName.keys())}
Base = [Base] if type(Base)==str else Base