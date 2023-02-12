import logging

from crypto_balancer.order import Order
from crypto_balancer.ccxt_exchange import CCXTExchange
from crypto_balancer.simple_balancer import SimpleBalancer
logger = logging.getLogger(__name__)


class TradeExecutor():

    def __init__(self, exchange: CCXTExchange, balancer: SimpleBalancer, do_smart_routing: bool):
        self.portfolio = portfolio
        self.exchange = exchange
        self.balancer = balancer
        self.
    def run(self, force=False, trade=False, max_orders=5, mode='mid'):

        balances = self.portfolio.balances

        res = {'orders': [],
               'success': [],
               'errors': [],
               'balances': balances,
               'total_fee': 0.0,
               'initial_portfolio': self.portfolio,
               'proposed_portfolio': None, }

        if self.portfolio.needs_balancing or force:
            orders = self.balancer.balance(self.portfolio,
                                           self.exchange,
                                           max_orders,
                                           mode)

            if orders['proposed_portfolio']:
                res['proposed_portfolio'] = orders['proposed_portfolio']
                res['total_fee'] = orders['total_fee']
                res['orders'] = orders['orders']

                if trade:
                    for order in orders['orders']:
                        try:
                            r = self.exchange.execute_order(order)
                            res['success'].append(Order(r['symbol'],
                                                        r['side'].upper(),
                                                        r['amount'],
                                                        r['price']))
                        except Exception as e:
                            res['errors'].append(order)
                            logger.error("Could not place order: {} {}"
                                         .format(order, e))

        return res
