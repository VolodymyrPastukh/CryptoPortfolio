# CryptoPortfolio

##### The simplest implementation of crypto portfolio for analytics of daily operations with crypto.  
>I guess it is the best in the global network!

The app fetches data from the Google Sheet with your crypto operations to analyze data and calculate profit/loss for each ticker.
In the app is used Binance API to get actual prices for most of the pairs.

### Prerequisites 
- python 3+
- pip (to install all additional packages)
- created Google Sheet with operations info in a special format
  1. sheet must be opened for view
  2. sheet must contain the next columns ['Date','Ticker','Amount','Price']
  3. sheet can contain additional columns
- connection to the network

### Install 
- clone the project
- in the directory create ***config.json*** file (for Google Sheets config)
  > example of config.json: `{ "sheet_id":"PUT_SHEET_ID", "sheet_name":"PUT_SHEET_NAME" }`
- run `python3 portfolio.py`
