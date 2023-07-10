from crypto_balancer.ccxt_exchange import CCXTExchange


class Rebalancer:
    def __init__(
        self, exchange: CCXTExchange, targets: dict, quote_currency, mode="mid"
    ):
        self.exchange = exchange
        self.targets = targets
        self.quote_currency = quote_currency
        self.mode = mode

    def rebalance(self):
        exchange = self.exchange
        targets = self.targets
        quote_currency = self.quote_currency
        mode = self.mode

        # Get the portfolio total and extract the total balance and codes
        portfolio = exchange.get_portfolio_total(quote_currency, mode)
        total_balance = portfolio["total"]
        codes = portfolio["codes"]

        # Calculate the weights for each code
        weights = {
            code: value / total_balance for code, value in codes.items() if value != 0.0
        }

        # Calculate the weights with direction
        weights_with_direction = [
            (code, targets[code] / 100 - value)
            if code in targets
            else (code, 0 - value)
            for code, value in weights.items()
        ]

        failed_sum = 0
        pass_sum = 0
        all_tradeable_amounts = {}

        # Check limits for each code and update all_tradeable_amounts
        for code, value in weights_with_direction:
            does_pass = exchange.check_limits(
                code, quote_currency, abs(value), mode, total_balance
            )
            if does_pass:
                all_tradeable_amounts[code] = value
                pass_sum += value
            else:
                failed_sum += weights[code]

        print("Amount not tradeable: ", failed_sum)

        # Sort all_tradeable_amounts by value
        all_tradeable_amounts = dict(
            sorted(all_tradeable_amounts.items(), key=lambda x: x[1])
        )

        # Initialize sell_amounts and buy_amounts
        sell_amounts = {}
        buy_amounts = {}

        # Separate all_tradeable_amounts into sell_amounts and buy_amounts
        for code, value in all_tradeable_amounts.items():
            if value < 0:
                sell_amounts[code] = value
            else:
                buy_amounts[code] = value

        # Build Initial Routes
        trade_routes = []
        for code, _ in all_tradeable_amounts.items():
            # Get the codes with the least and most amounts
            sell_code = min(sell_amounts, key=sell_amounts.get)
            buy_code = max(buy_amounts, key=buy_amounts.get)

            # Calculate the buy and sell weights
            buy_weight = buy_amounts[buy_code]
            sell_weight = sell_amounts[sell_code]
            total_weight = sell_weight + buy_weight

            # Skip if either the buy or sell weight is zero
            if sell_weight == 0 or buy_weight == 0:
                continue

            # Update the buy and sell amounts based on the total weight
            if total_weight < 0:
                sell_amounts[sell_code] = total_weight
                buy_amounts[buy_code] = 0
            else:
                sell_amounts[sell_code] = 0
                buy_amounts[buy_code] = total_weight

            # Get the smart route for the two codes
            route = exchange.get_smart_route(sell_code, buy_code)
            trade_routes.append({"route": route, "weight": abs(total_weight)})

        return trade_routes
