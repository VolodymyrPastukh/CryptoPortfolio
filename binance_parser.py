import pandas as pd
import numpy as np
import warnings
from utils import *
warnings.filterwarnings('ignore')

def binance_parsing_process():
    print('Parse Binance spot operations reports...')
    print('Ensure you have corresponding files [binance_1/2/3.csv] in this derectory and press to continue...')
    print('Press `Q` to exit...')

    if input().lower() != 'q':
        files = [f for f in os.listdir() if os.path.isfile(f) and 'binance' in f and '.csv' in f]

        if len(files) > 0:
            print(files)
            files_dfs = map(lambda file: pd.read_csv(file), files)
            print('Parsing can take a while...')
            binance_history_df = pd.concat(files_dfs).reset_index()
            result_df = parse_binance_parse(binance_history_df)

            clean_screen()
            filters = ['BUSD', 'USDT', 'ETH', 'SOL', 'BTC', 'BNB', 'NEAR', 'ATOM','DOT']
            print('Would you like to filter your report with the next tickers? Press `Y` to filter...')
            print('This tickers give more accurate result for now')
            print(filters)
            if input().lower() == 'y':
                result_df.to_csv(FULL_SPOT_HISTORY_FILE)
                result_df = result_df.loc[result_df['Ticker'].isin(filters)]
                result_df = result_df.iloc[::-1].reset_index().drop('index', axis=1)
            print(result_df.head(20))
            result_df.to_csv(SPOT_HISTORY_FILE)
            print('Reports were successfuly parsed!')
            print('Now you can import in to your GoogleSheet')
        else:
            print('Report files not found!')
