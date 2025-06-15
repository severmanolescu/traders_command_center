"""
Get holdings from portfolio.json and CoinMarketCap API.
"""

from src.api_client import get_crypto_data_by_symbols
from src.variables_fetcher import load_json_file


# pylint: disable=too-many-locals
def get_holdings():
    """
    Retrieve portfolio holdings from portfolio.json and CoinMarketCap API.
    Returns:
        tuple: A tuple containing:
            - holdings (list): List of dictionaries with holding details.
            - current_value (float): Total current value of the portfolio.
            - initial_investment (float): Total initial investment in the portfolio.
    """
    portfolio = load_json_file("./config/portfolio.json")
    coins = [key for key in portfolio.keys() if key != "last_update"]
    coins_data = get_crypto_data_by_symbols(coins)
    holdings = []

    if not coins_data or "data" not in coins_data:
        return holdings, 0, 0

    initial_investment = 0
    coin_values = {}
    for symbol, data in portfolio.items():
        if symbol != "last_update":
            coin_data = coins_data["data"][symbol]
            if coin_data:
                quantity = data["quantity"]
                coin_price = coin_data["quote"]["USD"]["price"]
                value = quantity * coin_price
                coin_values[symbol] = {
                    "coin_data": coin_data,
                    "quantity": quantity,
                    "avg_price": data["average_price"],
                    "total_investment": data["total_investment"],
                    "value": value,
                }
                initial_investment += data["total_investment"]

    current_value = sum(item["value"] for item in coin_values.values())

    for symbol, item in coin_values.items():
        coin_data = item["coin_data"]
        value = item["value"]
        total_investment = item["total_investment"]
        pnl_amount = value - total_investment
        pnl_percentage = (
            (pnl_amount / total_investment) * 100 if total_investment > 0 else 0
        )
        allocation = (value / current_value) * 100 if current_value > 0 else 0

        holding = {
            "asset": coin_data["name"],
            "symbol": symbol,
            "holdings": round(item["quantity"], 2),
            "exchange": "Binance",
            "avg_price": item["avg_price"],
            "current_price": coin_data["quote"]["USD"]["price"],
            "value": value,
            "day_change": round(coin_data["quote"]["USD"]["percent_change_24h"], 2),
            "week_change": round(coin_data["quote"]["USD"]["percent_change_7d"], 2),
            "pnl_amount": pnl_amount,
            "pnl_percentage": pnl_percentage,
            "allocation": round(allocation, 2),
        }
        holdings.append(holding)

    coin_mappings = load_json_file("./config/coin_mappings.json")
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
