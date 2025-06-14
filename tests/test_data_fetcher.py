"""
Tests for the variables_fetcher module.
"""

import os

from src.variables_fetcher import (
    get_api_key,
    get_api_url,
    get_atl_ath,
    load_json_file,
    save_data_to_json_file,
    save_new_transaction,
    save_transaction,
)


def test_get_api_key():
    """
    Test the retrieval of API keys from the configuration file.
    """
    # Test with a valid key
    key = get_api_key("CMC_API_KEY")
    assert key is not None, "API key should not be None"
    assert key == "", "API key should be an empty string"

    # Test with an invalid key
    invalid_key = get_api_key("INVALID_KEY")
    assert invalid_key is None, "Invalid API key should return None"


def test_get_api_url():
    """
    Test the retrieval of API URLs from the configuration file.
    """
    # Test with a valid URL key
    url = get_api_url("CMC_API_URL")
    assert url is not None, "API URL should not be None"
    assert url != "", "API key should be an empty string"

    # Test with an invalid URL key
    invalid_url = get_api_url("INVALID_URL")
    assert invalid_url is None, "Invalid API URL should return None"


def test_load_json_file():
    """
    Test the loading of JSON files.
    """
    # Test with a valid JSON file
    data = load_json_file("./config/config.json")
    assert isinstance(data, dict), "Loaded data should be a dictionary"
    assert "api_keys" in data, "JSON should contain 'api_keys' key"
    assert "api_urls" in data, "JSON should contain 'api_urls' key"

    # Test with a non-existent file
    empty_data = load_json_file("./config/non_existent.json")
    assert empty_data == [], "Loading a non-existent file should return an empty dict"

    # Test with an invalid JSON file
    invalid_data = load_json_file("./config/invalid.json")
    assert (
        invalid_data == []
    ), "Loading an invalid JSON file should return an empty dict"


def test_get_atl_ath():
    """
    Test the retrieval of All-Time Low (ATL) and All-Time High (ATH) values for a cryptocurrency.
    """
    # Test with a valid symbol
    atl, ath = get_atl_ath("BTC")
    assert atl is not None, "ATL should not be None"
    assert ath is not None, "ATH should not be None"
    assert isinstance(atl, float), "ATL should be a float"
    assert isinstance(ath, float), "ATH should be a float"

    # Test with an invalid symbol
    invalid_atl, invalid_ath = get_atl_ath("INVALID")
    assert invalid_atl == 99999999.9, "Invalid symbol ATL should be 99999999.9"
    assert invalid_ath == 0.0, "Invalid symbol ATH should be 0.0"


def test_save_data_to_json_file():
    """
    Test saving data to a JSON file.
    """
    data = {"key": "value"}
    file_path = "./tests/test_files/test_save.json"

    # Save data to JSON file
    save_data_to_json_file(file_path, data)

    # Load the saved data
    loaded_data = load_json_file(file_path)
    assert loaded_data == data, "Saved data should match loaded data"

    os.remove(file_path)


def test_save_transaction():
    """
    Test saving a new transaction to the transactions file.
    """
    transaction = {
        "symbol": "BTC",
        "amount": 0.01,
        "action": "buy",
        "price": 50000,
        "timestamp": "2023-10-01T12:00:00Z",
    }
    file_path = "./tests/test_files/test_transactions.json"

    # Save the transaction
    save_transaction(transaction, file_path)

    # Load the saved transactions
    transactions = load_json_file(file_path)
    assert isinstance(transactions, list), "Transactions should be a list"
    assert len(transactions) > 0, "There should be at least one transaction"
    assert (
        transactions[-1] == transaction
    ), "Last transaction should match the saved transaction"

    os.remove(file_path)


def test_save_new_transaction():
    """
    Test saving a new transaction to the transactions file.
    """
    file_path = "./tests/test_files/test_new_transactions.json"

    # Save the new transaction
    save_new_transaction(
        symbol="ETH", amount=0.5, price=3000, action="buy", file_path=file_path
    )

    # Load the saved transactions
    transactions = load_json_file(file_path)
    assert isinstance(transactions, list), "Transactions should be a list"
    assert len(transactions) > 0, "There should be at least one transaction"

    os.remove(file_path)
