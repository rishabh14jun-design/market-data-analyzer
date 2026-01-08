from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .ticker_logic import fetch_and_analyze


# =========================
# Create FastAPI app
# =========================
app = FastAPI(
    title="Stock Analyzer API",
    description="Backend API for stock analysis",
    version="1.0.0"
)

# =========================
# CORS (needed for Angular)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict to Angular domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Health check
# =========================
@app.get("/")
def health():
    return {"status": "OK", "message": "Stock Analyzer API running"}

# =========================
# Analyze stock
# =========================
@app.get("/analyze")
def analyze(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    try:
        result = fetch_and_analyze(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
