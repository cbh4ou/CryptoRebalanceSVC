import argparse
import configparser
import logging
import sys

from crypto_balancer.simple_balancer import SimpleBalancer
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

    total_target = sum(targets.values())
    if total_target != 100:
        logger.error("Total target needs to equal 100, it is {}"
                     .format(total_target))
        sys.exit(1)

    valuebase = config.get('valuebase') or args.valuebase

    exchange = CCXTExchange(args.exchange,
                            config['api_key'],
                            config['api_secret'])

    print("Connected to exchange: {}".format(exchange.name))

    if args.cancel:
        print("Cancelling open orders...")
        for order in exchange.cancel_orders():
            print("Cancelled order:", order['symbol'], order['id'])

    threshold = float(config['threshold'])
    max_orders = int(args.max_orders)

    portfolio = Portfolio.make_portfolio(
        targets, exchange, threshold, valuebase)

    print("Current Portfolio:")
    for currency in portfolio.balances:
        bal = portfolio.balances[currency]
        pct = portfolio.balances_pct[currency]
        tgt = targets[currency]
        # print("  {:<6s} {:<8.2f} ({:>5.2f} / {:>5.2f}%)"
        #     .format(currency, bal, pct, tgt))

    print("  Total value: {:.2f} {}".format(portfolio.valuation_quote,
                                            portfolio.quote_currency))
    balancer = SimpleBalancer()
    executor = TradeExecutor(portfolio, exchange, balancer)
    executor_res = executor.run(force=args.force,
                                trade=args.trade,
                                max_orders=max_orders,
                                mode=args.mode)

    print("  Balance RMS error: {:.2g} / {:.2g}".format(
        executor_res['initial_portfolio'].balance_rms_error,
        threshold))

    print("  Balance Max error: {:.2g} / {:.2g}".format(
        executor_res['initial_portfolio'].balance_max_error,
        threshold))

    if not portfolio.needs_balancing and not args.force:
        print("No balancing needed")
        sys.exit(0)

    print("Balancing needed{}:".format(" [FORCED]" if args.force else ""))

    print("Proposed Portfolio:")
    portfolio = executor_res['proposed_portfolio']

    if not portfolio:
        print("Could not calculate a better portfolio")
        sys.exit(0)

    for currency in portfolio.balances:
        bal = portfolio.balances[currency]
        pct = portfolio.balances_pct[currency]
        tgt = targets[currency]
        print("  {:<6s} {:<8.2f} ({:>5.2f} / {:>5.2f}%)"
              .format(currency, bal, pct, tgt))

    print("  Total value: {:.2f} {}".format(portfolio.valuation_quote,
                                            portfolio.quote_currency))
    print("  Balance RMS error: {:.2g} / {:.2g}".format(
        executor_res['proposed_portfolio'].balance_rms_error,
        threshold))

    print("  Balance Max error: {:.2g} / {:.2g}".format(
        executor_res['proposed_portfolio'].balance_max_error,
        threshold))

    total_fee = '%s' % float('%.4g' % executor_res['total_fee'])
    print("  Total fees to re-balance: {} {}"
          .format(total_fee,
                  portfolio.quote_currency))

    print("Orders:")
    if args.trade:
        for order in executor_res['success']:
            print("  Submitted: {}".format(order))

        for order in executor_res['errors']:
            print("  Failed: {}".format(order))
            print("  Error Response: {}".format(order))
    else:
        for order in executor_res['orders']:
            print("  " + str(order))


if __name__ == '__main__':
    main()
