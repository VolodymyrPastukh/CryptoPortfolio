#author: V.Androidovych
#version: 1.1.0

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import json
from utils import *
from binance_parser import binance_parsing_process
warnings.filterwarnings('ignore')

#----------------------functions
print('Start...')
print('Be sure you have network connection!')
print('Preparing resources, it can take a while...')

def fetch_purchases_history():
    with open('config.json') as f:
        config = json.load(f)

    sheet_id = config['sheet_id']
    sheet_name = config['sheet_name']
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

    try:
        google_sheet_df = pd.read_csv(url)
        if len(google_sheet_df) != 0:
            return google_sheet_df
        else:
            return pd.read_csv('spot_history_v1.0.csv')
    except:
        print('Something went wrong while loading data')
        return google_sheet_df

#----------------------main
files = [f for f in os.listdir() if os.path.isfile(f) and '.csv' in f]
found_spot_history = SPOT_HISTORY_FILE in files
if not found_spot_history:
    print('Would you like to generate data from binance reports? Press `Y` or any key to skip...')
    if input().lower() == 'y': binance_parsing_process()

print('Press any key to generate portfolio info or `Q` to exit...')

while input().lower() != 'q':
	clean_screen()
	print('---------------------------------------------------------------------')
	print('Fetching data from the google sheet...')
	purchases_df = fetch_purchases_history()
	print(purchases_df.head(20))
	print(' ')

	print('Generating portfolio info...')
	portfolio_df = generate_portfolio(purchases_df)
	print('Portfolio:')
	print(portfolio_df)
	print(' ')

	print('Diagram with total purchase parts...')
	print('Press any key to regenerate portfolio info or `Q` to exit...')
	plot_pie(portfolio_df)
	plt.show(block=False)
	print('---------------------------------------------------------------------')
