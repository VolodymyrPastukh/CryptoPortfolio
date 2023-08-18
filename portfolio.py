#author: V.Androidovych
#version: 1.0.0

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from binance import Client
from datetime import datetime as dt
import warnings
import json
import os
warnings.filterwarnings('ignore')

#----------------------functions
print('Start...')
print('Be sure you have network connection!')
print('Preparing resources, it can take a while...')

binance_client = Client()
def ticker_price(ticker: str, pair='USDT'):
    if ticker == 'USDT' or ticker == 'BUSD': return float(binance_client.get_ticker(symbol=f'{ticker}DAI')['lastPrice'])
    else: return float(binance_client.get_ticker(symbol=f'{ticker}{pair}')['lastPrice'])

def t_amount(df, ticker:str):
    return df[df['Ticker'] == ticker]['Amount'].sum()

def t_average_purchase_price(df, ticker:str):
    return df[df['Ticker'] == ticker]['Price'].mean()

def all_purchases_sum(df):
    return(df['Amount'] * df['Price']).sum()

def t_purchases_sum(df, ticker:str):
    df_ticker = df[df['Ticker'] == ticker]
    return(df_ticker['Amount'] * df_ticker['Price']).sum()

def t_current_price(df, ticker:str, current_price):
    return t_amount(df, ticker) * current_price

def t_percent(df, ticker:str):
    return t_purchases_sum(df, ticker)/all_purchases_sum(df)

def generate_portfolio(data):
    tickers = data['Ticker'].unique()
    params = ['Amount', 'Av. Purchase Price', 'Current Price', 'Total Purchase', 'Current cost', 'Part %', 'Profit/Loss','Profit/Loss %']
    df = pd.DataFrame(np.zeros((len(tickers),len(params))),columns = params, index=tickers)
    for ticker in tickers:
        current_price = ticker_price(ticker)
        df.loc[ticker]['Amount'] = t_amount(data, ticker)
        df.loc[ticker]['Av. Purchase Price'] = t_average_purchase_price(data, ticker)
        df.loc[ticker]['Current Price'] = current_price
        df.loc[ticker]['Total Purchase'] = t_purchases_sum(data, ticker)
        df.loc[ticker]['Current cost'] = df.loc[ticker]['Amount'] * current_price
        df.loc[ticker]['Profit/Loss'] = df.loc[ticker]['Current cost'] - df.loc[ticker]['Total Purchase']
        df.loc[ticker]['Profit/Loss %'] = df.loc[ticker]['Profit/Loss'] / df.loc[ticker]['Total Purchase']
        df.loc[ticker]['Part %'] = t_percent(data, ticker)
    return df

def fetch_purchases_history():
    with open('config.json') as f:
        config = json.load(f)
    
    sheet_id = config['sheet_id']
    sheet_name = config['sheet_name']
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    return pd.read_csv(url)

def add_purchase(df, date, ticker, amount, price):
    new_value = {'Date': date, 'Ticker': ticker, 'Amount': amount, 'Price': price}
    df = df.append(new_value,ignore_index=True)
    return df

def plot_pie(df):
    return plt.pie(df['Total Purchase'].values,autopct='%1.1f%%', labels=df['Total Purchase'].keys())

def clean():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

#----------------------main
print('Press any key to generate portfolio info or `Q` to exit...')

while input().lower() != 'q':
	clean()
	print('---------------------------------------------------------------------')
	print('Fetching data from the google sheet...')
	purchases_df = fetch_purchases_history()
	print('Last 20 crypto operations:')
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
