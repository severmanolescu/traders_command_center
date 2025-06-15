"""
Test cases for portfolio analytics functions.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from src.portfolio.analytics import (
    calculate_changes_from_history,
    calculate_diversity_score,
    calculate_metrics_from_portfolio_history,
    calculate_profit_loss,
    default_changes,
    get_change_for_period,
    load_and_normalize_history,
)


def test_calculate_profit_loss():
    """
    Test the profit and loss calculation.
    """
    result = calculate_profit_loss(1000, 1200)
    assert result["amount"] == -200, "Profit/Loss amount calculation is incorrect."
    assert (
        result["percentage"] == -16.67
    ), "Profit/Loss percentage calculation is incorrect."


def test_load_and_normalize_history():
    """
    Test loading and normalizing historical data.
    """
    history = load_and_normalize_history("./config/portfolio_history.json")
    assert isinstance(history, list), "History should be a list."
    assert len(history) == 0, "History should be empty."


def test_get_change_for_period():
    """Test calculating portfolio change for a specific time period"""
    # Create test data
    current_time = datetime(2023, 1, 5, 12, 0, 0)
    current_value = 1200
    history = [
        {"parsed_datetime": datetime(2023, 1, 5, 12, 0, 0), "total_value": 1200},
        {"parsed_datetime": datetime(2023, 1, 4, 12, 0, 0), "total_value": 1100},
        {"parsed_datetime": datetime(2023, 1, 1, 12, 0, 0), "total_value": 1000},
    ]

    # Test 1-day change
    one_day_delta = timedelta(days=1)
    one_day_change = get_change_for_period(
        history, current_value, current_time, one_day_delta
    )
    assert one_day_change["amount"] == "$100.00"
    assert one_day_change["percentage"] == "9.09%"
    assert one_day_change["is_positive"] is True

    # Test 4-day change
    four_day_delta = timedelta(days=4)
    four_day_change = get_change_for_period(
        history, current_value, current_time, four_day_delta
    )
    assert four_day_change["amount"] == "$200.00"
    assert four_day_change["percentage"] == "20.00%"
    assert four_day_change["is_positive"] is True

    # Test when no close entry exists (more than 1 day difference)
    seven_day_delta = timedelta(days=7)
    seven_day_change = get_change_for_period(
        history, current_value, current_time, seven_day_delta
    )
    assert seven_day_change["amount"] == 0
    assert seven_day_change["percentage"] == 0
    assert seven_day_change["is_positive"] is True

    # Test with empty history
    empty_history = []
    empty_change = get_change_for_period(
        empty_history, current_value, current_time, one_day_delta
    )
    assert empty_change["amount"] == 0
    assert empty_change["percentage"] == 0
    assert empty_change["is_positive"] is True


def test_calculate_changes_from_history():
    """Test the calculation of changes from historical data."""
    # Create mock history data
    mock_history = [
        {"parsed_datetime": datetime(2023, 1, 10), "total_value": 1200},
        {"parsed_datetime": datetime(2023, 1, 9), "total_value": 1150},
        {
            "parsed_datetime": datetime(2023, 1, 3),
            "total_value": 1000,
        },  # 7 days from the first entry
        {"parsed_datetime": datetime(2023, 1, 1), "total_value": 900},
    ]

    # Mock the load_and_normalize_history function to return our test data
    with patch(
        "src.portfolio.analytics.load_and_normalize_history", return_value=mock_history
    ):
        changes = calculate_changes_from_history()

        # Verify the changes for each time period
        assert changes["24h"]["amount"] == "$50.00"
        assert changes["24h"]["percentage"] == "4.35%"
        assert changes["24h"]["is_positive"] is True

        assert changes["7d"]["amount"] == "$200.00"
        assert changes["7d"]["percentage"] == "20.00%"
        assert changes["7d"]["is_positive"] is True

        # For 30d, there's no data point 30 days ago, so it should return default values
        assert changes["30d"]["amount"] == 0
        assert changes["30d"]["percentage"] == 0
        assert changes["30d"]["is_positive"] is True


def test_calculate_changes_from_empty_history():
    """Test that default changes are returned when history is empty."""
    # Mock empty history
    with patch("src.portfolio.analytics.load_and_normalize_history", return_value=[]):
        changes = calculate_changes_from_history()
        default = default_changes()

        # Verify that default changes are returned
        assert changes == default
        assert changes["24h"]["amount"] == 0
        assert changes["7d"]["amount"] == 0
        assert changes["30d"]["amount"] == 0


def test_default_changes():
    """Test the default changes function."""
    changes = default_changes()
    assert changes["24h"]["amount"] == 0
    assert changes["24h"]["percentage"] == 0
    assert changes["24h"]["is_positive"] is True

    assert changes["7d"]["amount"] == 0
    assert changes["7d"]["percentage"] == 0
    assert changes["7d"]["is_positive"] is True

    assert changes["30d"]["amount"] == 0
    assert changes["30d"]["percentage"] == 0
    assert changes["30d"]["is_positive"] is True


def test_calculate_diversity_score():
    """Test the diversity score calculation."""
    # Create mock portfolio data
    mock_portfolio = [
        {"symbol": "BTC", "allocation": 50},
        {"symbol": "ETH", "allocation": 30},
        {"symbol": "XRP", "allocation": 20},
    ]

    # Calculate diversity score
    diversity_score = calculate_diversity_score(mock_portfolio)

    # Verify the score is calculated correctly
    assert isinstance(diversity_score, float), "Diversity score should be a float."
    assert 0 <= diversity_score <= 100, "Diversity score should be between 0 and 100."


def test_calculate_metrics_from_portfolio_history_empty_data():
    """Test metrics calculation with empty portfolio history."""
    # Mock empty portfolio history
    with patch("src.portfolio.analytics.load_json_file", return_value=[]):
        max_drawdown, sharpe_ratio = calculate_metrics_from_portfolio_history()

        # Verify that the function handles empty data properly
        assert max_drawdown == 0, "Max drawdown should be 0 for empty history"
        assert sharpe_ratio == 0, "Sharpe ratio should be 0 for empty history"
