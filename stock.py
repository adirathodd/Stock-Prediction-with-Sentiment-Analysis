import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from yahoo import scrape_yahoo_finance

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None
        self.sentiment = None

    def create(self, window):
        self.set_data()
        self.create_mva(window)
        self.create_rsi(window) 
    
    def set_data(self):
        try:
            self.data = yf.download(self.ticker, start='2024-06-27')
            self.data = self.data.loc[:, ['Close', 'Volume']]
        except Exception as e:
            return str(e)
    
    def get_data(self):  
        return self.data
    
    def create_mva(self, window):
        self.data.loc[:, 'Moving Average'] = self.data.loc[:, 'Close'].rolling(window=window).mean()
        self.data.dropna(inplace=True)
    
    def create_rsi(self, window):
        delta = self.data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.data.loc[:, "RSI"] = rsi
        self.data.dropna(inplace=True)
        self.data.reset_index(inplace=True)


    def sentiment_analysis(self):
        news_df = scrape_yahoo_finance(self.ticker)
        average_compound_df = news_df.groupby('Date', as_index=False).agg({'Compound': 'mean'})
        average_compound_df.rename(columns={'Compound': 'Average_Compound'}, inplace=True)
        self.sentiment = average_compound_df



    def print(self):
        print(self.data)
        print(self.sentiment)

        result = pd.concat([self.data, self.sentiment], axis=1, join="inner")

        print(result)

