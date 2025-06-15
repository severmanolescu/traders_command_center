"""
Get holdings from portfolio.json and CoinMarketCap API.
"""

from src.api_client import get_crypto_data_by_symbols
from src.variables_fetcher import load_json_file


# pylint: disable=too-many-locals
def get_holdings():
    """
    Get portfolio data from CoinMarketCap and portfolio.json.

    Returns:
        list: list of all holding coins
        float: portfolio total value at current price
        float: initial investment
    """
    portfolio = load_json_file("./config/portfolio.json")

    coins = [key for key in portfolio.keys() if key != "last_update"]

    coins_data = get_crypto_data_by_symbols(coins)

    holdings = []

    if not coins_data or "data" not in coins_data:
        return holdings, 0, 0

    current_value = 0
    initial_investment = 0

    for symbol, data in portfolio.items():
        if symbol != "last_update":
            coin_data = coins_data["data"][symbol]

            if coin_data:
                current_price = coin_data["quote"]["USD"]["price"]
                quantity = data["quantity"]
                current_value += current_price * quantity

                quantity = data["quantity"]
                avg_price = data["average_price"]
                total_investment = data["total_investment"]

                initial_investment += total_investment

                coin_price = coin_data["quote"]["USD"]["price"]
                value = quantity * coin_price

                pnl_amount = value - total_investment
                pnl_percentage = (
                    (pnl_amount / data["total_investment"]) * 100
                    if data["total_investment"] > 0
                    else 0
                )
                allocation = (value / current_value) * 100 if current_value > 0 else 0

                holding = {
                    "asset": coin_data["name"],
                    "symbol": symbol,
                    "holdings": round(quantity, 2),
                    "exchange": "Binance",
                    "avg_price": avg_price,
                    "current_price": coin_price,
                    "value": value,
                    "day_change": round(
                        coin_data["quote"]["USD"]["percent_change_24h"], 2
                    ),
                    "week_change": round(
                        coin_data["quote"]["USD"]["percent_change_7d"], 2
                    ),
                    "pnl_amount": pnl_amount,
                    "pnl_percentage": pnl_percentage,
                    "allocation": round(allocation, 2),
                }

                holdings.append(holding)

    # Load coin mappings
    coin_mappings = load_json_file("./config/coin_mappings.json")

    # Add icon info to each holding
    for holding in holdings:
        symbol = holding["symbol"]
        if symbol in coin_mappings:
            holding["coin_info"] = coin_mappings[symbol]
        else:
            holding["coin_info"] = {
                "name": symbol.lower(),
                "color": "#F0F0F0",
                "icon": None,
            }

    return holdings, current_value, initial_investment
