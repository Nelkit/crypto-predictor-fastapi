import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project_title" in data
    assert "description" in data
    assert "endpoints" in data
    assert "api_version" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert "Welcome to the Ethereum Prediction API" in data["message"]

def test_predict_valid_token():
    # Mock the API and prediction
    sample_data = pd.DataFrame({
        "open": [3000, 3100, 3200],
        "high": [3100, 3200, 3300],
        "low": [2900, 3000, 3100],
        "close": [3050, 3150, 3250],
        "volume": [1000000, 1100000, 1200000],
        "market_cap": [500000000, 510000000, 520000000]
    })

    with patch('app.main.CoinGeckoApi') as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_instance.fetch_merged_daily_data.return_value = sample_data
        mock_api_class.return_value = mock_api_instance

        with patch('app.main.predict_next_day_high', return_value=3400.0):
            response = client.get("/predict/eth")
            assert response.status_code == 200
            data = response.json()
            assert data["token"] == "eth"
            assert data["next_day_high_predicted"] == "3400.00"
            assert "next_day_high_date" in data
            assert data["model"] == "LSTM (tuned)"
            assert "description" in data

def test_predict_invalid_token():
    response = client.get("/predict/btc")
    assert response.status_code == 400
    data = response.json()
    assert "Only Ethereum predictions are available" in data["detail"]

def test_predict_api_failure():
    with patch('app.main.CoinGeckoApi') as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_instance.fetch_merged_daily_data.return_value = pd.DataFrame()  # Empty DataFrame
        mock_api_class.return_value = mock_api_instance

        response = client.get("/predict/eth")
        assert response.status_code == 503
        data = response.json()
        assert "Failed to fetch OHLC data" in data["detail"]

def test_predict_missing_columns():
    sample_data = pd.DataFrame({
        "open": [3000, 3100],
        "high": [3100, 3200],
        # Missing low, close, volume, market_cap
    })

    with patch('app.main.CoinGeckoApi') as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_instance.fetch_merged_daily_data.return_value = sample_data
        mock_api_class.return_value = mock_api_instance

        response = client.get("/predict/eth")
        assert response.status_code == 500
        data = response.json()
        assert "Missing required columns" in data["detail"]

def test_predict_prediction_error():
    sample_data = pd.DataFrame({
        "open": [3000, 3100, 3200],
        "high": [3100, 3200, 3300],
        "low": [2900, 3000, 3100],
        "close": [3050, 3150, 3250],
        "volume": [1000000, 1100000, 1200000],
        "market_cap": [500000000, 510000000, 520000000]
    })

    with patch('app.main.CoinGeckoApi') as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_instance.fetch_merged_daily_data.return_value = sample_data
        mock_api_class.return_value = mock_api_instance

        with patch('app.main.predict_next_day_high', side_effect=Exception("Prediction failed")):
            response = client.get("/predict/eth")
            assert response.status_code == 500
            data = response.json()
            assert "Error during prediction" in data["detail"]
