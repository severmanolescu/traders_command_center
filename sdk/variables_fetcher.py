import os
import json

from sdk.logger import setup_logger

logger = setup_logger('variables_fetcher.log ')

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
        logger.error(f"Portfolio file '{file_path}' not found. Using an empty portfolio.")
        return {}

    try:
        with open(file_path, "r") as file:
            portfolio = json.load(file)
            logger.info(f"Portfolio loaded from '{file_path}'.")
            return portfolio
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in portfolio file '{file_path}'. Using an empty portfolio.")
        return {}
    except Exception as e:
        logger.error(f"Error loading portfolio from '{file_path}': {e}. Using an empty portfolio.")
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

    for entry in portfolio_history:
        if entry['total_value'] > all_time_high:
            all_time_high = entry['total_value']

        if entry['total_value'] < all_time_low:
            all_time_low = entry['total_value']

    return round(all_time_low, 2), round(all_time_high, 2)