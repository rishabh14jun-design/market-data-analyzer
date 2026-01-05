import sqlite3

# Open or create database file
conn = sqlite3.connect("market_data.db")

# Create cursor to execute SQL
cursor = conn.cursor()

# Create table (if not already present)
cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    symbol TEXT,
    date DATE,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY (symbol, date)
)
""")

# Save schema changes to disk
conn.commit()

# Close database connection
conn.close()

print("SQLite database and table ready")
