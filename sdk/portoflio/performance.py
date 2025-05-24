import json

from datetime import datetime
from sdk.variables_fetcher import load_json_file


def get_portfolio_performance():
    transactions = load_json_file('./config/transactions.json')

    portfolio_history = load_json_file('./config/portfolio_history.json')

    # Convert timestamps to JavaScript format (milliseconds since epoch)
    # And prepare data for different time periods
    chart_data = {
        "1D": [],
        "1W": [],
        "1M": [],
        "3M": [],
        "1Y": [],
        "All": []
    }

    # Current timestamp for filtering
    now = datetime.now()

    # Process each history entry
    for entry in portfolio_history:
        entry_date = datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S")
        timestamp = int(entry_date.timestamp() * 1000)  # Convert to milliseconds for JS

        # Create data point
        data_point = {
            "x": timestamp,
            "total_value": entry["total_value"],
            "total_investment": entry["total_investment"],
            "profit_loss": entry["profit_loss"],
            "profit_loss_percentage": entry["profit_loss_percentage"]
        }

        # Add to appropriate time periods
        days_diff = (now - entry_date).days

        # All
        chart_data["All"].append(data_point)

        # 1Y (365 days)
        if days_diff <= 365:
            chart_data["1Y"].append(data_point)

        # 3M (90 days)
        if days_diff <= 90:
            chart_data["3M"].append(data_point)

        # 1M (30 days)
        if days_diff <= 30:
            chart_data["1M"].append(data_point)

        # 1W (7 days)
        if days_diff <= 7:
            chart_data["1W"].append(data_point)

        # 1D (1 day)
        if days_diff <= 1:
            chart_data["1D"].append(data_point)

    # Sort each dataset by timestamp
    for period in chart_data:
        chart_data[period] = sorted(chart_data[period], key=lambda x: x["x"])

    # Convert to JSON for JavaScript
    chart_data_json = json.dumps(chart_data)

    return transactions, chart_data_json