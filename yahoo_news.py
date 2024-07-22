import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

from datetime import datetime, timedelta


def convert_relative_time_to_dates(description):
    now = datetime.now()

    if 'hour' in description:
        hours_ago = int(description.split()[0])
        date_time = now - timedelta(hours=hours_ago)
    elif 'yesterday' in description:
        date_time = now - timedelta(days=1)
    else:
        date_time = now  # Default to now if unrecognized format
    date_time = date_time.date().strftime("%m-%d-%Y") 

    return date_time


def scrape_yahoo_finance(stock_symbol, from_date, to_date):
    base_url = f"https://finance.yahoo.com/quote/{stock_symbol}/news?p={stock_symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    news_list = []

    def parse_articles(soup):
        news = soup.find_all(class_="stream-item yf-7rcxn")
        for new in news:
            title = new.a.get("aria-label")
            date_span = new.find(class_="publishing font-condensed yf-da5pxu")
            time_date = date_span.text.strip().split("•")[-1]
            date = convert_relative_time_to_dates(time_date)
            news_list.append([date, title])

        return True

    while True:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        if not parse_articles(soup):
            break

    return pd.DataFrame(news_list)

# Define the stock symbol and date range
stock_symbol = 'TSLA'
to_date = datetime.now().strftime('%Y-%m-%d')
from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

# Scrape the news headlines
news_df = scrape_yahoo_finance(stock_symbol, from_date, to_date)

# Print the DataFrame
print(news_df)
