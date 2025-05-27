from sdk.api_client import get_crypto_global_data


def get_dict_crypto_market_global_data():
    """
    Fetches global cryptocurrency market data from CoinMarketCap API.

    Returns:
        dict: A dictionary containing global market data including market cap, volume, and dominance metrics.
        Returns None if the API request fails or if the response does not contain expected data.
    """
    response = get_crypto_global_data()

    if response is None:
        return None

    if 'data' not in response:
        return None

    return {
        'market_cap_value': response['data']['quote']['USD']['total_market_cap'],
        'market_cap_change': response['data']['quote']['USD']['total_volume_24h'],
        'market_cap_24h_change': response['data']['quote']['USD']['total_volume_24h'],
        'btc_dominance': str(round(response['data']['btc_dominance'], 2)) + '%',
        'eth_dominance': str(round(response['data']['eth_dominance'], 2)) + '%',
    }