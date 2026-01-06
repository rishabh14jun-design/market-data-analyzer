import sys
import requests
import pandas as pd
import db_utils

API_KEY = "FGT563EWASDNCIWX"   # move to .env later


# =========================
# SYMBOL SEARCH
# =========================
def search_symbol(keyword):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keyword,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "bestMatches" not in data:
        return []

    results = []
    for item in data["bestMatches"]:
        results.append({
            "symbol": item.get("1. symbol"),
            "name": item.get("2. name"),
            "region": item.get("4. region"),
            "score": float(item.get("9. matchScore", 0))
        })

    return results


# =========================
# FETCH FROM API
# =========================
def fetch_daily_prices(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"API error: {data}")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")

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


# =========================
# RSI CALCULATION
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
# MAIN
# =========================
def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python ticker-search.py search <KEYWORD>")
        print("  python ticker-search.py fetch <SYMBOL>")
        sys.exit(1)

    action = sys.argv[1].lower()
    value = sys.argv[2].upper()

    # ---------- SEARCH ----------
    if action == "search":
        print(f"\nSearching for '{value}'...\n")
        results = search_symbol(value)

        if not results:
            print("No symbols found.")
        else:
            for r in results:
                print(
                    f"{r['symbol']:10} | "
                    f"{r['name'][:40]:40} | "
                    f"{r['region']:15} | "
                    f"score={r['score']}"
                )

    # ---------- FETCH ----------
    elif action == "fetch":
        print(f"\nChecking local database for {value}...\n")

        df = db_utils.load_prices_from_sqlite(value)
        latest_date = db_utils.get_latest_date(value)
        print(f"ticker latest_date in database: {latest_date}")
        today = pd.Timestamp.today().date()
        print(f"todays timestamp: {today}")
        weekday = pd.Timestamp.today().weekday()
        print(f"Weekday: {weekday}")

        if weekday == 5:          # Saturday
          expected_date = today - pd.Timedelta(days=1)
        elif weekday == 6:        # Sunday
          expected_date = today - pd.Timedelta(days=2)
        else:                     # Monday–Friday
          expected_date = today



        if df.empty or latest_date is None or pd.to_datetime(latest_date).date() < expected_date:
            print("Local data missing or outdated. Fetching from API...\n")
            api_df = fetch_daily_prices(value)
            db_utils.save_prices_to_sqlite(value, api_df)
            df = db_utils.load_prices_from_sqlite(value)
        else:
            print("Using cached local data.\n")

        # Use last 22 trading days
        df = df.tail(22)

        # ----- INDICATORS -----
        df["Daily Return %"] = df["Close"].pct_change() * 100
        df["MA_5"] = df["Close"].rolling(5).mean()
        df["MA_10"] = df["Close"].rolling(10).mean()
        df["RSI_14"] = calculate_rsi(df["Close"], 14)
        df["Avg_Volume"] = df["Volume"].rolling(10).mean()

        latest = df.iloc[-1]

        # ----- SIGNAL LOGIC -----
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

        stop_loss = None
        if signal == "BUY":
            stop_loss = round(latest["Close"] * 0.95, 2)

        # ----- OUTPUT -----
        output_file = f"stock_app/{value}_alpha_1month.csv"
        df.to_csv(output_file)

        print("----- SIGNAL SUMMARY -----")
        print(f"Close Price     : {round(latest['Close'], 2)}")
        print(f"MA_5 / MA_10    : {round(latest['MA_5'],2)} / {round(latest['MA_10'],2)}")
        print(f"RSI (14)        : {round(latest['RSI_14'],2)}")
        print(f"Volume          : {int(latest['Volume'])}")
        print(f"Avg Volume      : {int(latest['Avg_Volume'])}")
        print(f"Signal          : {signal}")

        if stop_loss:
            print(f"Suggested SL    : {stop_loss}")

        print(f"\nSaved CSV : {output_file}")
        print("\nLast 5 rows:")
        print(df.tail())

    else:
        print("Invalid action. Use 'search' or 'fetch'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
