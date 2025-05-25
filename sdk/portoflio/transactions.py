import csv
import logging
from io import StringIO

import pytz

from sdk.variables_fetcher import (
    load_json_file,
    save_transaction,
    save_new_transaction,
    save_data_to_json_file,
)

from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def load_transactions():
    """
    Load transactions from the JSON file.

    Returns:
        list: List of transaction dictionaries
    """
    transactions = load_json_file('./config/transactions.json')

    if len(transactions) == 0:
        logger.error('No transactions found in the JSON file.')
        return

    # Convert timestamps to datetime objects for sorting
    for transaction in transactions:
        transaction['datetime'] = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))

        transaction['amount'] =  f"{round(transaction['amount'], 2):,.2f}"
        transaction['price'] =  f"${round(transaction['price'], 2):,.2f}"

    # Sort transactions by date (newest first)
    transactions.sort(key=lambda x: x['datetime'], reverse=True)

    return transactions

def load_transactions_by_symbol(symbol):
    """
    Load transactions for a specific symbol.

    Args:
        symbol (str): The symbol to filter transactions by.

    Returns:
        list: List of transaction dictionaries for the specified symbol.
    """
    transactions = load_transactions()

    if transactions is None:
        logger.error('No transactions found in the JSON file.')
        return []

    # Filter transactions by symbol
    filtered_transactions = [tx for tx in transactions if tx['symbol'] == symbol]

    return filtered_transactions

def create_csv_content(symbol):
    """
    Create CSV content from transactions.

    Args:
        symbol (str): The symbol to filter transactions by

    Returns:
        str: CSV formatted string.
        str: Filename for the CSV.
    """
    try:
        # Get transactions for the symbol (or all if symbol is 'all')
        if symbol.lower() == 'all':
            transactions = load_transactions()  # Get all transactions
            filename = f"all_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            transactions = load_transactions_by_symbol(symbol)
            filename = f"{symbol}_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Date', 'Time', 'Action', 'Symbol', 'Amount', 'Price', 'Total', 'Status'])

        # Write transaction data
        for tx in transactions:
            writer.writerow([
                tx['datetime'].strftime('%Y-%m-%d'),
                tx['datetime'].strftime('%H:%M:%S'),
                tx['action'],
                tx['symbol'],
                tx['amount'],
                tx['price'],
                tx['total'],
                'Completed'
            ])

        output.seek(0)

        return output.getvalue(), filename
    except Exception as e:
        logger.error(f"Error creating CSV content: {e}")

        return None, 'transactions.csv'

def update_buy(symbol, amount, price, date=None, exchange=None, wallet=None, notes=None):
    """
    Handles buying a cryptocurrency and updating the portfolio correctly.

    Args:
        symbol (str): Coin symbol
        amount (float): Transaction coin amount
        price (float): Transaction price
        date (str, optional): Transaction date in ISO format. Defaults to None.
        exchange (str, optional): Exchange where the transaction occurred. Defaults to None.
        wallet (str, optional): Wallet where the asset is stored. Defaults to None.
        notes (str, optional): Additional notes for the transaction. Defaults to None.
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

    save_new_transaction(symbol, amount, price, 'BUY', date, exchange, wallet, notes)


def update_sell(symbol, amount, price, date=None, exchange=None, wallet=None, notes=None):
    """
    Handles selling a cryptocurrency, updating portfolio, and adding USDT balance.
    Args:
        symbol (str): Coin symbol
        amount (float): Transaction coin amount
        price (float): Transaction price
        date (str, optional): Transaction date in ISO format. Defaults to None.
        exchange (str, optional): Exchange where the transaction occurred. Defaults to None.
        wallet (str, optional): Wallet where the asset is stored. Defaults to None.
        notes (str, optional): Additional notes for the transaction. Defaults to None.
    """
    portfolio = load_json_file('./config/portfolio.json')

    if not portfolio:
        return False

    if symbol in portfolio:
        current_quantity = portfolio[symbol]["quantity"]
        current_avg_price = portfolio[symbol]["average_price"]
        current_total_investment = portfolio[symbol]["total_investment"]

        # Weighted average price calculation
        new_quantity = current_quantity - amount
    else:
        return False

    portfolio[symbol] = {
        "quantity": round(new_quantity, 6),
        "average_price": round(current_avg_price, 6),
        "total_investment": round(current_total_investment, 2),
        "allocation_percentage": None  # To be calculated later
    }
    save_data_to_json_file('./config/portfolio.json', portfolio)

    save_new_transaction(symbol, amount, price, 'SELL', date, exchange, wallet, notes)
