import os
import json
import logging

from datetime import datetime, timezone

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
            return config['api_keys'].get(key_name.lower())
    except (FileNotFoundError, KeyError) as e:
        logger.error(f"Error fetching API key {key_name}: {str(e)}")

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
    Return All Time Low and All Time High from the portfolio history JSON

    Args:
        file_path (str): The path to the JSON

    Returns:
        float: All Time Low
        float All Time High
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

def save_transaction(symbol, action, amount, price, file_path='./config/transactions.json'):
    """
    Records a transaction in the transactions file.

    Args:
        symbol (str): Coin symbol
        action (str): Buy or Sell
        amount (float): Transaction coin amount
        price (float): Transaction price
        file_path (str): Path to the JSON file
    """
    transactions = load_json_file(file_path)

    if transactions is None:
        return

    transaction = {
        "symbol": symbol,
        "action": action.upper(),
        "amount": round(float(amount), 6),
        "price": round(float(price), 6),
        "total": round(float(amount) * float(price), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
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

def update_buy(symbol, amount, price):
    """
    Handles buying a cryptocurrency and updating the portfolio correctly.

    Args:
        symbol (str): Coin symbol
        amount (float): Transaction coin amount
        price (float): Transaction price
    """
    portfolio = load_json_file('./config/portfolio.json')

    if not portfolio:
        return

    if symbol in portfolio:
        current_quantity = portfolio[symbol]["quantity"]
        current_avg_price = portfolio[symbol]["average_price"]
        current_total_investment = portfolio[symbol]["total_investment"]

        # Weighted average price calculation
        new_quantity = current_quantity + amount
        new_avg_price = ((current_quantity * current_avg_price) + (amount * price)) / new_quantity
        new_total_investment = current_total_investment + (amount * price)
    else:
        # If it's a new asset, initialize with all required fields
        new_quantity = amount
        new_avg_price = price
        new_total_investment = round(amount * price, 2)

    portfolio[symbol] = {
        "quantity": round(new_quantity, 6),
        "average_price": round(new_avg_price, 6),
        "total_investment": round(new_total_investment, 2),
        "allocation_percentage": None  # To be calculated later
    }

    save_data_to_json_file('./config/portfolio.json', portfolio)
    save_transaction(symbol, 'Buy', amount, price)
