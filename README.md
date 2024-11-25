If you find my project helpful, you can donate me for a cup of coffee, or some beers so I can code more :) <a href="https://www.buymeacoffee.com/jrwsp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>

BTC: bc1q2zpmmlz7ujwx2ghsgw5j7umv8wmpchplemvhtu <br>
ETH: 0x80e98FcfED62970e35a57d2F1fefed7C89d5DaF4

# Cash-and-carry arbitrage monitoring
Simple Python script for monitoring the cash-and-carry arbitrage opportunity across centralized exchanges on terminal.
</br>
One can run the monitoring script directly in terminal. To do this, simply type:
```
python CaC_main.py
```
The script will start fetching price data from exchanges. After a few moment you should see the spreads on terminal screen.
![terminal_screen](/figures/spread_terminal.png)

Spr.-f (%) is a spread between spot and future prices adjusted by exchange's fee. </br>
APY-f (%) is annualized return adjusted by exchange's fee. </br>
Depends on data accessible by `ccxt` library, spot and future prices can be either a mark price or last price. Please verify the actual price on exchange before starting your trades.
## requirement
- Python 3.xx (Tested with 3.11 and 3.12)
- Pandas
- ccxt
- tabulate
- nest-asyncio
- termcolor


## Adding new CEX
Each exchange needs their own fetch function, because there is different information can be accessible by `ccxt` library. To add a new exchange you need to put your own fetching function in `CaC_functions_fetch.py` and add the function name in `FetchTickersFunction` variable in `config.py`. Some variables in `config.py`, such as fee, also need accordingly. 

## Open position 
You can also monitor your current open position by add the information in `CaC_open_position.py`. If there is no open position, simply set `my_position=[]`.
![position2](/figures/position_example_2.png)
- `FutureShortPrice` is effective entry price of `Symbol` short position. This is what you see in CEX's open position tab.  
- `SpotBuy` is an average buying spot price. If you have multiple buys, simply add each buy as an list' element respectively. The script will calculate weighted average price automatically.

When running the script you should see the position table below the main table. The script will calculate your entry %spread and compare with the current %spread to show the %PnL.
![position1](/figures/position_example_1.png)