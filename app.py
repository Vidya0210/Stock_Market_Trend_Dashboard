
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Stock Market Intelligence",
    page_icon="📈",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "AAPL_stock_data.csv"

# ==========================================
# CUSTOM STYLING
# ==========================================



st.markdown("""
<style>

/* Main dashboard background */
.stApp {
    background: linear-gradient(135deg, #0B1220, #172B4D);
}

/* Main dashboard headings */
h1, h2, h3 {
    color: #FFFFFF !important;
}

/* General dashboard text */
p, label {
    color: #FFFFFF;
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #DCE3ED;
}

/* IMPORTANT: Make all KPI card text dark */
[data-testid="stMetric"] * {
    color: #17243A !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #101B35;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Dividers */
hr {
    border-color: #526581;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
    df = df.sort_values("Date")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Stock data file not found. Run src/fetch_stock_data.py first.")
    st.stop()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📊 Dashboard Controls")

st.sidebar.write("Stock: Apple Inc. (AAPL)")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = df[
        (df["Date"].dt.date >= start_date) &
        (df["Date"].dt.date <= end_date)
    ]
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("No stock data available for this date range.")
    st.stop()

# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("📈 Stock Market Intelligence Dashboard")

st.caption(
    "Interactive analysis of Apple Inc. stock market performance"
)

st.divider()

# ==========================================
# KEY PERFORMANCE INDICATORS
# ==========================================

latest_price = filtered_df["Close"].iloc[-1]
highest_price = filtered_df["Close"].max()
lowest_price = filtered_df["Close"].min()
average_price = filtered_df["Close"].mean()

daily_return = filtered_df["Daily_Return"].iloc[-1]

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Latest Price", f"${latest_price:,.2f}")
col2.metric("Highest Price", f"${highest_price:,.2f}")
col3.metric("Lowest Price", f"${lowest_price:,.2f}")
col4.metric("Average Price", f"${average_price:,.2f}")
col5.metric(
    "Latest Daily Return",
    f"{daily_return:.2f}%" if pd.notna(daily_return) else "N/A"
)

st.divider()

# ==========================================
# CLOSING PRICE TREND
# ==========================================

st.subheader("Historical Stock Price Trend")

price_fig = px.line(
    filtered_df,
    x="Date",
    y="Close",
    title="Apple Closing Price Over Time"
)

price_fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    yaxis_title="Price (USD)",
    xaxis_title="Date"
)

st.plotly_chart(price_fig, use_container_width=True)

# ==========================================
# DAILY RETURNS AND TRADING VOLUME
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Daily Returns")

    return_fig = px.line(
        filtered_df,
        x="Date",
        y="Daily_Return",
        title="Daily Stock Returns (%)"
    )

    return_fig.add_hline(y=0, line_dash="dash")

    return_fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(return_fig, use_container_width=True)

with col2:
    st.subheader("Trading Volume")

    volume_fig = px.bar(
        filtered_df,
        x="Date",
        y="Volume",
        title="Daily Trading Volume"
    )

    volume_fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(volume_fig, use_container_width=True)

# ==========================================
# MOVING AVERAGES
# ==========================================

st.subheader("Moving Average Analysis")

ma_df = filtered_df.copy()

ma_df["MA_50"] = ma_df["Close"].rolling(50).mean()
ma_df["MA_200"] = ma_df["Close"].rolling(200).mean()

ma_fig = go.Figure()

ma_fig.add_trace(go.Scatter(
    x=ma_df["Date"],
    y=ma_df["Close"],
    name="Closing Price",
    mode="lines"
))

ma_fig.add_trace(go.Scatter(
    x=ma_df["Date"],
    y=ma_df["MA_50"],
    name="50-Day Moving Average",
    mode="lines"
))

ma_fig.add_trace(go.Scatter(
    x=ma_df["Date"],
    y=ma_df["MA_200"],
    name="200-Day Moving Average",
    mode="lines"
))

ma_fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Price (USD)"
)

st.plotly_chart(ma_fig, use_container_width=True)

# ==========================================
# MONTHLY PERFORMANCE
# ==========================================

st.subheader("Monthly Stock Performance")

monthly_df = filtered_df.copy()

monthly_df["Year_Month"] = (
    monthly_df["Date"].dt.to_period("M").astype(str)
)

monthly_summary = monthly_df.groupby(
    "Year_Month"
).agg(
    Average_Close=("Close", "mean"),
    Total_Volume=("Volume", "sum")
).reset_index()

monthly_fig = px.bar(
    monthly_summary,
    x="Year_Month",
    y="Average_Close",
    title="Monthly Average Closing Price",
    labels={
        "Year_Month": "Month",
        "Average_Close": "Average Price (USD)"
    }
)

monthly_fig.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45
)

st.plotly_chart(monthly_fig, use_container_width=True)


# ==========================================
# MONTHLY RETURNS ANALYSIS
# ==========================================

st.subheader("Monthly Returns Performance")

monthly_returns_df = filtered_df.copy()

monthly_returns_df["Year_Month"] = (
    monthly_returns_df["Date"].dt.to_period("M").astype(str)
)

monthly_returns = monthly_returns_df.groupby(
    "Year_Month"
)["Close"].agg(
    First_Close="first",
    Last_Close="last"
).reset_index()

monthly_returns["Monthly_Return"] = (
    (monthly_returns["Last_Close"] - monthly_returns["First_Close"])
    / monthly_returns["First_Close"]
) * 100

monthly_returns["Performance"] = monthly_returns[
    "Monthly_Return"
].apply(
    lambda x: "Positive" if x >= 0 else "Negative"
)

monthly_fig = go.Figure()

monthly_fig.add_trace(go.Bar(
    x=monthly_returns["Year_Month"],
    y=monthly_returns["Monthly_Return"],
    marker_color=[
        "#16A34A" if value >= 0 else "#DC2626"
        for value in monthly_returns["Monthly_Return"]
    ],
    name="Monthly Return"
))

monthly_fig.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray"
)

monthly_fig.update_layout(
    title="Monthly Stock Returns (%)",
    xaxis_title="Month",
    yaxis_title="Monthly Return (%)",
    template="plotly_white",
    hovermode="x unified",
    xaxis_tickangle=-45
)

st.plotly_chart(monthly_fig, use_container_width=True)

st.dataframe(
    monthly_returns.sort_values(
        "Year_Month", ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# RSI TECHNICAL INDICATOR
# ==========================================

st.subheader("Relative Strength Index (RSI)")

rsi_df = filtered_df.copy()

# Calculate daily price changes
delta = rsi_df["Close"].diff()

# Separate gains and losses
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

# Calculate average gains and losses
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

# Calculate RSI
rs = avg_gain / avg_loss

rsi_df["RSI"] = 100 - (100 / (1 + rs))

# Handle periods with no losses or no gains
rsi_df.loc[
    (avg_loss == 0) & (avg_gain > 0), "RSI"
] = 100

rsi_df.loc[
    (avg_loss == 0) & (avg_gain == 0), "RSI"
] = 50

# Create RSI chart
rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    x=rsi_df["Date"],
    y=rsi_df["RSI"],
    mode="lines",
    name="RSI (14)",
    line=dict(width=2)
))

# Overbought level
rsi_fig.add_hline(
    y=70,
    line_dash="dash",
    annotation_text="Overbought (70)"
)

# Oversold level
rsi_fig.add_hline(
    y=30,
    line_dash="dash",
    annotation_text="Oversold (30)"
)

rsi_fig.update_layout(
    title="Apple Stock RSI Indicator",
    xaxis_title="Date",
    yaxis_title="RSI",
    yaxis_range=[0, 100],
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(rsi_fig, use_container_width=True)

latest_rsi = rsi_df["RSI"].dropna()

if not latest_rsi.empty:
    current_rsi = latest_rsi.iloc[-1]

    st.metric(
        "Latest RSI (14)",
        f"{current_rsi:.2f}"
    )

    if current_rsi > 70:
        st.warning("The stock may be overbought.")
    elif current_rsi < 30:
        st.success("The stock may be oversold.")
    else:
        st.info("RSI is currently in the neutral range.")



# ==========================================
# MACD TECHNICAL INDICATOR
# ==========================================

st.subheader("MACD – Stock Momentum Analysis")

macd_df = filtered_df.copy()

# Calculate 12-day and 26-day exponential moving averages
macd_df["EMA_12"] = macd_df["Close"].ewm(
    span=12, adjust=False
).mean()

macd_df["EMA_26"] = macd_df["Close"].ewm(
    span=26, adjust=False
).mean()

# Calculate MACD line
macd_df["MACD"] = (
    macd_df["EMA_12"] - macd_df["EMA_26"]
)

# Calculate signal line
macd_df["Signal_Line"] = macd_df["MACD"].ewm(
    span=9, adjust=False
).mean()

# Calculate histogram
macd_df["MACD_Histogram"] = (
    macd_df["MACD"] - macd_df["Signal_Line"]
)

# Create MACD chart
macd_fig = go.Figure()

macd_fig.add_trace(go.Scatter(
    x=macd_df["Date"],
    y=macd_df["MACD"],
    mode="lines",
    name="MACD Line"
))

macd_fig.add_trace(go.Scatter(
    x=macd_df["Date"],
    y=macd_df["Signal_Line"],
    mode="lines",
    name="Signal Line"
))

macd_fig.add_trace(go.Bar(
    x=macd_df["Date"],
    y=macd_df["MACD_Histogram"],
    name="MACD Histogram"
))

macd_fig.add_hline(y=0, line_dash="dash")

macd_fig.update_layout(
    title="Apple Stock MACD Indicator",
    xaxis_title="Date",
    yaxis_title="MACD Value",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(macd_fig, use_container_width=True)

# Latest MACD values
latest_macd = macd_df.iloc[-1]

col1, col2, col3 = st.columns(3)

col1.metric(
    "MACD Line",
    f"{latest_macd['MACD']:.2f}"
)

col2.metric(
    "Signal Line",
    f"{latest_macd['Signal_Line']:.2f}"
)

col3.metric(
    "MACD Histogram",
    f"{latest_macd['MACD_Histogram']:.2f}"
)

if latest_macd["MACD"] > latest_macd["Signal_Line"]:
    st.success("MACD is above the Signal Line – positive momentum indication.")
else:
    st.warning("MACD is below the Signal Line – negative momentum indication.")



# ==========================================
# STOCK COMPARISON ANALYSIS
# ==========================================

st.subheader("Stock Market Comparison")

st.write(
    "Compare Apple's performance with other leading technology companies."
)

selected_stocks = st.multiselect(
    "Select companies to compare",
    options=["MSFT", "GOOGL", "NVDA", "AMZN"],
    default=["MSFT", "NVDA"]
)

if st.button("Compare Stocks"):

    comparison_data = {}

    comparison_start = filtered_df["Date"].min().strftime("%Y-%m-%d")
    comparison_end = (
        filtered_df["Date"].max() + pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # Include Apple as the benchmark
    comparison_data["AAPL"] = filtered_df[
        ["Date", "Close"]
    ].copy()

    for ticker in selected_stocks:

        try:
            stock_df = yf.Ticker(ticker).history(
                start=comparison_start,
                end=comparison_end,
                auto_adjust=True
            )

            if stock_df.empty:
                st.warning(f"No data available for {ticker}.")
                continue

            stock_df = stock_df.reset_index()

            comparison_data[ticker] = pd.DataFrame({
                "Date": pd.to_datetime(
                    stock_df["Date"]
                ).dt.tz_localize(None),
                "Close": stock_df["Close"]
            })

        except Exception as error:
            st.warning(f"Could not download {ticker}: {error}")

    # Calculate percentage performance from the first available price
    comparison_fig = go.Figure()

    for ticker, stock in comparison_data.items():

        stock = stock.dropna(subset=["Close"]).sort_values("Date")

        if stock.empty:
            continue

        first_price = stock["Close"].iloc[0]

        stock["Performance"] = (
            (stock["Close"] / first_price) - 1
        ) * 100

        comparison_fig.add_trace(go.Scatter(
            x=stock["Date"],
            y=stock["Performance"],
            mode="lines",
            name=ticker
        ))

    comparison_fig.update_layout(
        title="Stock Performance Comparison (%)",
        xaxis_title="Date",
        yaxis_title="Performance (%)",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        comparison_fig,
        use_container_width=True
    )

# ==========================================
# DATA TABLE
# ==========================================

st.subheader("Stock Market Historical Data")

st.dataframe(
    filtered_df.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# DOWNLOAD STOCK ANALYSIS REPORTS
# ==========================================

st.subheader("Download Analysis Reports")

download_col1, download_col2 = st.columns(2)

with download_col1:

    stock_csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Stock Data",
        data=stock_csv,
        file_name="AAPL_stock_analysis.csv",
        mime="text/csv"
    )

with download_col2:

    monthly_csv = monthly_returns.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Monthly Returns",
        data=monthly_csv,
        file_name="AAPL_monthly_returns.csv",
        mime="text/csv"
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Stock Market Trend Dashboard | Data source: Yahoo Finance | "
    "Built using Python, Pandas, Plotly and Streamlit"
)
