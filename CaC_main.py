print("Python Code Starting.")
import time
import os
import ccxt
from tabulate import tabulate
from logo import btc_logo
from CaC_functions import *
from config import *
def main():
    # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Loading markets...")
    #Get symbols to monitor.
    ExchangeTickers = filter_multi_threads(ExchangeName, Base, Type, Inverse,WhichTickersIndex, filter_kwargs)
    print("Done.")

    while True:
        print("FETCHING...")
        combined_df, position_PnL = fetch_main(ExchangeTickers, FetchTickersFucntion, ExchangeFee)
        combined_df = combined_df.round(2)
        #Colorize unique exchanges.
        combined_df = colorize_dataframe(combined_df, 'Exchange', exchange_colors)
        table_spread = tabulate(combined_df, headers='keys', tablefmt='psql', showindex=False)
        # Print the DataFrame
        os.system('cls' if os.name == 'nt' else 'clear')
        print(table_spread)
        if position_PnL is not None:
            position_PnL = colorize_PnL(position_PnL, PnL_column='PnL') #Write PnL table from my position and colorized.
            table_position = tabulate(position_PnL, headers='keys', tablefmt='psql', showindex=False)
            print("### My Positions ###")
            print(table_position)
        #Print logo and last update.
        logo_lines = logo.split('\n')
        logo_lines[1] += f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        for line in logo_lines:
            print(line)
        # Wait the next update
        time.sleep(RefreshTime)
        
if __name__=="__main__":
    main()