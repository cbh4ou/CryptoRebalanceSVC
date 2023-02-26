import math
from crypto_balancer.ccxt_exchange import CCXTExchange

class Portfolio():

    @classmethod
    def make_portfolio(cls, targets, exchange: CCXTExchange,
                       threshold=1.0, quote_currency="USD"):
        p = cls(targets, exchange, threshold)
        p.sync_balances()
        p.sync_rates()
        return p

    def __init__(self, targets, exchange: CCXTExchange, threshold=1.0,
                 quote_currency="USD"):
        self.targets = targets
        self.threshold = threshold
        self.exchange = exchange
        self.quote_currency = quote_currency
        self.balances = {}
        self.rates = {}

    def copy(self):
        p = Portfolio(self.targets,
                      self.exchange,
                      self.threshold,
                      self.quote_currency)
        p.balances = self.balances.copy()
        p.rates = self.rates.copy()
        return p

    def sync_balances(self):
        self.balances = self.exchange.get_total_balances

    def sync_rates(self):
        self.rates = self.exchange.rates.copy()

    @property
    def currencies(self):
        return self.targets.keys()

    @property
    def balances_quote(self):
        _balances_quote = {}
        qc = self.quote_currency
        for currency in self.currencies:
            amount = self.balances[currency]
            if currency == self.quote_currency:
                _balances_quote[currency] = amount
            else:
                pair = f"{currency}/{qc}"
                try:
                    _balances_quote[currency] = amount * self.rates[pair]['mid']
                except KeyError:
                    raise ValueError("Invalid pair: {}".format(pair))
        return _balances_quote

    @property
    def valuation_quote(self):
        return sum(self.balances_quote.values())

    @property
    def needs_balancing(self):
        return self.balance_max_error > self.threshold

    @property
    def balances_pct(self):
        # first convert the amounts into their base value
        _balances_quote = self.balances_quote
        _total = self.valuation_quote

        if not _total:
            return {currency: 0 for currency in self.currencies}

        return {currency: (_balances_quote[currency] / _total) * 100.0
                for currency in self.currencies}

    @property
    def balance_errors_pct(self):
        _balances_quote = self.balances_quote
        _total = sum(_balances_quote.values())

        if not _total:
            return []

        def calc_diff(currency):
            return _total * (self.targets[currency] / 100.0) \
                - _balances_quote[currency]

        pcts = [(calc_diff(currency) / _total) * 100.0
                for currency in self.currencies]
        return pcts

    @property
    def balance_rms_error(self):
        pcts = self.balance_errors_pct
        num = len(pcts)
        if not num:
            return 0.0
        return math.sqrt(sum([x**2 for x in pcts]) / num)

    @property
    def balance_max_error(self):
        pcts = self.balance_errors_pct
        pcts = [abs(x) for x in pcts]
        return max(pcts)

    @property
    def differences_quote(self):
        # first convert the amounts into their base value
        _balances_quote = self.balances_quote
        _total = self.valuation_quote

        def calc_diff(currency):
            return _total * (self.targets[currency] / 100.0) \
                - _balances_quote[currency]

        return {currency: calc_diff(currency) for currency in self.currencies}
