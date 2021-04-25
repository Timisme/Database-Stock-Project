from analysis.efficient_portfolio import portfolio_manager


# stored_data : [{id, price, vol}, {id...}]

def get_weights(buy_list, stored_data, exp_span=60):
    output_dict = {}

    stored_list = [str(stock_dict['stock_id']) + ".TW" for stock_dict in stored_data]
    stock_list = buy_list + stored_list

    if stored_list:
        total_spent = sum([stock_dict['price'] * 1000 * stock_dict['volume'] for stock_dict in stored_data])
        assert total_spent <= 100000000, 'total_spent exceeds our budget'

    else:
        total_spent = 1000000

    manager = portfolio_manager(stock_list=stock_list)
    weights_list = manager.get_max_sharpe_recent_weights(exp_span=exp_span)

    owned_ratio = sum(weights_list[len(buy_list):])
    print('recommended portfolio weight sum for our stocks in db: {}'.format(owned_ratio))
    print('estimated total spent : {:.3f}'.format(total_spent))
    if owned_ratio > 0.2:  # 若計算持有投組weight超過2成，照計算買賣
        buy_spent = total_spent * (1 - owned_ratio) / owned_ratio

    else:
        buy_spent = total_spent * (1 - 0.2) / 0.2  # 若計算持有投組weight低於兩成，設持有weight最低為兩成

    for buy_stock, buy_weight in zip(buy_list, weights_list[:len(buy_list)]):
        output_dict[buy_stock] = buy_spent * buy_weight

    return output_dict


if __name__ == '__main__':
    print('ok')
