from unittest.mock import MagicMock, patch

import pytest

from src.api_client import (
    get_crypto_data_by_symbols,
    get_crypto_global_data,
    get_eth_gas_fee,
)


@pytest.fixture
def mock_response():
    """Fixture for mocked response"""
    mock = MagicMock()
    mock.json.return_value = {"status": {"error_code": 0}, "data": {}}
    mock.status_code = 200
    return mock


@pytest.fixture
def mock_session():
    """Fixture for mocked requests session"""
    with patch("src.api_client.requests.Session") as mock_session:
        session_instance = mock_session.return_value
        session_instance.get.return_value = MagicMock(status_code=200)
        yield session_instance


def test_get_crypto_data_by_symbols(mock_session, mock_response):
    """Test getting crypto data by symbols"""
    mock_session.get.return_value = mock_response
    mock_response.json.return_value = {
        "status": {"error_code": 0},
        "data": {"BTC": {"quote": {"USD": {"price": 50000}}}},
    }

    result = get_crypto_data_by_symbols(symbols=["BTC"], session=mock_session)
    assert isinstance(result, dict)
    assert "BTC" in result["data"]


def test_get_crypto_global_data(mock_session, mock_response):
    """Test getting global crypto data"""
    mock_session.get.return_value = mock_response
    mock_response.json.return_value = {
        "status_code": "200",
        "data": {"total_market_cap": {"USD": 2000000000000}},
    }

    result = get_crypto_global_data(session=mock_session)
    assert isinstance(result, dict)
    assert "total_market_cap" in result["data"]


def test_get_eth_gas_fee(mock_session, mock_response):
    """Test getting Ethereum gas fee"""
    mock_session.get.return_value = mock_response
    mock_response.json.return_value = {
        "status_code": "200",
        "result": {
            "SafeGasPrice": "20",
            "ProposeGasPrice": "50",
            "FastGasPrice": "100",
        },
    }

    safe_gas, propose_gas, fast_gas = get_eth_gas_fee(session=mock_session)
    assert isinstance(safe_gas, str), "Safe gas should be a string"
    assert safe_gas is "20", "Safe gas should be 20"
