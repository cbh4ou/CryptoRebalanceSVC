from itertools import product

from crypto_balancer.order import Order
from crypto_balancer.ccxt_exchange import CCXTExchange
targets = {
    'BTC' : 50,
    'USDT' : 40,
    'ETH' : 10
}

class Rebalancer():

    def rebalance(self, exchange: CCXTExchange, targets: dict, quote_currency, mode='mid'):
        portfolio = exchange.get_portfolio_total(quote_currency, mode)
        total_balance = portfolio["total"]
        codes = portfolio["codes"]
        weights = {key: value / total_balance for key, value in codes.items()}
        amounts_to_sell = {}
        print(weights)
        print({"new_target" : weights[key] - value for key, value in targets.keys() if key in weights})
            
    def build_orders():
        pass
            