# flask_trade_tracker/app.py
import json

from flask import Flask, request, render_template, redirect, url_for, send_file
import sqlite3, csv, os
from io import StringIO

from sdk.portfolio_manager import(
    get_holdings,
    calculate_profit_loss,
    calculate_changes_from_history,
    calculate_diversity_score,
    calculate_risk_level,
    calculate_portfolio_volatility,
    load_transactions,
    get_portfolio_performance,
    calculate_metrics_from_portfolio_history,
    determine_risk_level,
)

from sdk.variables_fetcher import get_atl_ath

app = Flask(__name__)
DB_FILE = 'trades.db'

# Initialize DB if not exists
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
conn.execute('''CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  pair TEXT,
  type TEXT,
  entry REAL,
  stopLoss REAL,
  takeProfit REAL,
  exit REAL,
  profit REAL,
  size REAL,
  leverage REAL,
  strategy TEXT,
  result TEXT,
  confidence INTEGER,
  session TEXT,
  note TEXT
)''')

conn.commit()
conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    trades = conn.execute("SELECT * FROM trades").fetchall()

    pairs = [row[0] for row in conn.execute("SELECT DISTINCT pair FROM trades").fetchall()]
    strategies = [row[0] for row in conn.execute("SELECT DISTINCT strategy FROM trades").fetchall()]
    conn.close()

    return render_template("index.html", trades=trades, pairs=pairs, strategies=strategies)

@app.route('/history')
def history_tab():
    conn = sqlite3.connect(DB_FILE)
    trades = conn.execute("SELECT * FROM trades").fetchall()

    pairs = [row[0] for row in conn.execute("SELECT DISTINCT pair FROM trades").fetchall()]
    strategies = [row[0] for row in conn.execute("SELECT DISTINCT strategy FROM trades").fetchall()]
    conn.close()

    return render_template("history.html", trades=trades, pairs=pairs, strategies=strategies)

@app.route('/portfolio')
def portfolio():
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

    # Calculate overall percentage change (24h)
    if holdings:
        # Calculate weighted average change based on each asset's allocation percentage
        weighted_change = sum(holding['day_change'] * holding['percentage'] / 100 for holding in holdings)
    else:
        weighted_change = 0

    weighted_change = round(weighted_change, 2)

    # Load coin mappings
    with open("./config/coin_mappings.json", "r") as file:
        coin_mappings = json.load(file)

    # Add icon info to each holding
    for holding in holdings:
        symbol = holding["symbol"]
        if symbol in coin_mappings:
            holding["coin_info"] = coin_mappings[symbol]
        else:
            holding["coin_info"] = {
                "name": symbol.lower(),
                "color": "#F0F0F0",
                "icon": None
            }

    is_positive_total_value = True if weighted_change > 0 else False
    is_positive_all_time = True if profit_loss['amount'] > 0 else False

    risk_levels = {
        'volatility': determine_risk_level(portfolio_volatility, 'volatility'),
        'diversity': determine_risk_level(diversity_score, 'diversity'),
        'max_drawdown': determine_risk_level(max_drawdown, 'max_drawdown'),
        'sharpe_ratio': determine_risk_level(sharpe_ratio, 'sharpe_ratio')
    }

    return render_template(
        'portfolio.html',
        # Holdings table
        holdings=holdings,
        # Portfolio Value Card
        portfolio_value=f"${current_value:,.2f}",
        is_positive_total_value=is_positive_total_value,
        change_percentage=weighted_change,
        all_time_low=f"${all_time_low:,.2f}",
        all_time_high=f"${all_time_high:,.2f}",
        # Profit & Loss Card
        all_time_profit=f"${profit_loss['amount']:,.2f}",
        all_time_profit_percentage=profit_loss['percentage'],
        is_positive_all_time=is_positive_all_time,
        profit_24h=history_changes['24h']['amount'],
        profit_percentage_24=history_changes['24h']['percentage'],
        is_positive_24h=history_changes['24h']['is_positive'],
        profit_7d=history_changes['7d']['amount'],
        profit_percentage_7d=history_changes['7d']['percentage'],
        is_positive_7d=history_changes['7d']['is_positive'],
        profit_30d=history_changes['30d']['amount'],
        profit_percentage_30d=history_changes['30d']['percentage'],
        is_positive_30d=history_changes['30d']['is_positive'],
        # Allocation & Metrics
        assets_count=len(holdings),
        diversity_score=diversity_score,
        risk_string=risk_string,
        risk_level=risk_level,
        portfolio_volatility=portfolio_volatility,
        # Recent Transactions
        transactions=transactions,
        # Portfolio Performance
        chart_data=chart_data_json,
        # Risk Analysis
        risk_levels=risk_levels,
        max_drawdown=max_drawdown,
        sharpe_ratio=sharpe_ratio,
    )

@app.route('/add', methods=['POST'])
def add_trade():
    data = [request.form[k] for k in [
        'date', 'pair', 'type', 'entry', 'stopLoss', 'takeProfit',
        'exit', 'profit', 'size', 'leverage', 'strategy',
        'result', 'confidence', 'session', 'note'
    ]]

    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
      INSERT INTO trades (
        date, pair, type, entry, stopLoss, takeProfit,
        exit, profit, size, leverage, strategy,
        result, confidence, session, note
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    conn = sqlite3.connect(DB_FILE)
    trades = conn.execute("SELECT * FROM trades").fetchall()
    headers = [d[0] for d in conn.execute("PRAGMA table_info(trades)")]
    conn.close()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)
    for row in trades:
        writer.writerow(row)

    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='trades.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
