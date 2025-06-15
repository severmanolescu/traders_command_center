"""
Risk assessment module for portfolio management.
"""

import logging

from src.variables_fetcher import load_json_file

logger = logging.getLogger(__name__)


def calculate_risk_level(holdings):
    """
    Calculate portfolio risk level.

    Args:
        holdings (list): List of holding dictionaries

    Returns:
        str: Risk level (Low, Medium, Medium-High, High, Very High)
        float: Calculated risk score
    """
    if not holdings:
        return "Low", 0

    # You can define asset risk levels based on your judgment or historical data
    asset_risk_levels = load_json_file("./config/asset_risk_levels.json")

    if not asset_risk_levels:
        logger.warning("Asset risk levels not found or empty. Defaulting to low risk.")
        return "Low", 0

    # Default risk level for unknown assets
    default_risk = 85

    # Calculate weighted risk score
    total_weight = 0
    weighted_risk = 0

    for holding in holdings:
        symbol = holding["symbol"]
        allocation = holding["allocation"]
        risk_score = asset_risk_levels.get(symbol, default_risk)

        weighted_risk += risk_score * allocation
        total_weight += allocation

    # Calculate average risk score
    avg_risk_score = weighted_risk / total_weight if total_weight > 0 else default_risk

    # Map score to risk level
    if avg_risk_score < 60:
        risk_level = "Very Low"
    elif avg_risk_score < 70:
        risk_level = "Low"
    elif avg_risk_score < 80:
        risk_level = "Medium"
    elif avg_risk_score < 90:
        risk_level = "High"
    else:
        risk_level = "Very High"

    return risk_level, round(avg_risk_score, 1)


def calculate_portfolio_volatility(holdings):
    """
    Calculate portfolio volatility.

    Args:
        holdings (list): List of holding dictionaries

    Returns:
        float: Portfolio volatility as a percentage
    """
    if not holdings:
        return 0

    total_allocation = 0
    weighted_volatility = 0

    for holding in holdings:
        allocation = holding["allocation"]

        week_volatility = abs(holding["week_change"])
        annualized_volatility = week_volatility * 3.7  # Rough conversion to annual

        weighted_volatility += annualized_volatility * allocation
        total_allocation += allocation

    # Calculate average volatility
    avg_volatility = (
        weighted_volatility / total_allocation if total_allocation > 0 else 0
    )

    return round(avg_volatility, 1)


# pylint: disable=too-many-return-statements
def determine_risk_level(value, metric_type):
    """
    Determine risk level, color, and width based on metric value
    """

    if metric_type == "volatility":
        if value < 15:
            return {"level": "Low", "color": "green", "width": "40%"}
        if value < 30:
            return {"level": "Medium", "color": "yellow", "width": "65%"}
        return {"level": "High", "color": "red", "width": "80%"}
    if metric_type == "diversity":
        if value < 4:
            return {"level": "Poor", "color": "red", "width": "35%"}
        if value < 7:
            return {"level": "Medium", "color": "yellow", "width": "60%"}
        return {"level": "Good", "color": "green", "width": "74%"}
    if metric_type == "max_drawdown":
        if value < 15:
            return {"level": "Low", "color": "green", "width": "40%"}
        if value < 25:
            return {"level": "Medium", "color": "yellow", "width": "65%"}
        return {"level": "High", "color": "red", "width": "80%"}
    if metric_type == "sharpe_ratio":
        if value < 0.5:
            return {"level": "Poor", "color": "red", "width": "35%"}
        if value < 1:
            return {"level": "Medium", "color": "yellow", "width": "50%"}
        return {"level": "Good", "color": "green", "width": "68%"}
    return {"level": "Unknown", "color": "gray", "width": "50%"}
