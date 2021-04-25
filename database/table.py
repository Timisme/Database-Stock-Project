from database.db import connection


def create_table():
    cur = connection.cursor()

    cur.execute('DROP TABLE IF EXISTS TempSell')

    cur.execute('CREATE TABLE IF NOT EXISTS TempBuy ('
                'stock_id INTEGER PRIMARY KEY,'
                'price FLOAT NOT NULL,'
                'volume INTEGER NOT NULL);')

    cur.execute('CREATE TABLE IF NOT EXISTS TempSell ('
                'stock_id INTEGER PRIMARY KEY,'
                'predictedPrice FLOAT NOT NULL,'
                'price FLOAT NOT NULL,'
                'volume INTEGER NOT NULL);')

    cur.execute('CREATE TABLE IF NOT EXISTS Stock ('
                'stock_id INTEGER PRIMARY KEY);')

    cur.execute('CREATE TABLE IF NOT EXISTS Information ('
                'stock_id INTEGER NOT NULL,'
                'price FLOAT NOT NULL,'
                'volume INTEGER NOT NULL,'
                'FOREIGN KEY (stock_id) REFERENCES Stock(stock_id)'
                'ON UPDATE CASCADE ON DELETE CASCADE);')

    connection.commit()
