from database.db import connection


def insert_stock(dataset):
    cur = connection.cursor()
    for d in dataset:
        cur.execute('INSERT OR IGNORE INTO Stock (stock_id) VALUES (?)', (d['stock_id'],))

        information = [d['stock_id'], d['price'], d['volume']]
        cur.execute('SELECT Information.stock_id, Information.price, Information.volume '
                    'FROM Stock INNER JOIN Information on (Stock.stock_id = Information.stock_id)'
                    'WHERE Information.stock_id = ? AND Information.price = ? '
                    'ORDER BY Information.stock_id', (d['stock_id'], d['price']))

        row = cur.fetchall()
        if row:
            total_volume = row[0][2] + d['volume']
            update_stock([{"stock_id": d['stock_id'], "price": d['price'], "volume": total_volume}])
            continue

        cur.execute('INSERT INTO Information (stock_id, price, volume) VALUES (?, ?, ?)', information)
        connection.commit()


def delete_stock(stock_id):
    cur = connection.cursor()
    cur.execute('PRAGMA foreign_keys = ON')
    cur.execute('DELETE FROM Stock WHERE stock_id = ?', [stock_id])
    connection.commit()


def get_stock():
    from database.temp import select_and_insert
    select_and_insert("sell")
    select_and_insert("buy")

    cur = connection.cursor()
    cur.execute('SELECT Information.stock_id, Information.price, Information.volume '
                'FROM Stock INNER JOIN Information on (Stock.stock_id = Information.stock_id)'
                'ORDER BY Information.stock_id')

    rows = cur.fetchall()
    info = []
    for row in rows:
        info_dic = {'stock_id': row[0], 'price': row[1], 'volume': row[2]}
        info.append(info_dic)

    return info


def update_stock(dataset):
    cur = connection.cursor()
    for d in dataset:
        if d['volume'] == 0:
            cur.execute('DELETE FROM Information WHERE stock_id = ? AND price = ?',
                        (d['stock_id'], d['price']))
        else:
            cur.execute('UPDATE Information SET volume = ? WHERE stock_id = ? AND price = ?',
                        (d['volume'], d['stock_id'], d['price']))
        connection.commit()
