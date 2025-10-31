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

def predict_next_day_high(x: pd.DataFrame) -> float:
    """Predict the next-day high from input features.

    Args:
        x (pd.DataFrame): Input features for the sequence (rows = timesteps, cols = features).

    Returns:
        float: Predicted next-day high.

    Raises:
        ValueError: If `x` is empty or None.
        RuntimeError: If preprocessing or model prediction fails or returns unexpected shape.
    """
    if x is None or x.empty:
        raise ValueError("Input DataFrame `x` must not be empty.")

    try:
        # Scale input features using the pre-fitted scaler
        x_scaled = pd.DataFrame(scaler_X.transform(x), columns=x.columns)

        # Transform scaled features into sequences for LSTM input
        x_seq = seq_transformer.transform(x_scaled)

        # Predict scaled output using the trained LSTM model
        y_pred_scaled = model.predict(x_seq)

        # Inverse transform predictions to original scale
        y_pred = scaler_y.inverse_transform(y_pred_scaled)
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")

    # Return the last prediction (next-day high)
    if y_pred.ndim == 2 and y_pred.shape[1] >= 1:
        return float(y_pred[-1, 0])
    if y_pred.ndim == 1:
        return float(y_pred[-1])

    raise RuntimeError(f"Unexpected prediction output shape: {y_pred.shape}")
