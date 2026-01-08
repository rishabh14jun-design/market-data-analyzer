import pandas as pd
from . import db_utils
from datetime import timedelta
from .alpha_api import fetch_daily_prices   # your existing API function


# =========================
# UTIL: expected trading date
# =========================
def get_expected_trading_date():
    today = pd.Timestamp.today().date()
    weekday = pd.Timestamp.today().weekday()

    if weekday == 5:          # Saturday
        return today - timedelta(days=1)
    elif weekday == 6:        # Sunday
        return today - timedelta(days=2)
    else:                     # Mon–Fri
        return today


# =========================
# INDICATORS
# =========================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================
# CORE FUNCTION (USED BY API)
# =========================
def fetch_and_analyze(symbol: str) -> dict:
    symbol = symbol.upper()

    # ---- Load from DB first
    df = db_utils.load_prices_from_sqlite(symbol)
    latest_date = db_utils.get_latest_date(symbol)
    expected_date = get_expected_trading_date()

    # ---- Decide if API call needed
    if (
        df.empty
        or latest_date is None
        or pd.to_datetime(latest_date).date() < expected_date
    ):
        api_df = fetch_daily_prices(symbol)
        db_utils.save_prices_to_sqlite(symbol, api_df)
        df = db_utils.load_prices_from_sqlite(symbol)

    # ---- Safety check
    if df.empty or len(df) < 15:
        return {
            "symbol": symbol,
            "error": "Not enough data to analyze"
        }

    # ---- Use recent window
    df = df.tail(30)

    # ---- Indicators
    df["MA_5"] = df["Close"].rolling(5).mean()
    df["MA_10"] = df["Close"].rolling(10).mean()
    df["RSI_14"] = calculate_rsi(df["Close"], 14)
    df["Avg_Volume"] = df["Volume"].rolling(10).mean()

    latest = df.iloc[-1]

    # ---- Signal logic
    signal = "HOLD"

    if (
        latest["MA_5"] > latest["MA_10"]
        and latest["Close"] > latest["MA_10"]
        and 40 < latest["RSI_14"] < 70
        and latest["Volume"] > latest["Avg_Volume"]
    ):
        signal = "BUY"

    elif (
        latest["MA_5"] < latest["MA_10"]
        and latest["RSI_14"] < 40
    ):
        signal = "SELL"

    # ---- Risk management
    stop_loss = None
    if signal == "BUY":
        stop_loss = round(latest["Close"] * 0.95, 2)

    # ---- Return JSON-ready result
    return {
        "symbol": symbol,
        "signal": signal,
        "close_price": round(latest["Close"], 2),
        "rsi_14": round(latest["RSI_14"], 2),
        "ma_5": round(latest["MA_5"], 2),
        "ma_10": round(latest["MA_10"], 2),
        "volume": int(latest["Volume"]),
        "stop_loss": stop_loss,
        "data_upto": str(df.index[-1].date())
    }
