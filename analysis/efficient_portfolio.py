from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import pandas as pd
import yfinance as yf


class portfolio_manager():
    def __init__(self, stock_list):
        self.stock_list = stock_list
        self.pf = self.df_close_generator()

    def df_close_generator(self):
        df = pd.DataFrame(yf.Ticker(self.stock_list[0]).history(period='max').Close)
        for stock in self.stock_list[1:]:
            df = pd.concat([df, yf.Ticker(stock).history(period='max').Close], axis=1)
        df.columns = self.stock_list
        return df

    def get_max_sharpe_recent_weights(self, exp_span, target_return=2.0):
        mu = expected_returns.ema_historical_return(self.pf, span=exp_span, frequency=252)
        sigma = risk_models.exp_cov(self.pf, span=exp_span, frequency=252)
        ef = EfficientFrontier(mu, sigma)
        try: 
            # ef.efficient_return(target_return)
            ef.max_sharpe()
            clean_weights_maxSR = ef.clean_weights()
            print('the optimal weights for recent max_SR portfolio is \n{}'.format(clean_weights_maxSR))
            ef.portfolio_performance(verbose=True)
            out = []
            for weight in list(clean_weights_maxSR.values()):
                if weight == 0:
                    out.append(0)
                else:
                    out.append(weight)

            return out

        except: 
            return [0] * len(self.stock_list)


if __name__ == '__main__':
    stock_list = ['1434.TW']
    port_manager = portfolio_manager(stock_list=stock_list)
    # print(port_manager.df_close_generator().tail(5))
    weights = port_manager.get_max_sharpe_recent_weights(exp_span=50)
    print(weights)
