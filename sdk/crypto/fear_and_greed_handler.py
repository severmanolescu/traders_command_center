"""
Fear & Greed Index Handler
This module fetches the Fear & Greed Index data from an external
API and processes it to provide a classification and color coding based on the index value.
"""

import logging

import requests

from sdk.variables_fetcher import get_api_url

logger = logging.getLogger(__name__)


def get_fear_greed_data():
    """
    Get Fear & Greed Index data
    Returns:
        dict: Contains:
            Fear & Greed Index value,
            classification,
            last updated time,
            stroke offset for SVG gauge,
            and color.
    """
    try:
        # Try to get real data from Alternative.me Crypto Fear & Greed API
        url = get_api_url("ALTERNATIVE_ME_FNG")

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            value = int(data["data"][0]["value"])
        else:
            logger.error(
                "Error fetching Fear & Greed data from API, using random value instead."
            )

            # Fallback to random value
            value = 0
    except requests.RequestException as e:
        logger.error("RequestException while fetching Fear & Greed data: %s", e)

        value = 0

    # Calculate classification
    if value <= 25:
        classification = "Extreme Fear"
        color = "#ef4444"
    elif value <= 45:
        classification = "Fear"
        color = "#f97316"
    elif value <= 55:
        classification = "Neutral"
        color = "#eab308"
    elif value <= 75:
        classification = "Greed"
        color = "#84cc16"
    else:
        classification = "Extreme Greed"
        color = "#22c55e"

    # Calculate stroke offset for SVG gauge
    total_length = 251.2
    progress = value / 100
    stroke_offset = total_length - (total_length * progress)

    return {
        "value": value,
        "classification": classification,
        "last_updated": "Updated now",
        "stroke_offset": stroke_offset,
        "color": color,
    }
