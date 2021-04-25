import sqlite3
import yfinance as yf
import numpy as np
import math
from datetime import datetime

import sys 

sys.path.append("database")

connection = sqlite3.connect('database/history.db')


def create_table():
	cur = connection.cursor()

	cur.execute('CREATE TABLE IF NOT EXISTS Stock ('
				'stock_id INTEGER PRIMARY KEY,'
				'date STRING NOT NULL);')

	cur.execute('CREATE TABLE IF NOT EXISTS History ('
				'stock_id INTEGER NOT NULL,'
				'date STRING NOT NULL,'
				'price FLOAT NOT NULL,'
				'FOREIGN KEY (stock_id) REFERENCES Stock(stock_id)'
				'ON UPDATE CASCADE ON DELETE CASCADE);')

	connection.commit()


def check_up_to_date(stock_id, today):
	if type(stock_id) != int:
		stock_id = int(stock_id.split('.')[0])

	cur = connection.cursor()
	cur.execute('SELECT Stock.date FROM Stock WHERE Stock.stock_id = ? ', (stock_id,))
	try:
		date = str(cur.fetchall()[0][0])
	except:
		return False
	if today == date:
		return True
	else:
		return False


def delete_stock(stock_id):
	if type(stock_id) != int:
		stock_id = int(stock_id.split('.')[0])

	cur = connection.cursor()
	cur.execute('PRAGMA foreign_keys = ON')
	cur.execute('DELETE FROM Stock WHERE stock_id = ?', [stock_id])
	connection.commit()


def insert(stock_id, today):
<<<<<<< HEAD
	delete_stock(stock_id)  # 更新前先清除舊資料

	cur = connection.cursor()
	print("Updating history close price of {}...".format(stock_id))
	try:
		if type(stock_id) != str:
			stock_id = stock_id + ".TW"
		hist = yf.Ticker(stock_id).history(period="3y").reset_index()
	except:
		print("cannot get information of {}".format(stock_id))
		return False

	if type(stock_id) != int:
		stock_id = int(stock_id.split('.')[0])

	cur.execute('INSERT OR IGNORE INTO Stock (stock_id, date) VALUES (?, ?)', (stock_id, today))
	for idx in hist.index:
		information = [stock_id, str(hist['Date'][idx]).split(' ')[0].replace('-', ''),
					   round(float(hist['Close'][idx]), 2)]
		if not information[2]:
			print("{}'s {} price is {}".format(information[0], information[1], information[2]))
			continue
		cur.execute('INSERT INTO History (stock_id, date, price) VALUES (?, ?, ?)', information)
		connection.commit()
	return True
=======
    delete_stock(stock_id)  # 更新前先清除舊資料

    cur = connection.cursor()
    print("Updating history close price of {}...".format(stock_id))
    try:
        if type(stock_id) != str:
            stock_id = stock_id + ".TW"
        hist = yf.Ticker(stock_id).history(period="3y").reset_index()
    except:
        print("cannot get information of {}".format(stock_id))
        return False

    if type(stock_id) != int:
        stock_id = int(stock_id.split('.')[0])

    cur.execute('INSERT OR IGNORE INTO Stock (stock_id, date) VALUES (?, ?)', (stock_id, today))
    for idx in hist.index:
        information = [stock_id, str(hist['Date'][idx]).split(' ')[0].replace('-', ''),
                       round(float(hist['Close'][idx]), 2)]
        if math.isnan(information[2]):
            print("{}'s {} price is {}".format(information[0], information[1], information[2]))
            continue
        cur.execute('INSERT INTO History (stock_id, date, price) VALUES (?, ?, ?)', information)
        connection.commit()
    return True
>>>>>>> 14806014a86b3a2bccae0bde75f912ff5bc95fe3


def correlation(parent, children):
	"""
	:param parent: 我們針對的公司
	:param children: 其他所有公司
	:return:
	"""
	cur = connection.cursor()
	cur.execute('SELECT History.price FROM History WHERE History.stock_id = ? ', (parent,))
	parent_price = cur.fetchall()
	assert parent_price, print("cannot get {} from database".format(parent))
	parent_price = np.array([i[0] for i in parent_price])
	cur.execute('SELECT History.price FROM History WHERE History.stock_id = ? ', (children,))
	children_price = cur.fetchall()
	assert children_price, print("cannot get {} from database".format(children))
	children_price = np.array([i[0] for i in children_price])

	cov = np.cov(parent_price, children_price)
	p_std, c_std = np.std(parent_price), np.std(children_price)
	corr = cov[0][1] / (p_std * c_std)
	return corr


def find_correlation(stock_id, rank):
<<<<<<< HEAD
	"""
	:param stock_id: (ex: 2330.TW)
	:param rank: 要找幾個正負最相關
	:return:
	"""
	from analysis.fundamental_analysis import stock_list
	today = str(datetime.today()).split(' ')[0].replace('-', '')
	create_table()

	if not check_up_to_date(stock_id, today):
		success = insert(stock_id, today)
		assert success, print("cannot find {} in yfinance".format(stock_id))

	corr_list = []
	stock_id = int(stock_id.split('.')[0])
	for stock in stock_list:
		if not check_up_to_date(stock, today):
			success = insert(stock, today)
			if not success:
				continue

		stock = int(stock.split('.')[0])
		if stock != stock_id:
			try:
				corr = correlation(stock_id, stock)
				corr_list.append({"stock_id": str(stock) + ".TW", "corr": round(corr, 3)})
			except:
				continue

	corr_list = sorted(corr_list, key=lambda x: x['corr'])
	return sorted(corr_list[-rank:], key=lambda x: x['corr'], reverse=True), corr_list[:rank]


if __name__ == "__main__":
	# create_table()
	# crawl_history()
	# correlation(2330, 3071)
	positive, negative = find_correlation("2109.TW", 5)
	print(positive)
	print(negative)
	#insert(6175, str(datetime.today()).split(' ')[0].replace('-', ''))

	# 2109
=======
    """
    :param stock_id: (ex: 2330.TW)
    :param rank: 要找幾個正負最相關
    :return:
    """
    from fundamental_analysis import stock_list
    today = str(datetime.today()).split(' ')[0].replace('-', '')
    create_table()

    if check_up_to_date(stock_id, today):
        success = insert(stock_id, today)
        assert success, print("cannot find {} in yfinance".format(stock_id))

    corr_list = []
    stock_id = int(stock_id.split('.')[0])
    for stock in stock_list:
        if check_up_to_date(stock, today):
            success = insert(stock, today)
            if not success:
                continue

        stock = int(stock.split('.')[0])
        if stock != stock_id:
            try:
                corr = correlation(stock_id, stock)
                corr_list.append({"stock_id": str(stock) + ".TW", "corr": round(corr, 3)})
            except:
                continue

    corr_list = sorted(corr_list, key=lambda x: x['corr'])
    return sorted(corr_list[-rank:], key=lambda x: x['corr'], reverse=True), corr_list[:rank]


if __name__ == "__main__":
    # create_table()
    # crawl_history()
    # correlation(2330, 3071)
    positive, negative = find_correlation("2317.TW", 5)
    print(positive)
    print(negative)
    #insert(6175, str(datetime.today()).split(' ')[0].replace('-', ''))
>>>>>>> 14806014a86b3a2bccae0bde75f912ff5bc95fe3
