import sqlite3
import pandas as pd


DB_FILE = "market_data.db"


def save_prices_to_sqlite(symbol, df):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for trade_date, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO prices
            (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            trade_date.strftime("%Y-%m-%d"),
            row["Open"],
            row["High"],
            row["Low"],
            row["Close"],
            int(row["Volume"])
        ))

    conn.commit()
    conn.close()


def load_prices_from_sqlite(symbol):
    conn = sqlite3.connect(DB_FILE)

    query = """
        SELECT date, open, high, low, close, volume
        FROM prices
        WHERE symbol = ?
        ORDER BY date
    """

    df = pd.read_sql(query, conn, params=(symbol,))
    conn.close()

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }, inplace=True)

    return df


def get_latest_date(symbol):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT MAX(date) FROM prices WHERE symbol = ?",
        (symbol,)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0]  # can be None
