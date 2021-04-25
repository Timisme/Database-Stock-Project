from database.db import connection
import datetime
import yfinance as yf


def check(stock_id, price):
    stock_id = str(stock_id) + ".TW"
    data = yf.Ticker(stock_id)
    df = data.history(period="5d")

    if str(df.index.values[-1]).split("T")[0] == str(datetime.date.today()):
        low, high = df['Low'].values[-1], df['High'].values[-1]
    else:
        low, high = df['Low'].values[-1], df['High'].values[-1]

    if low < price < high:
        return True
    else:
        return False


def insert_temp(dataset, mode):
    assert mode in ["buy", "sell"]
    cur = connection.cursor()
    for d in dataset:
        if mode == "buy":
            information = [d['stock_id'], d['price'], d['volume']]
            cur.execute('INSERT INTO TempBuy (stock_id, price, volume) VALUES (?, ?, ?)', information)
        else:
            information = [d['stock_id'], d['predictedPrice'], d['price'], d['volume']]
            cur.execute('INSERT INTO TempSell (stock_id, predictedPrice, price, volume) VALUES (?, ?, ?, ?)', information)
        connection.commit()


def delete_temp(stock_id, mode):
    assert mode in ["buy", "sell"]
    cur = connection.cursor()
    if mode == "buy":
        cur.execute('DELETE FROM TempBuy WHERE stock_id = ?', [stock_id])
    else:
        cur.execute('DELETE FROM TempSell WHERE stock_id = ?', [stock_id])
    connection.commit()


def select_and_insert(mode):
    assert mode in ["buy", "sell"]
    from database.stock import insert_stock, update_stock

    cur = connection.cursor()
    if mode == "buy":
        cur.execute('SELECT * FROM TempBuy')
    else:
        cur.execute('SELECT * FROM TempSell')
    rows = cur.fetchall()

    for row in rows:
        if mode == "buy":
            if check(row[0], row[1]):
                insert_stock([{'stock_id': row[0], 'price': row[1], 'volume': row[2]}])
            delete_temp(row[0], "buy")
        else:
            if check(row[0], row[1]):
                # row[1] -> predicted price, row[2]-> price we spent when we brought it
                update_stock([{'stock_id': row[0], 'price': row[2], 'volume': row[3]}])
            delete_temp(row[0], "sell")
