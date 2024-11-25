If you find my project helpful, you can donate me for a cup of coffee, or some beers so I can code more :) <a href="https://www.buymeacoffee.com/jrwsp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>

BTC: bc1q2zpmmlz7ujwx2ghsgw5j7umv8wmpchplemvhtu <br>
ETH: 0x80e98FcfED62970e35a57d2F1fefed7C89d5DaF4


# Cash-and-carry arbitrage monitoring
Python script for monitoring the cash-and-carry arbitrage opportunity across centralized exchanges on terminal.

## Running on terminal
One can run the monitoring script directly in terminal. To do this, simply type:
```
python CaC_main.py
```
The script will start fetching price data from exchanges. After a few moment you should see the spreads on terminal screen.
![terminal_screen](/figures/spread_terminal.png)

## requirement
- Python 3.xx (Tested with 3.11 and 3.12)
- Pandas
- ccxt
- tabulate
- nest-asyncio
- termcolor


## Adding new CEX
Each exchange needs their own fetch function, because there is different information can be accessible by `ccxt` library. To add a new exchange you need to put your own fetching function in `CaC_functions_fetch.py` and add the function name in `FetchTickersFunction` variable in `config.py`.