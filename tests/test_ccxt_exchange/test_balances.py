import unittest
from unittest.mock import MagicMock, patch
from crypto_balancer.ccxt_exchange import CCXTExchange


def get_mock():
    return MagicMock()


def get_exchange():
    return CCXTExchange(name="binance", api_key="key", api_secret="secret")


class TestBalances(unittest.TestCase):
    def get_balance_data(self):
        return {
            'free': {
                'BTC': 0.5,
                'XRP': 1000
            },
            'used': {
                'ETH': 0.5,
                'XRP': 1000
            },
            'total': {
                'BTC': 0.5,
                'XRP': 1000
            }
        }

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_free_balances(self, mock_binance):
        mock_exchange = get_mock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = self.get_balance_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        exchange = get_exchange()

        # Now get_free_balances should return filtered results
        result = (
            exchange.get_free_balances()
        )  # Here we access the property without parentheses
        expected_result = {"BTC": 0.5, "XRP": 1000}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_locked_balances(self, mock_binance):
        mock_exchange = get_mock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = self.get_balance_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        exchange = get_exchange()

        # Now get_locked_balances should return filtered results
        result = (
            exchange.get_locked_balances()
        )  # Here we access the property without parentheses
        expected_result = {"ETH": 0.5, "XRP": 1000}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_total_balances(self, mock_binance):
        mock_exchange = get_mock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = self.get_balance_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        exchange = get_exchange()

        # Now get_locked_balances should return filtered results
        result = (
            exchange.get_total_balances()
        )  # Here we access the property without parentheses
        expected_result = {"BTC": 0.5, "XRP": 1000}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()


if __name__ == "__main__":
    unittest.main()
