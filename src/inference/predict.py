import os
from tensorflow.keras.models import load_model
import joblib
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

# Load preprocessing and model
preprocessor = joblib.load(os.path.join(MODEL_DIR, "pipeline_preprocessing.pkl"))
scaler_X = preprocessor["scaler_X"]
scaler_y = preprocessor["scaler_y"]
seq_transformer = preprocessor["seq"]

# load the trained LSTM model
model = load_model(os.path.join(MODEL_DIR, "lstm_model.keras"))

def predict_next_day_high(x: pd.DataFrame):
    x_scaled = pd.DataFrame(scaler_X.transform(x), columns=x.columns)

    x_seq = seq_transformer.transform(x_scaled)

    y_pred_scaled = model.predict(x_seq)
    y_pred = scaler_y.inverse_transform(y_pred_scaled)

    return y_pred[-1][0]
