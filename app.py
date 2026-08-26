# ============================================================
# TASK 2: STOCK PORTFOLIO TRACKER - STREAMLIT APP
# CodeAlpha Internship - Task 2
# Created by: Tehmina Anwar
# ============================================================

import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Stock Portfolio Tracker",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.08);
    text-align: center;
}

.profit {
    color: #0a8f3d;
    font-weight: bold;
}

.loss {
    color: #d93025;
    font-weight: bold;
}

.footer {
    text-align: center;
    color: #777;
    margin-top: 40px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">📈 Stock Portfolio Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'CodeAlpha Internship - Task 2 | Created by: Tehmina Anwar'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "🌐 Live stock prices are powered by Yahoo Finance. "
    "Enter valid ticker symbols such as AAPL, TSLA, MSFT, GOOGL, AMZN, META or NVDA."
)


# ============================================================
# SESSION STATE
# ============================================================

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []


# ============================================================
# GET LIVE PRICE
# ============================================================

@st.cache_data(ttl=60)
def get_stock_price(symbol):

    try:

        symbol = symbol.upper().strip()

        stock = yf.Ticker(symbol)

        data = stock.history(period="1d")

        if data.empty:
            return None

        price = data["Close"].iloc[-1]

        if pd.isna(price):
            return None

        return float(price)

    except Exception:
        return None


# ============================================================
# REFRESH ALL PRICES
# ============================================================

def refresh_all_prices():

    for item in st.session_state.portfolio:

        price = get_stock_price(item["stock"])

        if price is not None:
            item["current_price"] = price


# ============================================================
# CALCULATE TOTALS
# ============================================================

def calculate_totals():

    total_investment = 0
    total_value = 0

    for item in st.session_state.portfolio:

        investment = (
            item["purchase_price"] *
            item["quantity"]
        )

        current_value = (
            item["current_price"] *
            item["quantity"]
        )

        total_investment += investment
        total_value += current_value

    profit_loss = total_value - total_investment

    if total_investment > 0:
        percentage = (
            profit_loss /
            total_investment
        ) * 100
    else:
        percentage = 0

    return (
        total_investment,
        total_value,
        profit_loss,
        percentage
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Portfolio Controls")

    st.write(
        "Manage your stock portfolio from here."
    )

    if st.button(
        "🔄 Refresh Live Prices",
        use_container_width=True
    ):

        with st.spinner("Updating live prices..."):

            refresh_all_prices()

        st.success("Prices updated successfully!")

    st.divider()

    st.subheader("📌 Supported Examples")

    st.write(
        "AAPL\n\n"
        "TSLA\n\n"
        "GOOGL\n\n"
        "MSFT\n\n"
        "AMZN\n\n"
        "META\n\n"
        "NVDA"
    )

    st.divider()

    st.caption(
        "Created by Tehmina Anwar"
    )


# ============================================================
# TOP METRICS
# ============================================================

(
    total_investment,
    total_value,
    total_profit_loss,
    total_percentage
) = calculate_totals()


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Total Investment",
        f"${total_investment:,.2f}"
    )

with col2:

    st.metric(
        "📊 Current Value",
        f"${total_value:,.2f}"
    )

with col3:

    st.metric(
        "📈 Profit / Loss",
        f"${total_profit_loss:,.2f}",
        delta=f"{total_percentage:.2f}%"
    )

with col4:

    st.metric(
        "📦 Holdings",
        len(st.session_state.portfolio)
    )


st.divider()


# ============================================================
# ADD STOCK
# ============================================================

st.header("➕ Add Stock")

with st.form("add_stock_form"):

    col1, col2, col3 = st.columns(3)

    with col1:

        symbol = st.text_input(
            "Stock Symbol",
            placeholder="Example: AAPL"
        ).upper().strip()

    with col2:

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1,
            value=1
        )

    with col3:

        purchase_price = st.number_input(
            "Purchase Price per Share",
            min_value=0.01,
            step=0.01,
            value=1.00
        )

    submitted = st.form_submit_button(
        "➕ Add Stock",
        use_container_width=True
    )


if submitted:

    if not symbol:

        st.error(
            "❌ Please enter a stock symbol."
        )

    else:

        with st.spinner(
            f"Fetching live price for {symbol}..."
        ):

            current_price = get_stock_price(symbol)

        if current_price is None:

            st.error(
                f"❌ Could not find live data for {symbol}. "
                "Please check the ticker symbol."
            )

        else:

            # Check if stock already exists

            existing = None

            for item in st.session_state.portfolio:

                if item["stock"] == symbol:
                    existing = item
                    break

            if existing:

                old_quantity = existing["quantity"]

                old_investment = (
                    existing["purchase_price"] *
                    old_quantity
                )

                new_investment = (
                    purchase_price *
                    quantity
                )

                new_quantity = (
                    old_quantity +
                    quantity
                )

                combined_investment = (
                    old_investment +
                    new_investment
                )

                existing["quantity"] = new_quantity

                existing["purchase_price"] = (
                    combined_investment /
                    new_quantity
                )

                existing["current_price"] = (
                    current_price
                )

                st.success(
                    f"✅ {symbol} updated with "
                    f"{quantity} additional shares."
                )

            else:

                st.session_state.portfolio.append({

                    "stock": symbol,

                    "quantity": int(quantity),

                    "purchase_price": float(
                        purchase_price
                    ),

                    "current_price": float(
                        current_price
                    )

                })

                st.success(
                    f"✅ {symbol} added successfully!"
                )

            st.rerun()


# ============================================================
# PORTFOLIO TABLE
# ============================================================

st.header("📊 Your Portfolio")


if not st.session_state.portfolio:

    st.warning(
        "Your portfolio is empty. Add a stock above to get started."
    )

else:

    rows = []

    for item in st.session_state.portfolio:

        stock = item["stock"]

        quantity = item["quantity"]

        purchase_price = item["purchase_price"]

        current_price = item["current_price"]

        investment = (
            purchase_price *
            quantity
        )

        current_value = (
            current_price *
            quantity
        )

        profit_loss = (
            current_value -
            investment
        )

        if investment != 0:

            percentage = (
                profit_loss /
                investment
            ) * 100

        else:

            percentage = 0

        rows.append({

            "Stock": stock,

            "Quantity": quantity,

            "Buy Price": purchase_price,

            "Current Price": current_price,

            "Investment": investment,

            "Current Value": current_value,

            "Profit/Loss": profit_loss,

            "Return %": percentage

        })


    df = pd.DataFrame(rows)


    st.dataframe(

        df.style.format({

            "Buy Price": "${:,.2f}",

            "Current Price": "${:,.2f}",

            "Investment": "${:,.2f}",

            "Current Value": "${:,.2f}",

            "Profit/Loss": "${:,.2f}",

            "Return %": "{:.2f}%"

        }),

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# STOCK MANAGEMENT
# ============================================================

if st.session_state.portfolio:

    st.divider()

    st.header("✏️ Manage Holdings")

    symbols = [
        item["stock"]
        for item in st.session_state.portfolio
    ]

    selected_stock = st.selectbox(
        "Select Stock",
        symbols
    )

    selected_item = next(
        item
        for item in st.session_state.portfolio
        if item["stock"] == selected_stock
    )


    col1, col2 = st.columns(2)


    # UPDATE

    with col1:

        st.subheader("✏️ Update Quantity")

        new_quantity = st.number_input(
            "New Quantity",
            min_value=1,
            value=int(
                selected_item["quantity"]
            ),
            step=1
        )

        if st.button(
            "Update Stock",
            use_container_width=True
        ):

            selected_item["quantity"] = int(
                new_quantity
            )

            st.success(
                f"✅ {selected_stock} updated."
            )

            st.rerun()


    # DELETE

    with col2:

        st.subheader("🗑️ Delete Stock")

        st.write(
            f"Remove **{selected_stock}** "
            "from your portfolio."
        )

        if st.button(
            "Delete Stock",
            use_container_width=True
        ):

            st.session_state.portfolio = [

                item

                for item in st.session_state.portfolio

                if item["stock"] != selected_stock

            ]

            st.success(
                f"✅ {selected_stock} deleted."
            )

            st.rerun()


# ============================================================
# CHECK STOCK PRICE
# ============================================================

st.divider()

st.header("🔎 Check Live Stock Price")

price_symbol = st.text_input(
    "Enter any stock symbol",
    placeholder="Example: NVDA"
).upper().strip()


if st.button(
    "🔎 Check Price",
    use_container_width=False
):

    if not price_symbol:

        st.error(
            "Please enter a stock symbol."
        )

    else:

        with st.spinner(
            f"Fetching {price_symbol} price..."
        ):

            price = get_stock_price(
                price_symbol
            )

        if price is None:

            st.error(
                f"❌ Could not find {price_symbol}."
            )

        else:

            st.success(
                f"💵 {price_symbol} Current Price: "
                f"${price:,.2f}"
            )


# ============================================================
# PORTFOLIO CHART
# ============================================================

if st.session_state.portfolio:

    st.divider()

    st.header("📈 Portfolio Value Chart")

    chart_data = pd.DataFrame({

        "Stock": [
            item["stock"]
            for item in st.session_state.portfolio
        ],

        "Current Value": [

            item["current_price"] *
            item["quantity"]

            for item in st.session_state.portfolio

        ]

    })

    chart_data = chart_data.set_index(
        "Stock"
    )

    st.bar_chart(
        chart_data
    )


# ============================================================
# DOWNLOAD CSV
# ============================================================

if st.session_state.portfolio:

    st.divider()

    st.header("💾 Export Portfolio")

    export_rows = []

    for item in st.session_state.portfolio:

        investment = (
            item["purchase_price"] *
            item["quantity"]
        )

        current_value = (
            item["current_price"] *
            item["quantity"]
        )

        profit_loss = (
            current_value -
            investment
        )

        percentage = (

            (profit_loss / investment) * 100

            if investment != 0

            else 0

        )

        export_rows.append({

            "Stock": item["stock"],

            "Quantity": item["quantity"],

            "Purchase Price":
                item["purchase_price"],

            "Current Price":
                item["current_price"],

            "Investment":
                investment,

            "Current Value":
                current_value,

            "Profit/Loss":
                profit_loss,

            "Profit/Loss %":
                percentage

        })


    export_df = pd.DataFrame(
        export_rows
    )


    csv_data = export_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(

        label="📥 Download Portfolio CSV",

        data=csv_data,

        file_name="portfolio.csv",

        mime="text/csv",

        use_container_width=True

    )


# ============================================================
# TXT REPORT
# ============================================================

if st.session_state.portfolio:

    report = []

    report.append(
        "STOCK PORTFOLIO REPORT"
    )

    report.append(
        "=" * 60
    )

    report.append(
        "Created by: Tehmina Anwar"
    )

    report.append(
        "CodeAlpha Internship - Task 2"
    )

    report.append(
        "Date: " +
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    report.append(
        "=" * 60
    )

    report.append("")


    for item in st.session_state.portfolio:

        investment = (
            item["purchase_price"] *
            item["quantity"]
        )

        current_value = (
            item["current_price"] *
            item["quantity"]
        )

        profit_loss = (
            current_value -
            investment
        )

        percentage = (

            (profit_loss / investment) * 100

            if investment != 0

            else 0

        )


        report.append(
            f"Stock: {item['stock']}"
        )

        report.append(
            f"Quantity: {item['quantity']}"
        )

        report.append(
            f"Purchase Price: "
            f"${item['purchase_price']:,.2f}"
        )

        report.append(
            f"Current Price: "
            f"${item['current_price']:,.2f}"
        )

        report.append(
            f"Investment: "
            f"${investment:,.2f}"
        )

        report.append(
            f"Current Value: "
            f"${current_value:,.2f}"
        )

        report.append(
            f"Profit/Loss: "
            f"${profit_loss:,.2f}"
        )

        report.append(
            f"Return: "
            f"{percentage:.2f}%"
        )

        report.append(
            "-" * 60
        )


    report.append("")

    report.append(
        f"TOTAL INVESTMENT: "
        f"${total_investment:,.2f}"
    )

    report.append(
        f"CURRENT PORTFOLIO VALUE: "
        f"${total_value:,.2f}"
    )

    report.append(
        f"TOTAL PROFIT/LOSS: "
        f"${total_profit_loss:,.2f}"
    )

    report.append(
        f"TOTAL RETURN: "
        f"{total_percentage:.2f}%"
    )

    report.append("")

    report.append(
        "Created by: Tehmina Anwar"
    )


    report_text = "\n".join(
        report
    )


    st.download_button(

        label="📄 Download TXT Report",

        data=report_text,

        file_name="portfolio_report.txt",

        mime="text/plain",

        use_container_width=True

    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        📈 Stock Portfolio Tracker<br>
        CodeAlpha Internship - Task 2<br>
        Created by <b>Tehmina Anwar</b><br>
        🌐 Live data powered by Yahoo Finance
    </div>
    """,
    unsafe_allow_html=True
)