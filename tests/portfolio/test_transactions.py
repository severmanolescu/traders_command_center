"""
Test cases for portfolio transactions module.
"""

import json
from unittest.mock import patch

from src.portfolio.transactions import (
    create_csv_content,
    load_transactions,
    load_transactions_by_symbol,
    update_buy,
    update_sell,
)


def test_load_transactions():
    """Test loading transactions from the JSON file."""
    transactions = load_transactions()
    assert isinstance(transactions, list)
    assert len(transactions) == 0, "Should return a empty list of transactions"


def test_load_transactions_mock_data():
    """Test loading transaction data from file."""
    mock_transactions = [
        {
            "timestamp": "2023-01-15T12:00:00Z",
            "action": "BUY",
            "symbol": "BTC",
            "price": 35000,
            "amount": 0.1,
            "total": 3500,
        },
        {
            "timestamp": "2023-02-20T12:00:00Z",
            "action": "SELL",
            "symbol": "ETH",
            "price": 2200,
            "amount": 2,
            "total": 4400,
        },
    ]

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        mock_load_json.return_value = mock_transactions

        transactions = load_transactions()

        assert len(transactions) == 2, "Should load 2 transactions"
        assert (
            transactions[0]["symbol"] == "ETH"
        ), "First transaction should be ETH (newest)"
        assert transactions[0]["action"] == "SELL", "First transaction should be SELL"
        assert transactions[1]["symbol"] == "BTC", "Second transaction should be BTC"

        # Check formatting
        assert transactions[0]["amount"] == "2.00", "Amount should be formatted"
        assert transactions[0]["price"] == "$2,200.00", "Price should be formatted"

        assert (
            transactions[0]["datetime"] > transactions[1]["datetime"]
        ), "Transactions should be sorted newest first"

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        mock_load_json.return_value = []
        transactions = load_transactions()
        assert transactions == [], "Should return empty list when no transactions exist"


def test_load_transactions_by_symbol():
    """Test loading transactions by symbol."""
    transactions = load_transactions_by_symbol("ETH")
    assert isinstance(transactions, list)
    assert len(transactions) == 0, "Should return a empty list of transactions"


def test_load_transactions_by_symbol_mock_data():
    """Test loading transactions by symbol."""
    mock_transactions = [
        {
            "timestamp": "2023-01-15T12:00:00Z",
            "action": "BUY",
            "symbol": "BTC",
            "price": 35000,
            "amount": 0.1,
            "total": 3500,
        },
        {
            "timestamp": "2023-02-20T12:00:00Z",
            "action": "SELL",
            "symbol": "ETH",
            "price": 2200,
            "amount": 2,
            "total": 4400,
        },
    ]

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        # Use a deep copy for each test to avoid data mutation between tests
        mock_load_json.return_value = json.loads(json.dumps(mock_transactions))

        btc_transactions = load_transactions_by_symbol("BTC")
        assert len(btc_transactions) == 1, "Should return 1 BTC transaction"
        assert (
            btc_transactions[0]["symbol"] == "BTC"
        ), "BTC transaction should be returned"

    # Create a new patch for each symbol test to ensure fresh data
    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        mock_load_json.return_value = json.loads(json.dumps(mock_transactions))

        eth_transactions = load_transactions_by_symbol("ETH")
        assert len(eth_transactions) == 1, "Should return 1 ETH transaction"
        assert (
            eth_transactions[0]["symbol"] == "ETH"
        ), "ETH transaction should be returned"

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        mock_load_json.return_value = json.loads(json.dumps(mock_transactions))

        xrp_transactions = load_transactions_by_symbol("XRP")
        assert len(xrp_transactions) == 0, "Should return empty list for unknown symbol"


def test_create_csv_content():
    """Test creating CSV content from transactions."""
    mock_transactions = [
        {
            "timestamp": "2023-01-15T12:00:00Z",
            "action": "BUY",
            "symbol": "BTC",
            "price": 35000,
            "amount": 0.1,
            "total": 3500,
        },
        {
            "timestamp": "2023-02-20T12:00:00Z",
            "action": "SELL",
            "symbol": "ETH",
            "price": 2200,
            "amount": 2,
            "total": 4400,
        },
    ]

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json:
        mock_load_json.return_value = json.loads(json.dumps(mock_transactions))

        csv_content = create_csv_content("BTC")
        assert csv_content, print("CSV content should not be empty")
        assert (
            '2023-01-15,12:00:00,BUY,BTC,0.10,"$35,000.00",3500,Completed'
            in csv_content[0]
        ), "CSV should contain BTC transaction"


def test_update_buy_updates_portfolio_and_saves_transaction():
    """
    Test updating portfolio with a buy transaction.
    """
    mock_portfolio = {
        "BTC": {
            "quantity": 1.0,
            "average_price": 30000.0,
            "total_investment": 30000.0,
            "allocation_percentage": 50.0,
        }
    }

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json, patch(
        "src.portfolio.transactions.save_data_to_json_file"
    ) as mock_save_json, patch(
        "src.portfolio.transactions.save_new_transaction"
    ) as mock_save_tx:

        mock_load_json.return_value = mock_portfolio.copy()

        update_buy("BTC", 0.5, 35000.0, date="2023-03-01T12:00:00Z")

        # Check that the portfolio was updated and saved
        assert mock_save_json.called
        saved_portfolio = mock_save_json.call_args[0][1]
        assert "BTC" in saved_portfolio
        assert saved_portfolio["BTC"]["quantity"] == 1.5
        assert saved_portfolio["BTC"]["average_price"] != 30000.0  # Should be updated

        # Check that the transaction was saved
        mock_save_tx.assert_called_with(
            "BTC", 0.5, 35000.0, "BUY", "2023-03-01T12:00:00Z", None, None, None
        )


def test_update_sell_updates_portfolio_and_saves_transaction():
    """
    Test updating portfolio with a sell transaction.
    """
    mock_portfolio = {
        "BTC": {
            "quantity": 1.0,
            "average_price": 30000.0,
            "total_investment": 30000.0,
            "allocation_percentage": 50.0,
        }
    }

    with patch("src.portfolio.transactions.load_json_file") as mock_load_json, patch(
        "src.portfolio.transactions.save_data_to_json_file"
    ) as mock_save_json, patch(
        "src.portfolio.transactions.save_new_transaction"
    ) as mock_save_tx:

        mock_load_json.return_value = mock_portfolio.copy()

        update_sell("BTC", 0.5, 35000.0, date="2023-03-01T12:00:00Z")

        # Check that the portfolio was updated and saved
        assert mock_save_json.called
        saved_portfolio = mock_save_json.call_args[0][1]
        assert "BTC" in saved_portfolio
        assert saved_portfolio["BTC"]["quantity"] == 0.5  # 1.0 - 0.5

        # Check that the transaction was saved
        mock_save_tx.assert_called_with(
            "BTC", 0.5, 35000.0, "SELL", "2023-03-01T12:00:00Z", None, None, None
        )
