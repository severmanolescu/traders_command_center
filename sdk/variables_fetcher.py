import os
import json
import logging
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
        with open("./config/config.json", 'r') as file:
            logger.info(f'Requested API key: {key_name}')
            config = json.load(file)
            return config['api_keys'].get(key_name.upper())
    except (FileNotFoundError, KeyError) as e:
        logger.error(f"Error fetching API key {key_name}: {str(e)}")
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
        with open("./config/config.json", 'r') as file:
            logger.info(f'Requested API URL: {key_name}')
            config = json.load(file)
            return config['api_urls'].get(key_name.upper())
    except (FileNotFoundError, KeyError) as e:
        logger.error(f"Error fetching API URL {key_name}: {str(e)}")
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
        logger.error(f"JSON '{file_path}' not found. Using an empty JSON.")
        return {}

    try:
        with open(file_path, "r") as file:
            portfolio = json.load(file)
            logger.info(f"JSON loaded from '{file_path}'.")
            return portfolio
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON file '{file_path}'. Using an empty JSON.")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON from '{file_path}': {e}. Using an empty JSON.")
        return {}

def get_atl_ath(file_path='./config/portfolio_history.json'):
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
        if entry['total_value'] > all_time_high:
            all_time_high = entry['total_value']

        if entry['total_value'] < all_time_low:
            all_time_low = entry['total_value']

    return round(all_time_low, 2), round(all_time_high, 2)

def save_transaction(transaction, file_path='./config/transactions.json'):
    """
    Records a transaction in the transactions file.

    Args:
        transaction (dict): Transaction data to be saved
        file_path (str): Path to the JSON file
    """
    transactions = load_json_file(file_path)

    if transactions is None:
        return

    transactions.append(transaction)
    save_data_to_json_file(file_path, transactions)


def save_data_to_json_file(file_path, data):
    """
    Save JSON data to a file.

    Args:
        file_path (str): Path to the JSON file
        data (dict): Data to be saved to the JSON file
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def save_new_transaction(symbol, amount, price, action, date=None, exchange=None, wallet=None, notes=None):
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
    utc_dt = datetime.now(timezone.utc)
    if date:
        # Parse to naive datetime (assumes local time)
        naive_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M")

        local_tz = pytz.timezone('Europe/Bucharest')

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
        "timestamp": utc_dt.isoformat() ,
    }

    save_transaction(transaction)
