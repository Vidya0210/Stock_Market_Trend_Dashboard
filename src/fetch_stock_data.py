
from pathlib import Path
import pandas as pd
import yfinance as yf

# ==========================================
# STOCK MARKET DATA COLLECTION
# ==========================================

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Stock details
TICKER = "AAPL"
START_DATE = "2020-01-01"

# Output location
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / f"{TICKER}_stock_data.csv"


def fetch_stock_data():

    print("Downloading stock market data...")
    print(f"Stock: {TICKER}")

    # Download historical stock data
    df = yf.download(
        TICKER,
        start=START_DATE,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        print("No stock data received. Please check your internet connection or ticker.")
        return

    # Handle MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Convert date index into a column
    df.reset_index(inplace=True)

    # Calculate daily percentage returns
    df["Daily_Return"] = df["Close"].pct_change() * 100

    # Save data as CSV
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nStock data downloaded successfully!")
    print(f"Total records: {len(df):,}")
    print(f"Saved file: {OUTPUT_FILE}")

    print("\nFirst five records:")
    print(df.head())


if __name__ == "__main__":
    fetch_stock_data()
