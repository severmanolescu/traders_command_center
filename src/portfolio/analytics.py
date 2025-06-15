"""
Calculate portfolio analytics such as profit/loss, changes over time,
iversity score, risk metrics, and more.
"""

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.portfolio.holdings import get_holdings
from src.portfolio.performance import get_portfolio_performance
from src.portfolio.risk import (
    calculate_portfolio_volatility,
    calculate_risk_level,
    determine_risk_level,
)
from src.portfolio.transactions import load_transactions
from src.variables_fetcher import get_atl_ath, load_json_file

logger = logging.getLogger(__name__)


def calculate_profit_loss(current_value, initial_investment):
    """
    Calculate profit/loss metrics.

    Args:
        current_value (float): Current total value of the portfolio
        initial_investment (float): Initial investment amount

    Returns:
        dict: Dictionary containing P/L metrics
    """
    # Calculate P/L amount
    pnl_amount = current_value - initial_investment

    # Calculate P/L percentage
    if initial_investment > 0:
        pnl_percentage = (pnl_amount / initial_investment) * 100
    else:
        pnl_percentage = 0

    logger.info(
        "Calculated P/L: Amount = %s, Percentage = %s", pnl_amount, pnl_percentage
    )

    return {"amount": round(pnl_amount, 2), "percentage": round(pnl_percentage, 2)}


def load_and_normalize_history(path="./config/portfolio_history.json"):
    """
    Load and normalize the portfolio history from a JSON file.

    Args:
        path (str): Path to the portfolio history JSON file.

    Returns:
        list: A list of history entries with parsed datetime, sorted from newest to oldest.
    """
    history = load_json_file(path)

    if isinstance(history, dict) and "history" in history:
        history = history["history"]
    elif not isinstance(history, list):
        logger.error("Invalid history format")
        return []

    for entry in history:
        if "datetime" in entry:
            try:
                entry["parsed_datetime"] = datetime.strptime(
                    entry["datetime"], "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                logger.error("Invalid datetime format: %s", entry["datetime"])
                entry["parsed_datetime"] = datetime.now()

    history.sort(key=lambda x: x.get("parsed_datetime", datetime.min), reverse=True)
    return history


def get_change_for_period(history, current_value, current_time, delta):
    """
    Calculate the portfolio change for a specific time period.

    Args:
        history (list): List of history entries with parsed datetime.
        current_value (float): The most recent portfolio total value.
        current_time (datetime): The datetime of the most recent entry.
        delta (timedelta): The time period to compare against.

    Returns:
        dict: Dictionary with amount, percentage, and positivity of change.
    """
    target_time = current_time - delta
    closest_entry = None
    min_time_diff = float("inf")

    for entry in history:
        if "parsed_datetime" not in entry:
            continue
        entry_time = entry["parsed_datetime"]
        time_diff = abs((entry_time - target_time).total_seconds())
        if time_diff < min_time_diff:
            min_time_diff = time_diff
            closest_entry = entry

    if closest_entry and min_time_diff <= 86400:
        past_value = closest_entry["total_value"]
        change_amount = current_value - past_value
        change_percentage = (change_amount / past_value * 100) if past_value else 0
        return {
            "amount": f"${round(change_amount, 2):,.2f}",
            "percentage": f"{round(change_percentage, 2):,.2f}%",
            "is_positive": change_amount >= 0,
        }

    return {"amount": 0, "percentage": 0, "is_positive": True}


def calculate_changes_from_history():
    """
    Calculate portfolio changes over 24h, 7d, and 30d using portfolio history.

    Returns:
        dict: Dictionary containing changes (amount, percentage, and positivity)
              for each predefined time period.
    """
    history = load_and_normalize_history()
    if not history:
        return default_changes()

    current_entry = history[0]
    current_value = current_entry["total_value"]
    current_time = current_entry["parsed_datetime"]

    time_periods = {
        "24h": timedelta(days=1),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }

    changes = {
        period: get_change_for_period(history, current_value, current_time, delta)
        for period, delta in time_periods.items()
    }

    return changes


def default_changes():
    """
    Return default changes when no data is available
    """
    return {
        "24h": {"amount": 0, "percentage": 0, "is_positive": True},
        "7d": {"amount": 0, "percentage": 0, "is_positive": True},
        "30d": {"amount": 0, "percentage": 0, "is_positive": True},
    }


def calculate_diversity_score(holdings, max_score=10):
    """
    Calculate portfolio diversity score on a scale of 0 to max_score.
    Higher score means better diversification.

    Args:
        holdings (list): List of holding dictionaries
        max_score (int): Maximum score value (default: 10)

    Returns:
        float: Diversity score from 0 to max_score
    """
    if not holdings:
        return 0

    # Get allocation percentages
    allocations = []

    for h in holdings:
        allocations.append(h["allocation"])

    # Calculate Herfindahl-Hirschman Index (HHI) - a measure of concentration
    # HHI is the sum of squared percentages (lower is more diverse)
    hhi = sum((alloc / 100) ** 2 for alloc in allocations)
    # Normalize HHI to [0, 1] range
    # Perfect diversity (equal allocation): HHI = 1/n (n = number of assets)
    # Worst diversity (one asset = 100%): HHI = 1
    n = len(holdings)
    min_hhi = 1 / n  # Theoretical minimum HHI (perfect diversity)
    normalized_hhi = (1 - hhi) / (1 - min_hhi) if n > 1 else 0

    # Convert to score from 0 to max_score
    score = normalized_hhi * max_score

    # Round to 1 decimal place
    return round(score, 1)


def calculate_metrics_from_portfolio_history():
    """
    Calculate risk metrics from portfolio history data.

    Returns:
        Dictionary of risk metrics.
    """
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(load_json_file("./config/portfolio_history.json"))

    if len(df) == 0:
        return 0, 0

    # Convert datetime to proper datetime format and set as index
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")  # Ensure chronological order
    df.set_index("datetime", inplace=True)

    # Calculate daily returns based on total_value
    df["daily_return"] = df["total_value"].pct_change()

    # Drop NaN values (first row will have NaN return)
    df = df.dropna()

    # Calculate Max Drawdown
    # First, calculate cumulative returns (starting from 1)
    df["cumulative_return"] = (1 + df["daily_return"]).cumprod()

    # Calculate running maximum
    df["running_max"] = df["cumulative_return"].cummax()

    # Calculate drawdown
    df["drawdown"] = df["cumulative_return"] / df["running_max"] - 1

    # Find the maximum drawdown
    max_drawdown = abs(df["drawdown"].min()) * 100  # Convert to percentage

    # Calculate Sharpe Ratio
    # Assuming risk-free rate of 2% annually
    risk_free_rate = 0.02 / 252  # Daily risk-free rate

    # Calculate excess return
    df["excess_return"] = df["daily_return"] - risk_free_rate

    # Calculate Sharpe Ratio
    # For daily returns, multiply by sqrt(252) to annualize
    sharpe_ratio = df["excess_return"].mean() / df["daily_return"].std() * np.sqrt(252)

    return round(max_drawdown, 2), round(sharpe_ratio, 2)


# pylint: disable=too-many-locals
def calculate_portfolio_data():
    """
    Calculate the portfolio data.

    Returns:
        dict: with all the portfolio data.
    """
    holdings, current_value, initial_investment = get_holdings()

    profit_loss = calculate_profit_loss(current_value, initial_investment)

    all_time_low, all_time_high = get_atl_ath()

    history_changes = calculate_changes_from_history()

    diversity_score = calculate_diversity_score(holdings)

    risk_string, risk_level = calculate_risk_level(holdings)

    portfolio_volatility = calculate_portfolio_volatility(holdings)

    transactions = load_transactions()

    # pylint: disable=unused-variable
    transactions_performance, chart_data_json = get_portfolio_performance()

    max_drawdown, sharpe_ratio = calculate_metrics_from_portfolio_history()

    if holdings:
        weighted_change = sum(
            holding["day_change"] * holding["allocation"] / 100 for holding in holdings
        )
    else:
        weighted_change = 0

    weighted_change = round(weighted_change, 2)

    is_positive_total_value = weighted_change > 0
    is_positive_all_time = profit_loss["amount"] > 0

    risk_levels = {
        "volatility": determine_risk_level(portfolio_volatility, "volatility"),
        "diversity": determine_risk_level(diversity_score, "diversity"),
        "max_drawdown": determine_risk_level(max_drawdown, "max_drawdown"),
        "sharpe_ratio": determine_risk_level(sharpe_ratio, "sharpe_ratio"),
    }
    return {
        # Holdings table
        "holdings": holdings,
        # Portfolio Value Card
        "current_value": f"${round(current_value, 2):,.2f}",
        "is_positive_total_value": is_positive_total_value,
        "weighted_change": weighted_change,
        "all_time_low": f"${all_time_low:,.2f}",
        "all_time_high": f"${all_time_high:,.2f}",
        # Profit & Loss Card
        "all_time_profit": f"${profit_loss['amount']:,.2f}",
        "all_time_profit_percentage": profit_loss["percentage"],
        "is_positive_all_time": is_positive_all_time,
        "profit_24h": history_changes["24h"]["amount"],
        "profit_percentage_24": history_changes["24h"]["percentage"],
        "is_positive_24h": history_changes["24h"]["is_positive"],
        "profit_7d": history_changes["7d"]["amount"],
        "profit_percentage_7d": history_changes["7d"]["percentage"],
        "is_positive_7d": history_changes["7d"]["is_positive"],
        "profit_30d": history_changes["30d"]["amount"],
        "profit_percentage_30d": history_changes["30d"]["percentage"],
        "is_positive_30d": history_changes["30d"]["is_positive"],
        # Allocation & Metrics
        "assets_count": len(holdings),
        "diversity_score": diversity_score,
        "risk_string": risk_string,
        "risk_level": risk_level,
        "portfolio_volatility": portfolio_volatility,
        # Recent Transactions
        "transactions": transactions,
        # Portfolio Performance
        "chart_data": chart_data_json,
        # Risk Analysis
        "risk_levels": risk_levels,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
    }
