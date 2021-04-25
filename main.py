import numpy as np
from analysis.fundamental_analysis import stock_list
from analysis.technical_analysis import sell, buy
from analysis.stock_weight import get_weights
from database.table import create_table
from database.temp import insert_temp
from database.stock import get_stock, delete_stock
from model.run import stock_predict
from tools.utils import get_historical_data

if __name__ == "__main__":
    """
    stock format:
    [{"stock_id": 2330, "price": 522, "volume": 8},
     {"stock_id": 2454, "price": 740, "volume": 7}]
    """
    create_table()

    # -------------------------
    # - Check our stored data -
    # -------------------------
    print("=" * 50)
    print("Receive current owned stocks")
    print("=" * 50)
    stocks = get_stock()  # 跟屁眼拿資料

    all_stock, all_price, all_volume = [], [], []
    for dict_ in stocks:
        all_stock.append(str(dict_['stock_id']) + ".TW")
        all_price.append(float(dict_['price']))
        all_volume.append(int(dict_['volume']))

    all_stock, all_price, all_volume = np.array(all_stock), np.array(all_price), np.array(all_volume)
    # print('all_stock : ', all_stock)
    # print('all_price : ', all_price)
    # print('all_volume : ', all_volume)

    unique_stock = sorted(list(set(all_stock)))  # 所有庫存的股票（不會重複）
    stock_detail = {}  # 以dictionary的形式存放股票以利後面讀取股票資訊方便

    for stock in unique_stock:
        indexes = (all_stock == stock)
        history_price = all_price[indexes]
        history_volume = all_volume[indexes]
        close = round(get_historical_data(stock).Close[-1], 2)
        asset = np.sum(history_price * history_volume) / np.sum(history_volume)
        fell_percentage = ((close - asset) / asset) * 100  # 跌幅

        if fell_percentage < 0 and np.abs(fell_percentage) > 5:  # 跌幅超過10%就賣出
            sell_price1 = round(stock_predict(stock), 2)
            sell_price2 = round(stock_predict(stock), 2)
            sell_price = (sell_price1 * 1.05 + sell_price2) / 2
            for price in history_price:
                insert_temp([{"stock_id": int(stock.split(".")[0]), "predictedPrice": sell_price, "price": price, "volume": 0}], "sell")
            #stock_id = int(stock.split(".")[0])
            #delete_stock(stock_id)
            print("{} exceeds our selling threshold, sell all of it with ${}".format(stock, close))
        else:
            stock_detail[stock] = [history_price, history_volume]
    print('Current owned stocks:\n{}'.format(stock_detail))

    # -------------------------
    #  Check if we can sell it
    # -------------------------
    print("=" * 50)
    print("Check if we can sell it")
    print("=" * 50)
    must_sell = sell(unique_stock)
    print('Stocks to sell:\n{}'.format(must_sell))

    print("=" * 50)
    print("Predict the selling price")
    print("=" * 50)
    # --------------------------------------------------------------
    # - Insert good stocks into model to predict the selling price -
    # --------------------------------------------------------------
    for stock in must_sell:
        sell_price1 = round(stock_predict(stock), 2)
        sell_price2 = round(stock_predict(stock), 2)
        sell_price = (sell_price1 * 1.05 + sell_price2) / 2

        # ------------------------------------------------
        # - Update number of remained stocks in database -
        # ------------------------------------------------
        able_to_sell = stock_detail[stock][0] < np.array(sell_price)  # 大於當時購買價格的股票才會賣出
        if able_to_sell.any():
            history_price = stock_detail[stock][0][able_to_sell]
            history_volume = stock_detail[stock][1][able_to_sell]
            for price in history_price:
                insert_temp([{"stock_id": int(stock.split(".")[0]), "predictedPrice": sell_price, "price": price, "volume": 0}], "sell")
            print("Sell {} unit(s) of {} with ${}".format(int(np.sum(history_volume)), stock, sell_price))
        else:
            print("Previously buying price of all the unit(s) of {} are bigger than predicted price ${}"
                  .format(stock, sell_price))
            print("i.e, Don't sell it")
    # -------------------------------------------------
    # - Check selected stocks are worth buying or not -
    # -------------------------------------------------
    print("=" * 50)
    print("Check selected stocks are worth buying or not")
    print("=" * 50)
    must_buy = buy(stock_list)
    print('Stocks to buy:\n{}'.format(must_buy))

    # -----------------------------------------------------------------------
    # - Predict the buying price from model and insert stocks into database -
    # -----------------------------------------------------------------------
    print("=" * 50)
    print("Predict the buying price")
    print("=" * 50)
    buy_dict = get_weights(must_buy.tolist(), stocks)
    print("-" * 50)
    for stock, price in buy_dict.items():
        print("Recommended buy budget for {} : {:.2f}".format(stock, price))
        if price > 0:
            # close = round(get_historical_data(stock_id).Close[-1], 2)  # 這行不需要
            predicted_price1 = float(round(stock_predict(stock), 2))
            predicted_price2 = float(round(stock_predict(stock), 2))
            predicted_price = (predicted_price1 * 1.05 + predicted_price2) / 2
            volume = int(round(price / (predicted_price * 1000)))
            if volume < 1:
                print("Oops!, not enough money to buy {}".format(stock))
                continue
            insert_temp([{"stock_id": int(stock.split(".")[0]), "price": predicted_price, "volume": volume}], "buy")
            print("Buy {} unit(s) of {} with ${}".format(volume, stock, predicted_price))
        else:
            print("i.e., Don't buy it")

    print("-" * 50)
    print("Stock prediction has done for today, good luck for tomorrow:)")
