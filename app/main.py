from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.inference.predict import predict_next_day_high
from src.services.api import CoinGeckoApi
import pandas as pd
from datetime import date, timedelta

API_VERSION = "1.0.3"
app = FastAPI(
    title="Ethereum Price Prediction API",
    description="Predicts next-day HIGH price for Ethereum using an LSTM model.",
    version=API_VERSION,
)

@app.get("/", tags=["Overview"])
def read_root():
    """
    Display project overview and API documentation.
    """
    overview = {
        "project_title": "AT3 - Data Product with Machine Learning",
        "description": (
            "This FastAPI service hosts a trained LSTM model that predicts "
            "the next-day HIGH price for Ethereum based on historical market data. "
            "It forms part of the AMLA AT3 Crypto Data Product, which includes a Streamlit app "
            "and experimentation repository for time-series model evaluation."
        ),
        "objectives": [
            "Build a predictive model for Ethereum's next-day high price.",
            "Evaluate robustness under volatility and drift conditions.",
            "Deploy model via FastAPI and integrate with Streamlit front-end."
        ],
        "endpoints": {
            "/": "Project description and API documentation.",
            "/health/": "Service health check (returns 200).",
            "/predict/<token>": "Return next-day HIGH price prediction for the specified token."
        },
        "input_parameters": {
            "token": "string — cryptocurrency symbol (e.g., 'ETH')"
        },
        "output_format": {
            "token": "string — cryptocurrency symbol",
            "latest_date": "datetime — prediction generation time",
            "next_day_high": "float — predicted next-day high price (USD)",
            "model": "string — model type used for prediction",
            "description": "string — brief description of the prediction"
        },
        "related_repositories": {
            "Experiments": "https://github.com/nelkit/36120-25SP-group6-AT3-experimentation",
            "Streamlit App": "https://github.com/nelkit/36120-25SP-group6-AT3-streamlit",
            "FastAPI Model": "https://github.com/Nelkit/36120-25SP-group6-25609227-AT3-fastapi"
        },
        "api_version": API_VERSION
    }
    return JSONResponse(content=overview)

@app.get("/health", tags=["Health"])
def health_check():
    """
    Return API health status.
    """
    return JSONResponse(content={"status": "OK", "message": f"Welcome to the Ethereum Prediction API v{API_VERSION} 🚀"},
                        status_code=200)

@app.get("/predict/{token}", tags=["Prediction"])
def predict_price(token: str):
    """
    Predict the next-day HIGH price for Ethereum using historical OHLC data.
    """
    if token.lower() != "eth":
        raise HTTPException(status_code=400, detail="Only Ethereum predictions are available.")

    api = CoinGeckoApi()
    ohlc_data = api.fetch_merged_daily_data("ethereum", days=7)
    numerical_features = ["open", 'high', "low", "close", "volume", "market_cap"]
    data = ohlc_data[numerical_features]

    y_next = predict_next_day_high(data)
    prediction = float(y_next)

    next_day_high_date = date.today() + timedelta(days=1)

    result = {
        "token": token,
        "next_day_high_predicted": f"{prediction:.2f}",
        "next_day_high_date": f"{next_day_high_date}",
        "model": "LSTM (tuned)",
        "description": "Next-day HIGH price prediction for Ethereum in USD."
    }

    return JSONResponse(content=result)