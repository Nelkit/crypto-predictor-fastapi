from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.inference.predict import predict_next_day_high
from src.services.api import CoinGeckoApi
from datetime import date, timedelta

API_VERSION = "1.0.4"
app = FastAPI(
    title="Ethereum Price Prediction API",
    description="Predicts next-day HIGH price for Ethereum using an LSTM model.",
    version=API_VERSION,
    contact={
        "name": "Group 6 - AMLA AT3",
        "url": "https://github.com/Nelkit/36120-25SP-group6-25609227-AT3-fastapi",
        "email": "nelkit.chavezcalona@student.uts.edu.au",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.get("/", tags=["Overview"], summary="API Overview", response_description="Project overview and metadata")
def read_root():
    """
    Returns a JSON overview describing the API purpose, endpoints, parameters, and related repositories.

    This endpoint is useful for quick orientation and metadata retrieval.
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

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_description="Service health confirmation message",
    responses={200: {"description": "API is healthy and responsive"}},
)
def health_check():
    """
    Return API health status.

    Useful for monitoring tools like Render, Docker, or CI/CD pipelines.
    """
    return JSONResponse(content={"status": "OK", "message": f"Welcome to the Ethereum Prediction API v{API_VERSION} 🚀"},
                        status_code=200)

@app.get(
    "/predict/{token}", tags=["Prediction"],
    summary="Predict Ethereum next-day HIGH price",
    description=(
            "This endpoint predicts the **next-day HIGH price** for Ethereum (ETH) "
            "using a trained LSTM model. It fetches recent OHLC data from the CoinGecko API, "
            "processes the input features, and returns a price forecast for the following day."
    ),
    response_description="Predicted next-day high price in USD",
    responses={
        200: {
            "description": "Prediction generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "token": "ETH",
                        "next_day_high_predicted": "3540.27",
                        "next_day_high_date": "2025-11-01",
                        "model": "LSTM (tuned)",
                        "description": "Next-day HIGH price prediction for Ethereum in USD.",
                    }
                }
            },
        },
        400: {"description": "Invalid token or unsupported cryptocurrency"},
        503: {"description": "Failed to fetch data from CoinGecko"},
        500: {"description": "Error during model inference"},
    },
)
def predict_price(token: str):
    """
    ### Summary
    Predict the next-day HIGH price for Ethereum using historical OHLC data.

    ### Input
    - **token** (path parameter): Cryptocurrency symbol (must be 'ETH').

    ### Output
    JSON object containing:
    - `token`: Token symbol.
    - `next_day_high_predicted`: Predicted next-day high in USD.
    - `next_day_high_date`: Date for which the prediction applies.
    - `model`: Model used for prediction.
    - `description`: Short explanation of the result.
    """
    # Validate token input
    if token.lower() != "eth":
        raise HTTPException(status_code=400, detail="Only Ethereum predictions are available.")

    api = CoinGeckoApi()
    ohlc_data = api.fetch_merged_daily_data("ethereum", days=7)

    # validate fetched data
    if ohlc_data is None or ohlc_data.empty:
        raise HTTPException(status_code=503, detail="Failed to fetch OHLC data from API. Please try again later.")

    numerical_features = ["open", 'high', "low", "close", "volume", "market_cap"]
    missing_cols = [col for col in numerical_features if col not in ohlc_data.columns]

    if missing_cols:
        raise HTTPException(status_code=500, detail=f"Missing required columns in data: {missing_cols}")

    try:
        data = ohlc_data[numerical_features]
        y_next = predict_next_day_high(data)
        prediction = float(y_next)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

    next_day_high_date = date.today() + timedelta(days=1)
    result = {
        "token": token,
        "next_day_high_predicted": f"{prediction:.2f}",
        "next_day_high_date": f"{next_day_high_date}",
        "model": "LSTM (tuned)",
        "description": "Next-day HIGH price prediction for Ethereum in USD."
    }

    return JSONResponse(content=result)