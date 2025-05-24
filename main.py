import logging
import sqlite3, csv

from io import StringIO
from flask import Flask, request, render_template, redirect, url_for, send_file, flash, jsonify, make_response

from sdk.portoflio.analytics import(
    calculate_portfolio_data,
)
from sdk.logger import setup_logging
from sdk.variables_fetcher import update_buy
from sdk.portoflio.transactions import load_transactions_by_symbol, create_csv_content

app = Flask(__name__)
app.secret_key = '123123123123123123'

DB_FILE = 'trades.db'

setup_logging()
logger = logging.getLogger(__name__)

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


@app.route('/transactions/<symbol>')
def get_transactions_by_symbol(symbol):
    try:
        return jsonify(load_transactions_by_symbol(symbol))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export/transactions/<symbol>')
def export_transactions_csv(symbol):
    output, filename = create_csv_content(symbol)

    response = make_response(output)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

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
    portfolio_data = calculate_portfolio_data()

    return render_template(
        'portfolio.html',
        **portfolio_data
    )

@app.route('/buy_asset', methods=['POST'])
def buy_asset():
    try:
        # Get form data
        asset_name = request.form.get('asset_name')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        # Convert to proper decimal values for financial calculations
        price_decimal = float(price)
        quantity_decimal = float(quantity)

        update_buy(asset_name, quantity_decimal, price_decimal)

        flash('Asset purchased successfully!', 'success')
        return redirect(url_for('portfolio'))
    except ValueError as e:
        # Handle invalid number formats
        logger.error(f'Buy Asset Button invalid input: {str(e)}')
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('portfolio'))
    except Exception as e:
        # Handle other errors
        logger.error(f'Buy Asset Button an error occurred: {str(e)}')
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('portfolio'))

@app.route('/sell_asset', methods=['POST'])
def sell_asset():
    asset_name = request.form.get('asset_name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    logger.info(f'{asset_name}, {price}, {quantity}')

    return redirect(url_for('portfolio'))

# Handle sell transaction
# Get form data from request.form
# Process the transaction
# Redirect back to portfolio page

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

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000
    print(f"Starting server at http://{host}:{port}")
    app.run(host=host, port=port)
