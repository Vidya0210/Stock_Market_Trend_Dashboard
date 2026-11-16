
from pathlib import Path
import pandas as pd

# ==========================================
# STOCK DATA EXPLORATION AND ANALYSIS
# ==========================================

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Input and output files
INPUT_FILE = BASE_DIR / "data" / "AAPL_stock_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_FILE = OUTPUT_DIR / "stock_analysis_summary.csv"
MONTHLY_FILE = OUTPUT_DIR / "monthly_stock_analysis.csv"


def explore_stock_data():

    # 1. Load dataset
    print("\n========== 1. LOADING STOCK DATA ==========")

    if not INPUT_FILE.exists():
        print(f"Dataset not found: {INPUT_FILE}")
        print("Run python src/fetch_stock_data.py first.")
        return

    df = pd.read_csv(INPUT_FILE)

    # Convert Date column
    date_column = next(
        (col for col in df.columns if col.lower() in ["date", "datetime"]),
        None
    )

    if date_column is None:
        print("Date column not found. Please check the CSV file.")
        return

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df = df.dropna(subset=[date_column])
    df = df.sort_values(date_column).reset_index(drop=True)

    print("Dataset loaded successfully!")
    print(f"Number of rows: {len(df):,}")
    print(f"Number of columns: {len(df.columns)}")

    # 2. Display basic information
    print("\n========== 2. DATASET INFORMATION ==========")
    print("\nFirst 5 records:")
    print(df.head())

    print("\nLast 5 records:")
    print(df.tail())

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    # 3. Check missing values
    print("\n========== 3. DATA QUALITY CHECK ==========")

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:", df.duplicated().sum())

    # 4. Descriptive statistics
    print("\n========== 4. DESCRIPTIVE STATISTICS ==========")

    numeric_columns = df.select_dtypes(include="number").columns

    print(df[numeric_columns].describe())

    # 5. Calculate daily returns if not already available
    if "Daily_Return" not in df.columns and "Close" in df.columns:
        df["Daily_Return"] = df["Close"].pct_change() * 100

    # 6. Calculate key stock indicators
    print("\n========== 5. KEY STOCK INDICATORS ==========")

    if "Close" not in df.columns:
        print("Close price column not found.")
        return

    average_price = df["Close"].mean()
    highest_price = df["Close"].max()
    lowest_price = df["Close"].min()
    latest_price = df["Close"].iloc[-1]

    print(f"Average closing price: ${average_price:.2f}")
    print(f"Highest closing price: ${highest_price:.2f}")
    print(f"Lowest closing price: ${lowest_price:.2f}")
    print(f"Latest closing price: ${latest_price:.2f}")

    # 7. Calculate daily return statistics
    daily_return = df["Daily_Return"].dropna()

    average_return = daily_return.mean()
    volatility = daily_return.std()

    best_day = df.loc[df["Daily_Return"].idxmax()]
    worst_day = df.loc[df["Daily_Return"].idxmin()]

    print("\n========== 6. DAILY RETURN ANALYSIS ==========")
    print(f"Average daily return: {average_return:.3f}%")
    print(f"Daily return volatility: {volatility:.3f}%")
    print(
        f"Best trading day: {best_day[date_column].date()} "
        f"({best_day['Daily_Return']:.2f}%)"
    )
    print(
        f"Worst trading day: {worst_day[date_column].date()} "
        f"({worst_day['Daily_Return']:.2f}%)"
    )

    # 8. Monthly stock analysis
    print("\n========== 7. MONTHLY STOCK ANALYSIS ==========")

    df["Year_Month"] = df[date_column].dt.to_period("M").astype(str)

    monthly = df.groupby("Year_Month").agg(
        Average_Close=("Close", "mean"),
        Highest_Close=("Close", "max"),
        Lowest_Close=("Close", "min"),
        Total_Volume=("Volume", "sum")
    ).reset_index()

    print(monthly.tail(12).to_string(index=False))

    # 9. Save analysis results
    monthly.to_csv(MONTHLY_FILE, index=False)

    summary = pd.DataFrame({
        "Metric": [
            "Total Trading Records",
            "Average Closing Price",
            "Highest Closing Price",
            "Lowest Closing Price",
            "Latest Closing Price",
            "Average Daily Return (%)",
            "Daily Return Volatility (%)"
        ],
        "Value": [
            len(df),
            average_price,
            highest_price,
            lowest_price,
            latest_price,
            average_return,
            volatility
        ]
    })

    summary.to_csv(SUMMARY_FILE, index=False)

    print("\n========== 8. FILES SAVED ==========")
    print(f"Summary report: {SUMMARY_FILE}")
    print(f"Monthly report: {MONTHLY_FILE}")
    print("\nStock data exploration completed successfully!")


if __name__ == "__main__":
    explore_stock_data()
