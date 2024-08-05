from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import time
from transformers import pipeline
import torch
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Set up the Chrome driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

def convert_relative_time_to_dates(description):
    now = datetime.now()

    if 'hour' in description:
        hours_ago = int(description.split()[0])
        date_time = now - timedelta(hours=hours_ago)
    elif 'yesterday' in description:
        date_time = now - timedelta(days=1)
    elif 'days ago' in description:
        days_ago = int(description.split()[0])
        date_time = now - timedelta(days=days_ago)
    else:
        date_time = now  # Default to now if unrecognized format
    date_time = date_time.date().strftime("%Y-%m-%d") 

    return date_time


def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def sentiment_analysis(news_df):
    def helper(title):
        # Load the sentiment-analysis pipeline
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        device = 0 if torch.backends.mps.is_available() else -1

        sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=device)
        analysis = sentiment_pipeline(title)
        if analysis[0]['label'] == 'NEGATIVE':
            return (-1 * analysis[0]['score'])
        else:
            return analysis[0]['score']

    titles = news_df['Title'].tolist()

    res = []

    for title in titles:
        res.append(helper(title))

    news_df['Sentiment Score'] = res
    return news_df

def scrape_yahoo_finance(stock_symbol):
    base_url = f"https://finance.yahoo.com/quote/{stock_symbol}/news"

    driver.get(base_url)
    scroll_to_bottom(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    news_list = []

    news = soup.find_all(class_="stream-item yf-7rcxn")
    
    for new in news:
        title = new.a.get("aria-label")
        date_span = new.find(class_="publishing font-condensed yf-da5pxu")
        time_date = date_span.text.strip().split("•")[-1]
        date = convert_relative_time_to_dates(time_date)
        news_list.append([date, title])
    
    driver.quit()

    df = pd.DataFrame(news_list, columns=['Date', 'Title'])
 
    return sentiment_analysis(df)