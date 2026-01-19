from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
import requests
import os

from stock_app.ticker_logic import fetch_and_analyze

# =========================
# App setup
# =========================
app = FastAPI(
    title="Stock Analyzer API",
    version="1.0.0"
)

# =========================
# CORS (for Angular UI)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Alpha Vantage API Key
# =========================
ALPHA_API_KEY = os.getenv("ALPHA_API_KEY", "FGT563EWASDNCIWX")

# =========================
# Health check
# =========================
@app.get("/")
def health():
    return {"status": "OK", "message": "Backend running"}

# =========================
# Analyze endpoint
# =========================
@app.get("/analyze")
def analyze(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    try:
        return fetch_and_analyze(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# Search endpoint
# =========================
@app.get("/search")
def search_symbol(q: str = Query(..., min_length=2)):
    """
    Search stock symbols by company name using Alpha Vantage
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": q,
        "apikey": ALPHA_API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    matches = data.get("bestMatches", [])

    results = []
    for m in matches[:5]:
        results.append({
            "symbol": m.get("1. symbol"),
            "name": m.get("2. name"),
            "region": m.get("4. region"),
            "currency": m.get("8. currency")
        })

    return results
