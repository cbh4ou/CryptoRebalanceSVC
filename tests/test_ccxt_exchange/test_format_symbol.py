import unittest
from unittest.mock import MagicMock, patch
from crypto_balancer.ccxt_exchange import CCXTExchange


def get_mock():
    return MagicMock()


def get_exchange():
    return CCXTExchange(name="binance", api_key="key", api_secret="secret")


class TestFormatSymbol(unittest.TestCase):

    def test_get_rates(self):
        self.assertEqual(CCXTExchange.format_symbol('BTC', 'USDT'), 'BTC/USDT')
