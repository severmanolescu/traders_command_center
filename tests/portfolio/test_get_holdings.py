"""
Test for the get_holdings function in the portfolio module.
"""

from unittest.mock import patch

from src.portfolio.holdings import get_holdings


def test_get_holdings():
    """Test retrieving portfolio holdings data."""
    # Mock portfolio.json data
    mock_portfolio = {
        "BTC": {"quantity": 0.5, "average_price": 30000, "total_investment": 15000},
        "ETH": {"quantity": 5, "average_price": 2000, "total_investment": 10000},
        "last_update": "2023-05-01T12:00:00Z",
    }

    # Mock API response from CoinMarketCap
    mock_api_data = {
        "data": {
            "BTC": {
                "name": "Bitcoin",
                "quote": {
                    "USD": {
                        "price": 40000,
                        "percent_change_24h": 5.2,
                        "percent_change_7d": 10.5,
                    }
                },
            },
            "ETH": {
                "name": "Ethereum",
                "quote": {
                    "USD": {
                        "price": 2500,
                        "percent_change_24h": 3.1,
                        "percent_change_7d": 7.8,
                    }
                },
            },
        }
    }

    # Mock coin mappings
    mock_coin_mappings = {
        "BTC": {"name": "bitcoin", "color": "#F7931A", "icon": "bitcoin.svg"},
        "ETH": {"name": "ethereum", "color": "#627EEA", "icon": "ethereum.svg"},
    }

    # Apply patches
    with patch("src.portfolio.holdings.load_json_file") as mock_load_json, patch(
        "src.portfolio.holdings.get_crypto_data_by_symbols"
    ) as mock_get_crypto:
        # Configure mocks
        mock_load_json.side_effect = lambda path: (
            mock_portfolio if "portfolio.json" in path else mock_coin_mappings
        )
        mock_get_crypto.return_value = mock_api_data

        # Call the function
        holdings, current_value, initial_investment = get_holdings()

        # Verify results
        assert len(holdings) == 2, "Should return two holdings"
        assert current_value == 32500, "Total value should be $32,500"
        assert initial_investment == 25000, "Initial investment should be $25,000"

        # Check BTC details
        btc = next(h for h in holdings if h["symbol"] == "BTC")
        assert btc["asset"] == "Bitcoin"
        assert btc["holdings"] == 0.5
        assert btc["avg_price"] == 30000
        assert btc["current_price"] == 40000
        assert btc["value"] == 20000
        assert btc["pnl_amount"] == 5000
        assert btc["pnl_percentage"] == 33.33333333333333
        assert btc["allocation"] == 61.54
        assert btc["coin_info"]["name"] == "bitcoin"

        # Check ETH details
        eth = next(h for h in holdings if h["symbol"] == "ETH")
        assert eth["asset"] == "Ethereum"
        assert eth["holdings"] == 5
        assert eth["avg_price"] == 2000
        assert eth["current_price"] == 2500
        assert eth["value"] == 12500
        assert eth["pnl_amount"] == 2500
        assert eth["pnl_percentage"] == 25
        assert eth["allocation"] == 38.46


def test_get_holdings_empty_api_response():
    """Test handling of empty API response."""
    # Mock portfolio.json data
    mock_portfolio = {
        "BTC": {"quantity": 0.5, "average_price": 30000, "total_investment": 15000},
        "last_update": "2023-05-01T12:00:00Z",
    }

    # Apply patches
    with patch("src.portfolio.holdings.load_json_file") as mock_load_json, patch(
        "src.portfolio.holdings.get_crypto_data_by_symbols"
    ) as mock_get_crypto:
        # Configure mocks to simulate API failure
        mock_load_json.return_value = mock_portfolio
        mock_get_crypto.return_value = None

        # Call the function
        holdings, current_value, initial_investment = get_holdings()

        # Verify results
        assert not holdings, "Should return empty holdings list"
        assert current_value == 0, "Total value should be 0"
        assert initial_investment == 0, "Initial investment should be 0"
