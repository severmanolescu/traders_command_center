"""
Calculate portfolio performance over time and categorize it into different time periods.
"""

import json
from datetime import datetime

from sdk.variables_fetcher import load_json_file


def categorize_history_by_time(portfolio_history):
    """
    Categorize portfolio history into predefined time periods.

    Converts datetime strings to timestamps and organizes data into:
    1D, 1W, 1M, 3M, 1Y, and All.

    Args:
        portfolio_history (list): List of portfolio history entries.

    Returns:
        dict: Dictionary of categorized history data points by time period.
    """
    chart_data = {"1D": [], "1W": [], "1M": [], "3M": [], "1Y": [], "All": []}

    now = datetime.now()

    for entry in portfolio_history:
        entry_date = datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S")
        timestamp = int(entry_date.timestamp() * 1000)  # milliseconds for JS

        data_point = {
            "x": timestamp,
            "total_value": entry["total_value"],
            "total_investment": entry["total_investment"],
            "profit_loss": entry["profit_loss"],
            "profit_loss_percentage": entry["profit_loss_percentage"],
        }

        days_diff = (now - entry_date).days

        chart_data["All"].append(data_point)
        if days_diff <= 365:
            chart_data["1Y"].append(data_point)
        if days_diff <= 90:
            chart_data["3M"].append(data_point)
        if days_diff <= 30:
            chart_data["1M"].append(data_point)
        if days_diff <= 7:
            chart_data["1W"].append(data_point)
        if days_diff <= 1:
            chart_data["1D"].append(data_point)

    return chart_data


def sort_chart_data(chart_data):
    """
    Sort each time period's chart data by timestamp.

    Args:
        chart_data (dict): Chart data with lists of data points.

    Returns:
        dict: Chart data with sorted data points.
    """
    for period in chart_data:
        chart_data[period] = sorted(chart_data[period], key=lambda x: x["x"])
    return chart_data


def get_portfolio_performance():
    """
    Generate portfolio performance chart data.

    Returns:
        tuple:
            - list: Transaction entries.
            - str: JSON string of chart data categorized by time period.
    """
    transactions = load_json_file("//config/transactions.json")
    portfolio_history = load_json_file("./config/portfolio_history.json")

    chart_data = categorize_history_by_time(portfolio_history)
    sorted_chart_data = sort_chart_data(chart_data)
    chart_data_json = json.dumps(sorted_chart_data)

    return transactions, chart_data_json
