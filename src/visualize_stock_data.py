
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# STOCK MARKET DATA VISUALIZATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "AAPL_stock_data.csv"
CHART_DIR = BASE_DIR / "outputs" / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)


def load_stock_data():
    print("Loading Apple stock data...")

    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])

    print(f"Dataset loaded: {len(df):,} records")

    return df


def create_closing_price_chart(df):
    fig = px.line(
        df,
        x="Date",
        y="Close",
        title="Apple (AAPL) Historical Closing Price",
        labels={
            "Date": "Date",
            "Close": "Closing Price (USD)"
        }
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        hovermode="x unified"
    )

    fig.write_html(CHART_DIR / "closing_price.html")
    print("Closing price chart saved!")


def create_daily_return_chart(df):
    fig = px.line(
        df,
        x="Date",
        y="Daily_Return",
        title="Apple Daily Returns (%)",
        labels={
            "Date": "Date",
            "Daily_Return": "Daily Return (%)"
        }
    )

    fig.add_hline(y=0, line_dash="dash")

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        hovermode="x unified"
    )

    fig.write_html(CHART_DIR / "daily_returns.html")
    print("Daily returns chart saved!")


def create_volume_chart(df):
    fig = px.bar(
        df,
        x="Date",
        y="Volume",
        title="Apple Daily Trading Volume",
        labels={
            "Date": "Date",
            "Volume": "Trading Volume"
        }
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        hovermode="x unified"
    )

    fig.write_html(CHART_DIR / "trading_volume.html")
    print("Trading volume chart saved!")


def create_moving_average_chart(df):
    df = df.copy()

    df["MA_50"] = df["Close"].rolling(window=50).mean()
    df["MA_200"] = df["Close"].rolling(window=200).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Closing Price"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MA_50"],
        mode="lines",
        name="50-Day Moving Average"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MA_200"],
        mode="lines",
        name="200-Day Moving Average"
    ))

    fig.update_layout(
        title="Apple Stock Price with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        title_x=0.5,
        hovermode="x unified"
    )

    fig.write_html(CHART_DIR / "moving_averages.html")
    print("Moving average chart saved!")


def main():
    df = load_stock_data()

    print("\nCreating stock market charts...")

    create_closing_price_chart(df)
    create_daily_return_chart(df)
    create_volume_chart(df)
    create_moving_average_chart(df)

    print("\nAll visualizations created successfully!")
    print(f"Charts location: {CHART_DIR}")


if __name__ == "__main__":
    main()
