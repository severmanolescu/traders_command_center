from sdk.api_client import get_crypto_global_data

def format_market_cap(value):
    """
    Formats the market cap value into a human-readable string with appropriate units.

    Args:
        value (float): The market cap value in USD.

    Returns:
        str: A formatted string representing the market cap value.
    """
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    elif value >= 1e9:
        return f"${value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.2f}M"
    elif value >= 1e3:
        return f"${value / 1e3:.2f}K"
    else:
        return f"${value:.2f}"

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
        'market_cap_value': format_market_cap(response['data']['quote']['USD']['total_market_cap']) ,
        'market_cap_change': round(response['data']['quote']['USD']['total_market_cap_yesterday_percentage_change'], 2),
        'market_cap_24h_change': format_market_cap(response['data']['quote']['USD']['total_volume_24h']),
        'btc_dominance': str(round(response['data']['btc_dominance'], 2)) + '%',
        'eth_dominance': str(round(response['data']['eth_dominance'], 2)) + '%',
        'defi_market_cap': format_market_cap(response['data']['quote']['USD']['defi_market_cap']),
        'defi_24h_change': format_market_cap(response['data']['quote']['USD']['defi_volume_24h']),
    }