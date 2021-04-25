import talib
from talib import abstract
from pandas_datareader import data as pdr
import numpy as np


def sell(stock_list):
    signals = np.array(check(stock_list))
    stock_list = np.array(stock_list)
    sell_stock = (signals == -1)
    return stock_list[sell_stock]


def buy(stock_list):
    signals = np.array(check(stock_list))
    stock_list = np.array(stock_list)
    buy_stock = (signals == 1)
    return stock_list[buy_stock]


def check(stock_list):
    signals = []

    for idx, stock in enumerate(stock_list):
        print("Technical analysis checking for {} ...".format(stock))
        try:
            analyser = Analyser(stock)
            ma_sig = analyser.MA_signal()
            rsi_sig = analyser.RSI_signal()
            kd_sig = analyser.KD_signal()
            macd_sig = analyser.MACD_signal()

            signal = 0
            if rsi_sig != 0:
                signal = rsi_sig
            elif ma_sig != 0:
                signal = ma_sig
            elif (kd_sig == 1 and macd_sig == -1) or (kd_sig == -1 and macd_sig == 1):
                signal = 0
            elif kd_sig != 0:
                signal = kd_sig
            elif macd_sig != 0:
                signal = macd_sig
            signals.append(signal)

            # print("rsi:", rsi_sig)
            # print("ma:", ma_sig)
            # print("macd:", macd_sig)
            # print("kd:", kd_sig)
            # print("")
        except:
            print("cannot find information of {}".format(stock))
            signals.append(0)
            continue
    return signals


class Analyser:
    def __init__(self, stock_id):
        self.stock_id = stock_id
        self.stock_data = pdr.get_data_yahoo(self.stock_id)

    def MA_signal(self, MA_long=20, MA_short=5):

        MA_df = self.stock_data
        MA_df['MA_' + str(MA_long)] = talib.SMA(MA_df.Close, timeperiod=MA_long)
        MA_df['MA_' + str(MA_short)] = talib.SMA(MA_df.Close, timeperiod=MA_short)

        if (MA_df.iloc[-1, -1] > MA_df.iloc[-1, -2]) & (MA_df.iloc[-2, -1] < MA_df.iloc[-2, -2]):
            print('{} MA {} 超過 MA {}，黃金交叉'.format(MA_df.index[-1], MA_short, MA_long))
            return 1
        elif (MA_df.iloc[-1, -1] < MA_df.iloc[-1, -2]) & (MA_df.iloc[-2, -1] > MA_df.iloc[-2, -2]):
            print('{} MA {} 低於 MA {}，死亡交叉'.format(MA_df.index[-1], MA_short, MA_long))
            return -1
        return 0

    def RSI_signal(self, rolling=3, low_thres=40, high_thres=70):

        # RSI指標呈現「一段時間內股價買盤與賣盤力量強弱比例」，評估力量是相對平衡還是懸殊。
        # RSI (相對強弱指標) = n日漲幅平均值÷(n日漲幅平均值+ n日跌幅平均值) × 100
        # n日漲幅平均值 = n日內上漲日總上漲幅度加總 ÷ n
        # n日跌幅平均值 = n日內下跌日總下跌幅度加總 ÷ n

        df = self.stock_data
        df['RSI_14'] = talib.RSI(df.Close)
        df['RSI_14_MA_' + str(rolling)] = df['RSI_14'].rolling(rolling).mean()

        #if (df.iloc[-2, 2] < high_thres) & (df.iloc[-1, 2] >= high_thres):
        #    print('{} 過去{}天平均RSI大於{}，買方力道強勢'.format(df.index[-1], rolling, high_thres))
        #    return -1
        #elif (df.iloc[-2, 2] > low_thres) & (df.iloc[-1, 2] <= low_thres):
        #    print('{} 過去{}天平均RSI小於{}，賣方力道強勢'.format(df.index[-1], rolling, low_thres))
        #    return 1

        if df.iloc[-1, -2] >= high_thres:
            print('{} 過去{}天平均RSI大於{}，買方力道強勢'.format(df.iloc[-1, -1], rolling, high_thres))
            return -1
        elif df.iloc[-1, -2] <= low_thres:
            print('{} 過去{}天平均RSI小於{}，賣方力道強勢'.format(df.iloc[-1, -1], rolling, low_thres))
            return 1
        return 0

    def KD_signal(self, fastk=9):

        # KD指標，呈現過去一段時間股價強弱趨勢
        # 用K和D判斷目前價格相對過去一段時間的高低變化
        # KD指標呈現「最新股價的相對高低位置」，估股價目前處於相對高點或低點。
        # RSV= (今日收盤價 – 最近n天的最低價) ÷ (最近n天的最高價 – 最近n天最低價) × 100
        # 今日K值(快線)= 昨日K值 × (2/3 ) +今日RSV × ( 1/3)
        # 今日D值(慢線)= 昨日D值 × (2/3) +今日K值 × ( 1/3)
        # ※RSV中的n天，常見天數有以9天、14天等來比較，依標的屬性來調整。
        # fastk : RSV以 fastk 天為期

        df = self.stock_data
        df.columns = [col.lower() for col in df.columns]
        df_KD = abstract.STOCH(df, fastk_period=fastk)

        if (df_KD.iloc[-1, 0] > df_KD.iloc[-1, 1]) & (df_KD.iloc[-2, 0] < df_KD.iloc[-2, 1])\
                & (df_KD.iloc[-2, 0] < 20) & (df_KD.iloc[-2, 1] < 20):
            print('k值轉為大於d值，黃金交叉')
            return 1

        elif (df_KD.iloc[-1, 0] < df_KD.iloc[-1, 1]) & (df_KD.iloc[-2, 0] > df_KD.iloc[-2, 1])\
                & (df_KD.iloc[-2, 0] > 80) & (df_KD.iloc[-2, 1] > 80):
            print('k值轉為小於d值，死亡交叉')
            return -1

        # if (df_KD.iloc[-2, 0] < 80) & (df_KD.iloc[-1, 0] >= 80):
        #     return 1
        # elif (df_KD.iloc[-2, 0] > 30) & (df_KD.iloc[-1, 0] <= 30):
        #     return -1
        return 0

    def MACD_signal(self):
        df = self.stock_data
        _, _, df['MACDhist'] = talib.MACD(df.close)

        if (df['MACDhist'].iloc[-2] < 0) & (df['MACDhist'].iloc[-1] >= 0):
            print('{} MACD diff超過黃金交叉'.format(df['MACDhist'].iloc[-1]))
            return 1
        elif (df['MACDhist'].iloc[-2] > 0) & (df['MACDhist'].iloc[-1] <= 0):
            print('{} MACD diff超過死亡交叉'.format(df['MACDhist'].iloc[-1]))
            return -1
        return 0


if __name__ == "__main__":
    check(["2603.TW"])
