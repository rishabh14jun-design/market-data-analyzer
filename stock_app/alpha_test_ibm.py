import requests
import pandas as pd
import sys

# =========================
# CONFIG
# =========================
API_KEY = "FGT563EWASDNCIWX"   # later move to .env


# =========================
# DATA FETCH FUNCTION
# =========================
def fetch_daily_prices(symbol):
    """
    Fetch daily stock prices from Alpha Vantage (FREE endpoint)
    and return a clean pandas DataFrame.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",   # ~100 trading days
        "apikey": API_KEY
    }

    # ---- HTTP REQUEST ----
    response = requests.get(url, params=params)
    data = response.json()

    # ---- VALIDATION ----
    if "Time Series (Daily)" not in data:
        raise ValueError(f"API error or rate limit hit: {data}")

    # ---- STEP 9: Extract time series ----
    ts = data["Time Series (Daily)"]

    # ---- STEP 10: Dict -> DataFrame ----
    df = pd.DataFrame.from_dict(ts, orient="index")

    # ---- STEP 11: Rename columns ----
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)

    # ---- STEP 12: Enforce schema + numeric types ----
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    # ---- STEP 13: Datetime index + sort ----
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    return df


# =========================
# MAIN PROGRAM
# =========================
def main():
    # ---- Command-line argument handling ----
    if len(sys.argv) < 2:
        print("Usage: python alpha_test_ibm.py <SYMBOL>")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    output_file = f"stock_app/{symbol}_alpha_1month.csv"

    print(f"Fetching data for {symbol}...")

    # ---- Fetch data ----
    df = fetch_daily_prices(symbol)

    # Approx 1 month = last 22 trading days
    df_1_month = df.tail(22)

    # =========================
    # STEP 1: ANALYTICS
    # =========================
    df_1_month["Daily Return %"] = df_1_month["Close"].pct_change() * 100
    df_1_month["MA_5"] = df_1_month["Close"].rolling(5).mean()
    df_1_month["MA_10"] = df_1_month["Close"].rolling(10).mean()

    # ---- Save to CSV ----
    df_1_month.to_csv(output_file)

    print(f"Saved {len(df_1_month)} rows to {output_file}")
    print("\nLast 5 rows:")
    print(df_1_month.tail())


if __name__ == "__main__":
    main()
