import json
from datetime import datetime

from sdk.portfolio_manager import load_transactions, calculate_metrics_from_portfolio_history


print(calculate_metrics_from_portfolio_history())