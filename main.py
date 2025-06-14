"""
Main application file for the Flask trading journal.
"""

import logging
import sqlite3

from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from sdk.crypto.crypto_market_global_data import get_dict_crypto_market_global_data
from sdk.crypto.fear_and_greed_handler import get_fear_greed_data
from sdk.data_base.data_base_handler import initialize_data_base
from sdk.logger import setup_logging
from sdk.portoflio.analytics import calculate_portfolio_data
from sdk.portoflio.transactions import (
    create_csv_content,
    load_transactions_by_symbol,
    update_buy,
    update_sell,
)

app = Flask(__name__)
app.secret_key = "123123123123123123"

DB_FILE = "./data_bases/trades.db"

setup_logging()
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    trades = conn.execute("SELECT * FROM trades").fetchall()

    pairs = [
        row[0] for row in conn.execute("SELECT DISTINCT pair FROM trades").fetchall()
    ]
    strategies = [
        row[0]
        for row in conn.execute("SELECT DISTINCT strategy FROM trades").fetchall()
    ]
    conn.close()

    return render_template(
        "index.html", trades=trades, pairs=pairs, strategies=strategies
    )


@app.route("/transactions/<symbol>")
def get_transactions_by_symbol(symbol):
    try:
        return jsonify(load_transactions_by_symbol(symbol))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/transactions/<symbol>")
def export_transactions_csv(symbol):
    output, filename = create_csv_content(symbol)

    response = make_response(output)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@app.route("/add-transaction", methods=["POST"])
def add_new_transaction():
    try:
        asset = request.form.get("asset")
        amount = request.form.get("amount")
        purchase_price = request.form.get("purchasePrice")
        purchase_date = request.form.get("purchaseDate")
        exchange = request.form.get("exchange")
        wallet = request.form.get("wallet")
        notes = request.form.get("notes")

        if not all([asset, amount, purchase_price, purchase_date]):
            return jsonify({"error": "Please fill in all required fields"}), 400

        update_buy(
            asset,
            float(amount),
            float(purchase_price),
            purchase_date,
            exchange,
            wallet,
            notes,
        )
        return jsonify({"success": "Test response works!"}), 200

    except ValueError:
        return jsonify({"error": "Invalid number format in amount or price"}), 400
    except Exception as e:
        return jsonify({"error": f"Error adding transaction: {str(e)}"}), 500


@app.route("/history")
def history_tab():
    conn = sqlite3.connect(DB_FILE)
    trades = conn.execute("SELECT * FROM trades").fetchall()

    pairs = [
        row[0] for row in conn.execute("SELECT DISTINCT pair FROM trades").fetchall()
    ]
    strategies = [
        row[0]
        for row in conn.execute("SELECT DISTINCT strategy FROM trades").fetchall()
    ]
    conn.close()

    return render_template(
        "history.html", trades=trades, pairs=pairs, strategies=strategies
    )


@app.route("/api/global-crypto-data")
def get_global_crypto_data():
    """
    API endpoint to get Crypto Market Global Data
    """
    data = get_dict_crypto_market_global_data()
    return jsonify(data)


@app.route("/api/fear-greed")
def get_fear_greed():
    """
    API endpoint to get Fear & Greed data
    """
    data = get_fear_greed_data()
    return jsonify(data)


@app.route("/crypto")
def crypto():
    return render_template("crypto.html")


@app.route("/portfolio")
def portfolio():
    portfolio_data = calculate_portfolio_data()

    return render_template("portfolio.html", **portfolio_data)


@app.route("/buy_asset", methods=["POST"])
def buy_asset():
    try:
        # Get form data
        asset_name = request.form.get("asset_name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        # Convert to proper decimal values for financial calculations
        price_decimal = float(price)
        quantity_decimal = float(quantity)

        update_buy(asset_name, quantity_decimal, price_decimal)

        flash("Asset purchased successfully!", "success")
        return redirect(url_for("portfolio"))
    except ValueError as e:
        # Handle invalid number formats
        logger.error(f"Buy Asset Button invalid input: {str(e)}")
        flash(f"Invalid input: {str(e)}", "error")
        return redirect(url_for("portfolio"))
    except Exception as e:
        # Handle other errors
        logger.error(f"Buy Asset Button an error occurred: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("portfolio"))


@app.route("/sell_asset", methods=["POST"])
def sell_asset():
    try:
        # Get form data
        asset_name = request.form.get("asset_name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        # Convert to proper decimal values for financial calculations
        price_decimal = float(price)
        quantity_decimal = float(quantity)

        update_sell(asset_name, quantity_decimal, price_decimal)

        flash("Asset sold successfully!", "success")
        return redirect(url_for("portfolio"))
    except ValueError as e:
        # Handle invalid number formats
        logger.error(f"Sell Asset Button invalid input: {str(e)}")
        flash(f"Invalid input: {str(e)}", "error")
        return redirect(url_for("portfolio"))
    except Exception as e:
        # Handle other errors
        logger.error(f"Sell Asset Button an error occurred: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("portfolio"))


@app.route("/add", methods=["POST"])
def add_trade():
    data = [
        request.form[k]
        for k in [
            "date",
            "pair",
            "type",
            "entry",
            "stopLoss",
            "takeProfit",
            "exit",
            "profit",
            "size",
            "leverage",
            "strategy",
            "result",
            "confidence",
            "session",
            "note",
        ]
    ]

    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
      INSERT INTO trades (
        date, pair, type, entry, stopLoss, takeProfit,
        exit, profit, size, leverage, strategy,
        result, confidence, session, note
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        data,
    )

    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/export")
def export_csv():
    output, filename = create_csv_content("all")

    response = make_response(output)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


if __name__ == "__main__":
    initialize_data_base(DB_FILE)

    host = "127.0.0.1"
    port = 5000

    print(f"Starting server at http://{host}:{port}")

    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.methods}")

    app.run(host=host, port=port)
