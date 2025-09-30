from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "project": "Cryptocurrency Price Prediction API",
        "version": "0.1.0",
        "description": "API for predicting next-day HIGH prices of cryptocurrencies using pre-trained models."
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/predict/{token}")
def predict_price(token: str):
    return {
        "token": token,
    }