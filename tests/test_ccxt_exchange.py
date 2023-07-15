import unittest
from unittest.mock import MagicMock, patch
from crypto_balancer.ccxt_exchange import CCXTExchange


def get_test_data():
    return {
        "total": {"BTC": "0.5", "XRP":"1000"},
        "info": {
            "balances": [
                {"asset": "BTC", "free": "0.5", "locked": "0"},
                {"asset": "ETH", "free": "0", "locked": "0.5"},
                {"asset": "XRP", "free": "1000", "locked": "1000"},
            ]
        },
    }


class TestCCXTExchange(unittest.TestCase):
    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_free_balances(self, mock_binance):
        # Create an instance of the mock exchange
        mock_exchange = MagicMock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = get_test_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        # Instantiate the object you're testing
        exchange = CCXTExchange(name="binance", api_key="key", api_secret="secret")

        # Now get_free_balances should return filtered results
        result = (
            exchange.get_free_balances()
        )  # Here we access the property without parentheses
        expected_result = {"BTC": "0.5", "XRP": "1000"}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_locked_balances(self, mock_binance):
        # Create an instance of the mock exchange
        mock_exchange = MagicMock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = get_test_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        # Instantiate the object you're testing
        exchange = CCXTExchange(name="binance", api_key="key", api_secret="secret")

        # Now get_locked_balances should return filtered results
        result = (
            exchange.get_locked_balances()
        )  # Here we access the property without parentheses
        expected_result = {"ETH": "0.5", "XRP": "1000"}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()

    @patch("ccxt.binance")  # Mock the binance exchange directly
    def test_get_total_balances(self, mock_binance):
        # Create an instance of the mock exchange
        mock_exchange = MagicMock()

        # Setup the mock response
        mock_exchange.fetch_balance.return_value = get_test_data()

        # Make ccxt.binance() return the mock exchange instance
        mock_binance.return_value = mock_exchange

        # Instantiate the object you're testing
        exchange = CCXTExchange(name="binance", api_key="key", api_secret="secret")

        # Now get_locked_balances should return filtered results
        result = (
            exchange.get_total_balances()
        )  # Here we access the property without parentheses
        expected_result = {"BTC": "0.5", "XRP": "1000"}
        self.assertEqual(result, expected_result)

        # Make sure fetch_balance was actually called
        mock_exchange.fetch_balance.assert_called_once()


if __name__ == "__main__":
    unittest.main()
