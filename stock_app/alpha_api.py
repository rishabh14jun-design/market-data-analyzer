import requests
import pandas as pd

API_KEY = "FGT563EWASDNCIWX"   # later move to .env
BASE_URL = "https://www.alphavantage.co/query"


def fetch_daily_prices(symbol: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV prices from Alpha Vantage
    Returns Pandas DataFrame with index = date
    """

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",   # ~100 days
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=15)
    data = response.json()

    # ---- Error handling
    if "Error Message" in data:
        raise ValueError(f"Invalid symbol: {symbol}")

    if "Note" in data:
        raise ValueError("API rate limit hit")

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Unexpected API response: {data}")

    # ---- Convert JSON → DataFrame
    ts = data["Time Series (Daily)"]

    df = pd.DataFrame.from_dict(ts, orient="index")

    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)

    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    return df
