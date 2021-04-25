if __name__ == "__main__":
    from database.table import create_table
    from database.temp import insert_temp
    from database.stock import get_stock, update_stock, delete_stock

    create_table()
    stock_buy = [{"stock_id": 2330, "price": 511.2, "volume": 5},
                 {"stock_id": 2317, "price": 87.6, "volume": 8},
                 {"stock_id": 2498, "price": 31, "volume": 8},
                 {"stock_id": 1537, "price": 144.1, "volume": 8},
                 {"stock_id": 2301, "price": 49.6, "volume": 8},
                 {"stock_id": 2308, "price": 246, "volume": 8},
                 {"stock_id": 2454, "price": 720.1, "volume": 7}]

    stock_sell = [{"stock_id": 2308, "price": 246, "volume": 0},
                  {"stock_id": 2454, "price": 720.1, "volume": 0}]

    # df = get_stock()  # 跟屁眼拿資料
    # print(df)
    #delete_stock(2408)
    # insert_stock(stock) #不要賣的塞回去屁眼
    # insert_temp(stock)  # 要買的塞屁眼

    #df = get_stock()
    #print(df)
    # update_stock([{"stock_id": 9910, "price": 195.83, "volume": 0}])
    #insert_temp(stock_buy, "buy")
    #insert_temp(stock_sell, "sell")
