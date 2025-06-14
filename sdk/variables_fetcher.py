"""
This module provides functions to fetch API keys and URLs from a configuration file,
load JSON data from files, calculate all-time low and high values, and save transaction data.
"""

import json
import logging
import os
from datetime import datetime, timezone

import pytz

logger = logging.getLogger(__name__)


def get_api_key(key_name):
    """
    Retrieve an API key from the config.json file.

    Args:
        key_name (str): The name of the API key to retrieve

    Returns:
        str or None: The API key if found, None otherwise
    """
    try:
        with open("./config/config.json", "r", encoding="utf-8") as file:
            logger.info("Requested API key: %s", key_name)
            config = json.load(file)
            return config["api_keys"].get(key_name.upper())
    except (FileNotFoundError, KeyError) as e:
        logger.error("Error fetching API key %s: %s", key_name, str(e))
        print(f"Error fetching API key {key_name}: {str(e)}")

        return None


def get_api_url(key_name):
    """
    Retrieve an API URL from the config.json file.

    Args:
        key_name (str): The name of the API URL to retrieve

    Returns:
        str or None: The API URL if found, None otherwise
    """
    try:
        with open("./config/config.json", "r", encoding="utf-8") as file:
            logger.info("Requested API URL: %s", key_name)
            config = json.load(file)
            return config["api_urls"].get(key_name.upper())
    except (FileNotFoundError, KeyError) as e:
        logger.error("Error fetching API URL %s: %s", key_name, str(e))
        print(f"Error fetching API URL {key_name}: {str(e)}")

        return None


def load_json_file(file_path):
    """
    Load data from a JSON file.

    Args:
        file_path (str): The file path

    Returns:
        dict: JSON file content
    """
    if not os.path.exists(file_path):
        logger.error("JSON %s not found. Using an empty JSON.", file_path)
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            portfolio = json.load(file)
            logger.info("JSON loaded from %s.", file_path)
            return portfolio
    except json.JSONDecodeError:
        logger.error("Invalid JSON file %s. Using an empty JSON.", file_path)
        return {}
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(
            "Error loading JSON from %s: %s. Using an empty JSON.", file_path, str(e)
        )
        return {}


def get_atl_ath(file_path="./config/portfolio_history.json"):
    """
    Return All-Time Low and All-Time High from the portfolio history JSON

    Args:
        file_path (str): The path to the JSON

    Returns:
        float: All-Time Low
        float All-Time High
    """
    portfolio_history = load_json_file(file_path)

    all_time_high = 0
    all_time_low = 99999999

    logger.info("Calculate portfolio All Time Low and All Time High!")

    for entry in portfolio_history:
        if entry["total_value"] > all_time_high:
            all_time_high = entry["total_value"]

        if entry["total_value"] < all_time_low:
            all_time_low = entry["total_value"]

    return round(all_time_low, 2), round(all_time_high, 2)


def save_transaction(transaction, file_path="./config/transactions.json"):
    """
    Records a transaction in the transactions file.

    Args:
        transaction (dict): Transaction data to be saved
        file_path (str): Path to the JSON file
    """
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        logger.info("Created directory for file: %s", os.path.dirname(file_path))

    transactions = load_json_file(file_path)

    if transactions is None:
        logger.error("Failed to load transactions from %s", file_path)
        return

    transactions.append(transaction)
    save_data_to_json_file(file_path, transactions)
    logger.info("Transaction saved: %s", transaction)


def save_data_to_json_file(file_path, data):
    """
    Save JSON data to a file.

    Args:
        file_path (str): Path to the JSON file
        data (dict): Data to be saved to the JSON file
    """

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        logger.info("Created directory for file: %s", os.path.dirname(file_path))

    logger.info("Saving data to JSON file: %s", file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# pylint: disable=too-many-arguments, too-many-positional-arguments
def save_new_transaction(
    symbol, amount, price, action, date=None, exchange=None, wallet=None, notes=None
):
    """
    Save a new transaction to the transactions file.
    Args:
        symbol (str): Coin symbol
        amount (float): Transaction coin amount
        price (float): Transaction price
        action (str): Transaction action ('BUY', 'SELL')
        date (str, optional): Transaction date in ISO format. Defaults to None.
        exchange (str, optional): Exchange where the transaction occurred. Defaults to None.
        wallet (str, optional): Wallet where the asset is stored. Defaults to None.
        notes (str, optional): Additional notes for the transaction. Defaults to None.
    """
    if action not in ["BUY", "SELL"]:
        logger.error("Invalid action: %s. Must be 'BUY' or 'SELL'.", action)
        raise ValueError("Action must be 'BUY' or 'SELL'.")

    if not symbol or not amount or not price:
        logger.error("Symbol, amount, and price are required fields.")
        raise ValueError("Symbol, amount, and price are required fields.")

    utc_dt = datetime.now(timezone.utc)
    if date:
        # Parse to naive datetime (assumes local time)
        naive_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M")

        local_tz = pytz.timezone("Europe/Bucharest")

        # Localize the naive datetime
        localized_dt = local_tz.localize(naive_dt)

        # Convert to UTC
        utc_dt = localized_dt.astimezone(pytz.utc)

    transaction = {
        "symbol": symbol,
        "action": action,
        "amount": round(float(amount), 6),
        "price": round(float(price), 6),
        "total": round(float(amount) * float(price), 2),
        "exchange": exchange if exchange else "Unknown",
        "wallet": wallet if wallet else "Unknown",
        "notes": notes if notes else "",
        "timestamp": utc_dt.isoformat(),
    }

    save_transaction(transaction)
    logger.info("New transaction saved: %s", transaction)
