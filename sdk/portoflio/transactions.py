import csv
import logging
from io import StringIO

from sdk.variables_fetcher import load_json_file

from datetime import datetime

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
        symbol: The symbol to filter transactions by

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
