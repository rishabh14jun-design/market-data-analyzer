import yfinance as yf
import pandas as pd

SYMBOL = "TCS.NS"
BUY_PRICE = 2000

def main():
    stock = yf.Ticker(SYMBOL)

    # --- Company Info ---
    info = stock.info

    # Validate symbol
    if not info or info.get("longName") is None:
        print(f"Invalid or unsupported symbol: {SYMBOL}")
        return

    print("\nCompany:", info.get("longName"))
    print("Sector:", info.get("sector"))
    print("Market Cap:", info.get("marketCap"))

    # --- Price History ---
    data = stock.history(period="1mo")

    if data.empty:
        print("No data returned")
        return

    # --- Calculations ---
    data["Daily Return %"] = data["Close"].pct_change() * 100
    data["MA_5"] = data["Close"].rolling(window=5).mean()
    data["MA_10"] = data["Close"].rolling(window=10).mean()

    current_price = data["Close"].iloc[-1]
    pl = current_price - BUY_PRICE

    # --- Output ---
    print("\nLast 5 rows:")
    print(data.tail())

    print("\nBuy Price:", BUY_PRICE)
    print("Current Price:", round(current_price, 2))
    print("P/L:", round(pl, 2))

    # --- Export ---
    output_file = f"stock_app/{SYMBOL.replace('.', '_')}_analysis.csv"
    data.to_csv(output_file)
    print("\nData exported to:", output_file)


if __name__ == "__main__":
    main()
