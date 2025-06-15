"""
Test risk calculations in the portfolio module.
"""

from src.portfolio.risk import (
    calculate_portfolio_volatility,
    calculate_risk_level,
    determine_risk_level,
)


def test_calculate_risk_level():
    """Test the calculation of portfolio risk level."""
    holdings = [
        {"symbol": "BTC", "allocation": 0.5},
        {"symbol": "ETH", "allocation": 0.3},
        {"symbol": "XRP", "allocation": 0.2},
    ]

    risk_level, avg_score = calculate_risk_level(holdings)

    assert risk_level in [
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High",
    ], "Risk level should be one of the defined categories."
    assert isinstance(avg_score, float), "Average score should be a float."
    assert 0 <= avg_score <= 100, "Average score should be between 0 and 100."


def test_calculate_portfolio_volatility():
    """Test the calculation of portfolio volatility."""
    holdings = [
        {"symbol": "BTC", "allocation": 0.5, "week_change": 0.05},
        {"symbol": "ETH", "allocation": 0.3, "week_change": 0.03},
        {"symbol": "XRP", "allocation": 0.2, "week_change": 0.02},
    ]

    volatility = calculate_portfolio_volatility(holdings)

    assert isinstance(volatility, float), "Volatility should be a float."
    assert volatility >= 0, "Volatility should be non-negative."


def test_determine_risk_level():
    """Test the determine_risk_level function with various inputs."""

    # Test volatility risk levels
    volatility_low = determine_risk_level(10, "volatility")
    volatility_medium = determine_risk_level(20, "volatility")
    volatility_high = determine_risk_level(40, "volatility")

    assert volatility_low == {"level": "Low", "color": "green", "width": "40%"}
    assert volatility_medium == {"level": "Medium", "color": "yellow", "width": "65%"}
    assert volatility_high == {"level": "High", "color": "red", "width": "80%"}

    # Test diversity risk levels
    diversity_poor = determine_risk_level(3, "diversity")
    diversity_medium = determine_risk_level(5, "diversity")
    diversity_good = determine_risk_level(10, "diversity")

    assert diversity_poor == {"level": "Poor", "color": "red", "width": "35%"}
    assert diversity_medium == {"level": "Medium", "color": "yellow", "width": "60%"}
    assert diversity_good == {"level": "Good", "color": "green", "width": "74%"}

    # Test max_drawdown risk levels
    drawdown_low = determine_risk_level(10, "max_drawdown")
    drawdown_medium = determine_risk_level(20, "max_drawdown")
    drawdown_high = determine_risk_level(30, "max_drawdown")

    assert drawdown_low == {"level": "Low", "color": "green", "width": "40%"}
    assert drawdown_medium == {"level": "Medium", "color": "yellow", "width": "65%"}
    assert drawdown_high == {"level": "High", "color": "red", "width": "80%"}

    # Test sharpe_ratio risk levels
    sharpe_poor = determine_risk_level(0.3, "sharpe_ratio")
    sharpe_medium = determine_risk_level(0.7, "sharpe_ratio")
    sharpe_good = determine_risk_level(1.5, "sharpe_ratio")

    assert sharpe_poor == {"level": "Poor", "color": "red", "width": "35%"}
    assert sharpe_medium == {"level": "Medium", "color": "yellow", "width": "50%"}
    assert sharpe_good == {"level": "Good", "color": "green", "width": "68%"}

    # Test unknown metric type
    unknown = determine_risk_level(50, "unknown_metric")
    assert unknown == {"level": "Unknown", "color": "gray", "width": "50%"}
