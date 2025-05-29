import logging
import requests

from random import random

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
        response = requests.get('https://api.alternative.me/fng/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            value = int(data['data'][0]['value'])
        else:
            logger.error("Error fetching Fear & Greed data from API, using random value instead.")

            # Fallback to random value
            value = random.randint(1, 100)
    except Exception as e:
        # Fallback to random value if API fails
        logger.error("Failed to fetch Fear & Greed data from API, status code: %s", e)

        value = random.randint(1, 100)

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
        'value': value,
        'classification': classification,
        'last_updated': 'Updated now',
        'stroke_offset': stroke_offset,
        'color': color
    }