import os
import joblib
import urllib.parse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

# ✅ Load Random Forest Model
RF_MODEL_PATH = "models/random_forest_model_compressed.pkl"  # Assuming model is in the models folder

try:
    rf_model = joblib.load(RF_MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ {RF_MODEL_PATH} not found. Train and save the model first.")

# 🚀 Feature Extraction (no pandas)
def extract_features(url: str):
    parsed_url = urllib.parse.urlparse(url)
    return [[
        len(url),
        url.count('.'),
        int("@" in url),
        int("-" in parsed_url.netloc),
        int(parsed_url.scheme == "https"),
        parsed_url.netloc.count('.'),
        url.count('/'),
        sum(c.isdigit() for c in url),
        sum(c in "?&=_$" for c in url)
    ]]

# 🔥 FastAPI App
app = FastAPI()

# Define Pydantic model for input data validation
class URLRequest(BaseModel):
    url: str

@app.post("/predict")
async def predict(data: URLRequest):
    url = data.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    features = extract_features(url)
    prediction = rf_model.predict(features)[0]

    result = {
        "url": url,
        "prediction": "Phishing" if prediction == 1 else "Legit"
    }

    return result

# 🏁 Entry Point
if __name__ == '__main__':
    # FastAPI uses Uvicorn for ASGI-based serving, but since Railway handles that, you don't need to run app here
    pass
