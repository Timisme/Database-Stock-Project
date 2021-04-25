import talib
from talib import abstract
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler


# from sklearn.preprocessing import MinMaxScaler
# class feature_add():
# 	def __init__(self, )


def feature_add(df):
    ma_period = 10
    # rsi_period
    fastk = 9
    macd_fast = 6
    macd_slow = 12
    macd_period = 9

    df['MA' + str(ma_period)] = talib.SMA(df['close'], timeperiod=ma_period)
    df['RSI_14'] = talib.RSI(df['close'])
    _, _, df['MACDhist'] = talib.MACD(df['close'])

    vix_close = yf.Ticker('^VIX').history(period= 'max')['Close']
    tw_weighted = yf.Ticker('^TWII').history(period= 'max')['Close']
    sp500 = yf.Ticker('^GSPC').history(period= 'max').rename(columns={'Close': 'sp500'})['sp500']
    dowj = yf.Ticker('^DJI').history(period= 'max').rename(columns={'Close': 'Dowj'})['Dowj']
    # idx50 = yf.Tikcer('0050.TW').rename(columns={'Close': '0050'})['0050']
    # idx56 = yf.Tikcer('0056.TW').rename(columns={'Close': '0056'})['0056']
    df = pd.concat([df, abstract.STOCH(df, fastk_period=fastk), vix_close, tw_weighted, sp500, dowj],
                   axis=1).dropna()
    try:
        df.drop(columns=['adj close'], inplace=True)
    except:
        pass

    normalizer = MinMaxScaler()
    scaled_features = normalizer.fit_transform(df.values)
    df_scaled = pd.DataFrame(scaled_features, index=df.index)
    data = [list(row.values) for idx, row in df_scaled.iterrows()]

    max_price = max(df['close'])
    min_price = min(df['close'])

    return data, [max_price, min_price]
