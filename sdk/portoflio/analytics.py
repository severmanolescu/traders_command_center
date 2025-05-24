import logging

import numpy as np
import pandas as pd

from datetime import datetime, timedelta

from sdk.portoflio.holdings import get_holdings
from sdk.portoflio.transactions import load_transactions
from sdk.variables_fetcher import load_json_file, get_atl_ath
from sdk.portoflio.performance import get_portfolio_performance
from sdk.portoflio.risk import calculate_risk_level, calculate_portfolio_volatility, determine_risk_level

logger = logging.getLogger(__name__)


def calculate_profit_loss(current_value, initial_investment):
    """
    Calculate profit/loss metrics.

    Args:
        current_value (float): Current total value of the portfolio
        initial_investment (float): Initial investment amount

    Returns:
        dict: Dictionary containing P/L metrics
    """
    # Calculate P/L amount
    pnl_amount = current_value - initial_investment

    # Calculate P/L percentage
    if initial_investment > 0:
        pnl_percentage = (pnl_amount / initial_investment) * 100
    else:
        pnl_percentage = 0

    return {
        'amount': round(pnl_amount, 2),
        'percentage': round(pnl_percentage, 2)
    }

def calculate_changes_from_history():
    """
    Calculate portfolio changes using portfolio_history.json.

    Returns:
        dict: Portfolio changes for different time periods
    """
    history = load_json_file('./config/portfolio_history.json')

    # Check if history is a list or has a list inside
    if isinstance(history, dict) and 'history' in history:
        history = history['history']
    elif not isinstance(history, list):
        logger.error("Invalid history format")
        return default_changes()

    # Ensure history has entries
    if not history:
        return default_changes()

    # Parse datetimes and sort by date (newest first)
    for entry in history:
        if 'datetime' in entry:
            try:
                entry['parsed_datetime'] = datetime.strptime(entry['datetime'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                logger.error(f"Invalid datetime format: {entry['datetime']}")
                entry['parsed_datetime'] = datetime.now()  # Default to now

    # Sort by datetime (newest first)
    history.sort(key=lambda x: x.get('parsed_datetime', datetime.min), reverse=True)

    # Get current value from most recent entry
    current_entry = history[0]
    current_value = current_entry['total_value']
    current_time = current_entry['parsed_datetime']

    # Define time periods
    time_periods = {
        '24h': timedelta(days=1),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30)
    }

    changes = {}

    # For each time period, find the closest historical entry
    for period_name, time_delta in time_periods.items():
        target_time = current_time - time_delta

        # Find the closest entry to the target time
        closest_entry = None
        min_time_diff = float('inf')

        for entry in history:
            if 'parsed_datetime' not in entry:
                continue

            entry_time = entry['parsed_datetime']
            time_diff = abs((entry_time - target_time).total_seconds())

            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_entry = entry

        # If we found a reasonably close entry (within 1 day of target)
        if closest_entry and min_time_diff <= 86400:
            past_value = closest_entry['total_value']

            # Calculate change
            change_amount = current_value - past_value
            change_percentage = (change_amount / past_value * 100) if past_value else 0

            changes[period_name] = {
                'amount': f"${round(change_amount, 2):,.2f}",
                'percentage': f"{round(change_percentage, 2):,.2f}%",
                'is_positive': change_amount >= 0
            }
        else:
            # If no suitable entry found, set to 0
            changes[period_name] = {
                'amount': 0,
                'percentage': 0,
                'is_positive': True
            }

    return changes


def default_changes():
    """Return default changes when no data is available"""
    return {
        '24h': {'amount': 0, 'percentage': 0, 'is_positive': True},
        '7d': {'amount': 0, 'percentage': 0, 'is_positive': True},
        '30d': {'amount': 0, 'percentage': 0, 'is_positive': True}
    }


def calculate_diversity_score(holdings, max_score=10):
    """
    Calculate portfolio diversity score on a scale of 0 to max_score.
    Higher score means better diversification.

    Args:
        holdings (list): List of holding dictionaries
        max_score (int): Maximum score value (default: 10)

    Returns:
        float: Diversity score from 0 to max_score
    """
    if not holdings:
        return 0

    # Get allocation percentages
    allocations = []

    for h in holdings:
        allocations.append(h['percentage'])

    # Calculate Herfindahl-Hirschman Index (HHI) - a measure of concentration
    # HHI is the sum of squared percentages (lower is more diverse)
    hhi = sum([(alloc / 100) ** 2 for alloc in allocations])

    # Normalize HHI to [0, 1] range
    # Perfect diversity (equal allocation): HHI = 1/n (n = number of assets)
    # Worst diversity (one asset = 100%): HHI = 1
    n = len(holdings)
    min_hhi = 1 / n  # Theoretical minimum HHI (perfect diversity)
    normalized_hhi = (1 - hhi) / (1 - min_hhi) if n > 1 else 0

    # Convert to score from 0 to max_score
    score = normalized_hhi * max_score

    # Round to 1 decimal place
    return round(score, 1)

def calculate_metrics_from_portfolio_history():
    """
    Calculate risk metrics from portfolio history data.

    Returns:
        Dictionary of risk metrics.
    """
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(load_json_file('./config/portfolio_history.json'))

    if len(df) is 0:
        return 0, 0

    # Convert datetime to proper datetime format and set as index
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')  # Ensure chronological order
    df.set_index('datetime', inplace=True)

    # Calculate daily returns based on total_value
    df['daily_return'] = df['total_value'].pct_change()

    # Drop NaN values (first row will have NaN return)
    df = df.dropna()

    # Calculate Max Drawdown
    # First, calculate cumulative returns (starting from 1)
    df['cumulative_return'] = (1 + df['daily_return']).cumprod()

    # Calculate running maximum
    df['running_max'] = df['cumulative_return'].cummax()

    # Calculate drawdown
    df['drawdown'] = df['cumulative_return'] / df['running_max'] - 1

    # Find the maximum drawdown
    max_drawdown = abs(df['drawdown'].min()) * 100  # Convert to percentage

    # Calculate Sharpe Ratio
    # Assuming risk-free rate of 2% annually
    risk_free_rate = 0.02 / 252  # Daily risk-free rate

    # Calculate excess return
    df['excess_return'] = df['daily_return'] - risk_free_rate

    # Calculate Sharpe Ratio
    # For daily returns, multiply by sqrt(252) to annualize
    sharpe_ratio = df['excess_return'].mean() / df['daily_return'].std() * np.sqrt(252)

    return round(max_drawdown, 2), round(sharpe_ratio, 2)

def calculate_portfolio_data():
    """
    Calculate the portfolio data.

    Returns:
        dict: with all the portfolio data.
    """
    holdings, current_value, initial_investment = get_holdings()

    profit_loss = calculate_profit_loss(current_value, initial_investment)

    all_time_low, all_time_high = get_atl_ath()

    history_changes = calculate_changes_from_history()

    diversity_score = calculate_diversity_score(holdings)

    risk_string, risk_level = calculate_risk_level(holdings)

    portfolio_volatility = calculate_portfolio_volatility(holdings)

    transactions = load_transactions()

    transactions_performance, chart_data_json = get_portfolio_performance()

    max_drawdown, sharpe_ratio = calculate_metrics_from_portfolio_history()

    if holdings:
        weighted_change = sum(holding['day_change'] * holding['percentage'] / 100 for holding in holdings)
    else:
        weighted_change = 0

    weighted_change = round(weighted_change, 2)

    is_positive_total_value = True if weighted_change > 0 else False
    is_positive_all_time = True if profit_loss['amount'] > 0 else False

    risk_levels = {
        'volatility': determine_risk_level(portfolio_volatility, 'volatility'),
        'diversity': determine_risk_level(diversity_score, 'diversity'),
        'max_drawdown': determine_risk_level(max_drawdown, 'max_drawdown'),
        'sharpe_ratio': determine_risk_level(sharpe_ratio, 'sharpe_ratio')
    }
    return {
        # Holdings table
        'holdings': holdings,

        # Portfolio Value Card
        'current_value': f"${round(current_value, 2):,.2f}",
        'is_positive_total_value': is_positive_total_value,
        'weighted_change': weighted_change,
        'all_time_low': f"${all_time_low:,.2f}",
        'all_time_high': f"${all_time_high:,.2f}",

        # Profit & Loss Card
        'all_time_profit': f"${profit_loss['amount']:,.2f}",
        'all_time_profit_percentage': profit_loss['percentage'],
        'is_positive_all_time': is_positive_all_time,
        'profit_24h': history_changes['24h']['amount'],
        'profit_percentage_24': history_changes['24h']['percentage'],
        'is_positive_24h': history_changes['24h']['is_positive'],
        'profit_7d': history_changes['7d']['amount'],
        'profit_percentage_7d': history_changes['7d']['percentage'],
        'is_positive_7d': history_changes['7d']['is_positive'],
        'profit_30d': history_changes['30d']['amount'],
        'profit_percentage_30d': history_changes['30d']['percentage'],
        'is_positive_30d': history_changes['30d']['is_positive'],

        # Allocation & Metrics
        'assets_count': len(holdings),
        'diversity_score': diversity_score,
        'risk_string': risk_string,
        'risk_level': risk_level,
        'portfolio_volatility': portfolio_volatility,

        # Recent Transactions
        'transactions': transactions,

        # Portfolio Performance
        'chart_data': chart_data_json,

        # Risk Analysis
        'risk_levels': risk_levels,
        'max_drawdown': max_drawdown,
        'sharpe_rati': sharpe_ratio,
    }
