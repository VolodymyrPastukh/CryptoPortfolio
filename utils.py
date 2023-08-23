import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime as dt
import warnings
import json
import os
import re
from binance import Client
warnings.filterwarnings('ignore')

### Constants
SPOT_HISTORY_FILE = 'spot_history_v1.0.csv'
FULL_SPOT_HISTORY_FILE = 'full_spot_history_v1.0.csv'

USDT = 'USDT'
BUSD = 'BUSD'
DAI = 'DAI'
UAH = 'UAH'
LUNA = 'LUNA'

TIME_PATTERN_UNIX = '%Y-%m-%d %H:%M:%S'
TIME_PATTERN_SIMPLE = '%d/%m/%Y'

# Binance history report constants
B_DATE = 'Date(UTC)'
B_EXECUTED = 'Executed'
B_AMOUNT = 'Amount'
B_SIDE = 'Side'
B_SIDE_BUY = 'BUY'
B_SIDE_SELL = 'SELL'

### Binance functions
binance_client = Client()
def ticker_price(ticker: str, pair=USDT):
    if ticker == USDT or ticker == BUSD: return float(binance_client.get_ticker(symbol=f'{ticker}{DAI}')['lastPrice'])
    else: return float(binance_client.get_ticker(symbol=f'{ticker}{pair}')['lastPrice'])

def ticker_price_in_time(ticker: str, date: int):
    MINUTE = 60000
    MONTH = 2629743000
    result = 0
    symbol = f'{ticker}{USDT}'
    if ticker == UAH:
        symbol = f'{USDT}{ticker}'
    elif ticker == USDT:
        symbol=f'{ticker}{DAI}'

    agg = []
    endTimeCounter = MINUTE
    while (len(agg) == 0):
        if ticker == LUNA: endTimeCounter = endTimeCounter + MONTH
        else: endTimeCounter = endTimeCounter + MINUTE
        agg = binance_client.get_aggregate_trades(symbol=symbol, startTime=date, endTime=date + endTimeCounter)

    for i in agg:
        result = result + float(i['p'])
    return result / len(agg)

def binance_amount_format(amount:str):
    ticker = binance_amount_ticker_extract(amount)
    return float(amount.replace(ticker, '').replace(',',''))

def binance_amount_ticker_extract(string: str):
    regex = r'[A-Z]+'
    match = re.search(regex, str(string))
    if match:
        sub_string = match.group()
        return sub_string

def binance_amount_in_usdt(amount: str, date: str):
    ticker = binance_amount_ticker_extract(amount)
    pure_amount = binance_amount_format(amount)
    if ticker == USDT:
        return pure_amount
    price = ticker_price_in_time(ticker, date_timestamp(date))
    if ticker == UAH:
        return pure_amount / price
    else:
        return pure_amount * price


def parse_binance_parse(binance):
    new_df = pd.DataFrame(columns = ['Date', 'Ticker', 'Amount', 'Price'])
    binance_size = len(binance)
    for i in range(0, binance_size):
        percent_of_done = "{:.2f}".format(round((i / binance_size) * 100, 2))
        item = binance.loc[i]
        print(f'[{i}][{percent_of_done}%]:\t{item[B_DATE]}|{item[B_EXECUTED]}|{item[B_AMOUNT]}')
        date = item[B_DATE]
        timestamp = date_timestamp(date=date)
        date_formatted = timestamp_date(timestamp, TIME_PATTERN_SIMPLE)
        side = item[B_SIDE]

        # -->
        ticker = binance_amount_ticker_extract(item[B_EXECUTED])
        amount = binance_amount_format(item[B_EXECUTED])
        price = ticker_price_in_time(ticker, date_timestamp(date))
        if side == B_SIDE_SELL: amount = amount * -1
        new_value = {'Date': date_formatted, 'Ticker': ticker, 'Amount': amount, 'Price': price}
        new_df = new_df.append(new_value,ignore_index=True)

        # <--
        ticker = binance_amount_ticker_extract(item[B_AMOUNT])
        amount = binance_amount_format(item[B_AMOUNT])
        price = ticker_price_in_time(ticker, date_timestamp(date))
        if side == B_SIDE_BUY: amount = amount * -1
        new_value = {'Date': date_formatted, 'Ticker': ticker, 'Amount': amount, 'Price': price}
        new_df = new_df.append(new_value,ignore_index=True)
    return new_df

### Date/Timestamp extensions
def date_timestamp(date: str, pattern = TIME_PATTERN_UNIX):
    converter = dt.strptime(date, pattern)
    timestamp = converter.timestamp() * 1000
    return int(timestamp)

def timestamp_date(timestamp, pattern = TIME_PATTERN_UNIX):
    date = dt.fromtimestamp(timestamp / 1000)
    date_formatted = dt.strftime(date, pattern)
    return date_formatted

### Portfolio functions
def t_amount(df, ticker:str):
    return df[df['Ticker'] == ticker]['Amount'].sum()

def t_average_purchase_price(df, ticker:str):
    return df[df['Ticker'] == ticker]['Price'].mean() / df[df['Ticker'] == ticker]['Amount']].sum()

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


def add_purchase(df, date, ticker, amount, price):
    new_value = {'Date': date, 'Ticker': ticker, 'Amount': amount, 'Price': price}
    df = df.append(new_value,ignore_index=True)
    return df

### Plotting extensions
def plot_pie(df):
    return plt.pie(df['Total Purchase'].values,autopct='%1.1f%%', labels=df['Total Purchase'].keys())

### OS functions
def clean_screen():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')
