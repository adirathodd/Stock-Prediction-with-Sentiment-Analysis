import pandas as pd
import numpy as np
import yfinance as yf
from yahoo import scrape_yahoo_finance
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Input # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
import os

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.data = None
        self.sentiment = None
        self.prediction = None

    def create(self, window):
        self.set_data()
        self.create_mva(window)
        self.create_rsi(window)
        self.data.dropna(inplace=True)
        self.data.reset_index(inplace=True)
        self.data = self.data.drop(columns=["index"])
    
    def set_data(self):
        try:
            ticker = yf.Ticker(self.ticker)

            end_date = datetime.now()
            start_date = end_date - timedelta(days=30) #30 days of data

            # Get historical market data for the specified date range
            df = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            df.index = df.index.date
            df.reset_index(inplace=True)
            df.rename(columns={"index": "Date"}, inplace=True)
            self.data = df.loc[:, ['Date', 'Close', 'Volume']] #Main features
        except Exception as e:
            print(str(e))
    
    def get_data(self):  
        return self.data
    
    def create_mva(self, window):
        try:
            self.data.loc[:, 'Moving Average'] = self.data.loc[:, 'Close'].rolling(window=window).mean()
        except Exception as e:
            print(str(e))
    
    def create_rsi(self, window):
        try:
            delta = self.data['Close'].diff(1)
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            avg_gain = gain.rolling(window=window).mean()
            avg_loss = loss.rolling(window=window).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            self.data.loc[:, "RSI"] = rsi
        except Exception as e:
            print(str(e))


    def sentiment_analysis(self):
        try:
            news_df = scrape_yahoo_finance(self.ticker)
            average_compound_df = news_df.groupby('Date', as_index=False).agg({'Sentiment Score': 'mean'})
            self.sentiment = average_compound_df
            self.sentiment['Date'] = pd.to_datetime(self.sentiment['Date'])
            self.data['Date'] = pd.to_datetime(self.data['Date'])
            self.data = pd.merge(self.sentiment, self.data, on='Date', how='inner')
        except Exception as e:
            print(str(e))

    def predict(self):
        # Feature selection
        df_features = self.data[['Sentiment Score', 'Volume', 'Moving Average', 'RSI', 'Close']]

        # Normalize the data
        scaler = MinMaxScaler()
        df_scaled = scaler.fit_transform(df_features)

        # Create sequences for each data point - Previous (seq_length) data points will be an input to a given day's closing price
        def create_sequences(data, seq_length):
            sequences = []
            for i in range(len(data) - seq_length):
                sequence = data[i:i + seq_length]
                target = data[i + seq_length, -1]
                sequences.append((sequence, target))
            return sequences

        seq_length = 3
        sequences = create_sequences(df_scaled, seq_length)

        # Split sequences into features and targets
        X, y = zip(*sequences)
        X = np.array(X)
        y = np.array(y)

        model = Sequential([
            Input(shape=(seq_length, X.shape[-1])),
            LSTM(50, return_sequences=True),
            LSTM(50),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

        model.fit(X, y, epochs=50, batch_size=1, verbose=0)

        # Predict the next day's price
        last_sequence = df_scaled[-seq_length:]
        last_sequence = np.expand_dims(last_sequence, axis=0)
        predicted_price = model.predict(last_sequence, verbose=0)
        predicted_price = scaler.inverse_transform(np.concatenate((np.zeros((1, X.shape[-1] - 1)), predicted_price), axis=1))[:, -1]
        self.prediction = predicted_price[0]      
        
    def print(self):
        # Get the width of the terminal
        terminal_size = os.get_terminal_size().columns

        # Create the dashed line
        dashed_line = '-' * terminal_size
        print(dashed_line)
        print(self.data)
        print(dashed_line)
        print("Predicted next day's price:", self.prediction)
        print(dashed_line)