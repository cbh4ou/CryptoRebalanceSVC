import argparse
import configparser
import logging
import sys

from crypto_balancer.rebalancer import SimpleBalancer
from crypto_balancer.ccxt_exchange import CCXTExchange, exchanges
from crypto_balancer.executor import TradeExecutor
from crypto_balancer.portfolio import Portfolio

logger = logging.getLogger(__name__)


def main(args=None):
    config = configparser.ConfigParser()
    config.read('config.ini')

    def exchange_choices():
        return set(config.sections()) & set(exchanges)

    parser = argparse.ArgumentParser(
        description='Balance holdings on an exchange.')
    parser.add_argument('--trade', action="store_true",
                        help='Actually place orders')
    parser.add_argument('--force', action="store_true",
                        help='Force rebalance')
    parser.add_argument('--max_orders', default=5,
                        help='Maximum number of orders to perform in '
                             'rebalance')
    parser.add_argument('--valuebase', default='USDT',
                        help='Currency to value portfolio in')
    parser.add_argument('--cancel', action="store_true",
                        help='Cancel open orders first')
    parser.add_argument('--mode', choices=['mid', 'passive', 'cheap'],
                        default='mid',
                        help='Mode to place orders')
    parser.add_argument('exchange', choices=exchange_choices())
    args = parser.parse_args()

    config = config[args.exchange]

    # Tak
    try:
        targets = [x.split() for x in config['targets'].split('\n')]
        targets = dict([[a, float(b)] for (a, b) in targets])
    except ValueError:
        logger.error("Targets format invalid")
        sys.exit(1)

    if sum(targets.values()) != 100:
        logger.error("Total target needs to equal 100")
        sys.exit(1)

    valuebase = config.get('valuebase') or args.valuebase

    exchange = CCXTExchange(args.exchange,
                            config['api_key'],
                            config['api_secret'])

    balancer = SimpleBalancer()
    executor = TradeExecutor(exchange, balancer)
    executor_res = executor.run(force=args.force,
                                trade=args.trade,
                                mode=args.mode)


if __name__ == '__main__':
    main()
