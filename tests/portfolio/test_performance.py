"""
Test for portfolio performance calculations and categorization.
"""

import json
from datetime import datetime
from unittest.mock import patch

from src.portoflio.performance import (
    categorize_history_by_time,
    get_portfolio_performance,
    sort_chart_data,
)


def test_categorize_history_by_time():
    """Test the categorization of portfolio history by time periods."""
    # Mock portfolio history data
    mock_history = [
        {
            "datetime": "2025-02-03 00:28:06",
            "total_value": 1000,
            "total_investment": 800,
            "profit_loss": 200,
            "profit_loss_percentage": 25,
        },
        {
            "datetime": "2025-03-10 00:28:06",
            "total_value": 950,
            "total_investment": 800,
            "profit_loss": 150,
            "profit_loss_percentage": 18.75,
        },
        {
            "datetime": "2025-03-20 00:28:06",
            "total_value": 900,
            "total_investment": 800,
            "profit_loss": 100,
            "profit_loss_percentage": 12.5,
        },
    ]

    categorized_data = categorize_history_by_time(
        mock_history, datetime(2025, 3, 22, 12, 0, 0)
    )

    assert len(categorized_data["All"]) == 3, "All data should have 3 entries."
    assert len(categorized_data["1Y"]) == 3, "1Y data should have 3 entries."
    assert len(categorized_data["3M"]) == 3, "3M data should have 3 entries."
    assert len(categorized_data["1M"]) == 2, "1M data should have 2 entries."
    assert len(categorized_data["1W"]) == 1, "1W data should have 1 entry."
    assert len(categorized_data["1D"]) == 0, "1D data should have no entries."


def test_sort_chart_data():
    """Test the sorting of chart data by timestamp."""
    # Mock chart data
    mock_chart_data = {
        "1D": [
            {"x": 1706820486000, "total_value": 1000},
            {"x": 1706906886000, "total_value": 950},
        ],
        "1W": [
            {"x": 1706734086000, "total_value": 900},
            {"x": 1706820486000, "total_value": 1000},
        ],
    }

    sorted_data = sort_chart_data(mock_chart_data)

    assert (
        sorted_data["1D"][0]["x"] < sorted_data["1D"][1]["x"]
    ), "1D data should be sorted by timestamp."
    assert (
        sorted_data["1W"][0]["x"] < sorted_data["1W"][1]["x"]
    ), "1W data should be sorted by timestamp."


def test_get_portfolio_performance():
    """Test portfolio performance data generation."""
    # Mock data for transactions and portfolio history
    mock_transactions = [
        {"date": "2023-01-01", "type": "buy", "symbol": "BTC", "amount": 0.1},
        {"date": "2023-02-15", "type": "sell", "symbol": "ETH", "amount": 1.0},
    ]

    mock_portfolio_history = [
        {
            "datetime": "2023-01-01 12:00:00",
            "total_value": 10000,
            "total_investment": 9000,
            "profit_loss": 1000,
            "profit_loss_percentage": 11.11,
        },
        {
            "datetime": "2023-01-15 12:00:00",
            "total_value": 11000,
            "total_investment": 9000,
            "profit_loss": 2000,
            "profit_loss_percentage": 22.22,
        },
        {
            "datetime": "2023-03-01 12:00:00",
            "total_value": 12000,
            "total_investment": 9500,
            "profit_loss": 2500,
            "profit_loss_percentage": 26.32,
        },
    ]

    # Apply patches to mock file loading
    with patch("src.portoflio.performance.load_json_file") as mock_load_json, patch(
        "src.portoflio.performance.datetime"
    ) as mock_datetime:

        # Configure mocks
        mock_load_json.side_effect = lambda path: (
            mock_transactions if "transactions.json" in path else mock_portfolio_history
        )

        # Mock current date to March 10, 2023
        mock_now = datetime(2023, 3, 10)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime = datetime.strptime

        # Call the function
        transactions, chart_data_json = get_portfolio_performance()

        # Verify results
        assert transactions == mock_transactions, "Should return the mock transactions"

        # Parse the JSON string
        chart_data = json.loads(chart_data_json)

        # Verify structure
        assert set(chart_data.keys()) == {
            "1D",
            "1W",
            "1M",
            "3M",
            "1Y",
            "All",
        }, "Should have all time periods"

        # Verify categorization
        assert len(chart_data["All"]) == 3, "All should contain all 3 entries"
        assert (
            len(chart_data["1Y"]) == 3
        ), "1Y should contain all 3 entries (all within a year)"
        assert len(chart_data["3M"]) >= 1, "3M should contain at least the March entry"

        # Verify sorting
        for period in chart_data:
            timestamps = [point["x"] for point in chart_data[period]]
            assert timestamps == sorted(
                timestamps
            ), f"Data points in {period} should be sorted by timestamp"

        # Verify data point structure for one example
        if chart_data["All"]:
            data_point = chart_data["All"][0]
            assert "x" in data_point, "Data point should have timestamp"
            assert "total_value" in data_point, "Data point should have total value"
            assert (
                "total_investment" in data_point
            ), "Data point should have total investment"
            assert "profit_loss" in data_point, "Data point should have profit/loss"
            assert (
                "profit_loss_percentage" in data_point
            ), "Data point should have profit/loss percentage"
