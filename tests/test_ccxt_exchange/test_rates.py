import unittest
from unittest.mock import MagicMock, patch
from crypto_balancer.ccxt_exchange import CCXTExchange


def get_mock():
    return MagicMock()


def get_exchange():
    return CCXTExchange(name="binance", api_key="key", api_secret="secret")


class TestGetRates(unittest.TestCase):
    ticker_data = {"BNB/USDT": {"ask": 244.57, "bid": 244.5}, "BTC/USDT": {}}

    orderbook_data = {
        "asks": [
            [30303.18, 0.09207],
            [30710.0, 0.001],
        ],
        "bids": [
            [30303.02, 0.068767],
            [30199.13, 0.000383],
        ],
    }

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_ticker_rate(self, mock_binance):
        mock_exchange = get_mock()

        # Setup the mock response
        mock_exchange.fetch_tickers.return_value = self.ticker_data
        mock_exchange.fetchOrderBook.return_value = self.orderbook_data

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        exchange = get_exchange()

        # Now get_locked_balances should return filtered results
        result = exchange.get_rate("BNB/USDT")  # Here we access the property without parentheses
        expected_result = {"mid": 244.535, "high": 244.57, "low": 244.5}

        self.assertEqual(result, expected_result)

        # Make sure fetch_tickers was actually called
        mock_exchange.fetch_tickers.assert_called_once()
        mock_exchange.fetchOrderBook.assert_called_once()
