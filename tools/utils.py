import yfinance as yf
import pandas as pd


def get_historical_data(ticker):
    d = yf.Ticker(ticker)
    df = d.history(period="max")
    df.columns = df.columns.str.lower()
    df.columns = pd.Series(df.columns).str.capitalize().values
    return df.dropna()
