import logging
import requests

from sdk.variables_fetcher import get_api_key

logger = logging.getLogger(__name__)

def get_crypto_data_by_symbols(symbols, convert='USD'):
    """
    Get cryptocurrency data from CoinMarketCap for specific symbols.

    Args:
        symbols (list): List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
        convert (str): Currency to convert prices to

    Returns:
        dict: JSON response with cryptocurrency data or None if request failed
    """
    api_key = get_api_key("coinmarketcap")

    if api_key is None:
        logger.error("Failed to fetch CoinMarketCap API key!")
        return None

    logger.info(api_key)
    symbols_str = ','.join(symbols)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    params = {
        'symbol': symbols_str,
        'convert': convert
    }

    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }

    try:
        logger.info(f"Requesting data for symbols: {symbols_str}")
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            logger.info("CMC data request successfully")
            return response.json()
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return None
