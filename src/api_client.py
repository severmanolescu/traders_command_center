"""
Fetch cryptocurrency data from CoinMarketCap and Ethereum gas fees from Etherscan.
"""

import logging

import requests

from src.variables_fetcher import get_api_key, get_api_url

logger = logging.getLogger(__name__)


def get_crypto_data_by_symbols(symbols, convert="USD", session=None):
    """
    Get cryptocurrency data from CoinMarketCap for specific symbols.

    Args:
        symbols (list): List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
        convert (str): Currency to convert prices to

    Returns:
        dict: JSON response with cryptocurrency data or None if request failed
    """
    session = session or requests

    api_key = get_api_key("CMC_API_KEY")
    cmc_url = get_api_url("CMC_API_URL")

    if api_key is None:
        logger.error("Failed to fetch CoinMarketCap API key!")
        return None

    symbols_str = ",".join(symbols)

    params = {"symbol": symbols_str, "convert": convert}

    headers = {"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"}

    try:
        logger.info("Requesting data for symbols: %s", symbols_str)
        response = session.get(cmc_url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            logger.info("CMC data request successfully")
            return response.json()

        logger.error("API error: %s - %s", response.status_code, response.text)
        return None

    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error("Request error: %s", str(e))
        return None


def get_crypto_global_data(convert="USD", session=None):
    """
    Fetch global cryptocurrency market data from CoinMarketCap.
    Args:
        session: In case it is run from a test function
        convert: (str) Currency to convert values to (default is 'USD')

    Returns:
        dict: JSON response with global market data or None if request failed
    """
    session = session or requests

    api_key = get_api_key("CMC_API_KEY")
    cmc_url = get_api_url("CMC_API_URL")

    if api_key is None:
        logger.error("Failed to fetch CoinMarketCap API key!")
        return None

    params = {"convert": convert}

    headers = {"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"}

    try:
        logger.info("Requesting data for global metrics")
        response = session.get(cmc_url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            logger.info("CMC data request successfully")
            return response.json()

        logger.error("API error: %s - %s", response.status_code, response.text)
        return None
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error("Request error: %s", str(e))
        return None


def get_eth_gas_fee(session=None):
    """
    Fetch the current Ethereum gas fees from Etherscan.
    Returns:
        safe_gas (str or None): Safe gas price in Gwei
        propose_gas (str or None): Proposed gas price in Gwei
        fast_gas (str or None): Fast gas price in Gwei
    """
    try:
        session = session or requests

        url = get_api_url("ETHERSCAN_GAS_API_URL") + get_api_key("ETHERSCAN_API_KEY")
        response = session.get(url, timeout=30)

        if response.status_code == 200:
            gas_data = response.json()["result"]
            safe_gas = gas_data["SafeGasPrice"]
            propose_gas = gas_data["ProposeGasPrice"]
            fast_gas = gas_data["FastGasPrice"]
            return safe_gas, propose_gas, fast_gas

        logger.error(" Failed to fetch ETH gas fees.")
        print("❌ Failed to fetch ETH gas fees.")
        return None, None, None
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(" Error fetching ETH gas fees: %s", str(e))
        print(f"❌ Error fetching ETH gas fees: {e}")
        return None, None, None
