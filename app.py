from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sample_sales_data.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and prepare sample sales data."""
    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    df = df.dropna(subset=["date", "quantity", "unit_price"])

    df["total_amount"] = df["quantity"] * df["unit_price"]
    df["month"] = df["date"].dt.to_period("M").astype(str)

    return df


def format_currency(value: float) -> str:
    """Format values as currency."""
    return f"${value:,.2f}"


def main() -> None:
    st.set_page_config(
        page_title="Sales Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("Sales Dashboard")
    st.caption(
        "Interactive dashboard built with Streamlit, Python and CSV data."
    )

    df = load_data()

    st.sidebar.header("Filters")

    categories = sorted(df["category"].unique())
    channels = sorted(df["sales_channel"].unique())

    selected_categories = st.sidebar.multiselect(
        "Category",
        options=categories,
        default=categories,
    )

    selected_channels = st.sidebar.multiselect(
        "Sales Channel",
        options=channels,
        default=channels,
    )

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered_df = df[
        df["category"].isin(selected_categories)
        & df["sales_channel"].isin(selected_channels)
    ]

    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = filtered_df[
            (filtered_df["date"].dt.date >= start_date)
            & (filtered_df["date"].dt.date <= end_date)
        ]

    total_revenue = filtered_df["total_amount"].sum()
    total_orders = filtered_df["order_id"].nunique()
    total_units = filtered_df["quantity"].sum()
    average_ticket = total_revenue / total_orders if total_orders else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", format_currency(total_revenue))
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Total Units Sold", f"{int(total_units):,}")
    col4.metric("Average Ticket", format_currency(average_ticket))

    st.divider()

    category_report = (
        filtered_df.groupby("category", as_index=False)
        .agg(total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    channel_report = (
        filtered_df.groupby("sales_channel", as_index=False)
        .agg(total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    monthly_report = (
        filtered_df.groupby("month", as_index=False)
        .agg(total_revenue=("total_amount", "sum"))
        .sort_values("month")
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Revenue by Category")
        fig_category = px.bar(
            category_report,
            x="category",
            y="total_revenue",
            text_auto=".2s",
            labels={
                "category": "Category",
                "total_revenue": "Revenue",
            },
        )
        st.plotly_chart(fig_category, use_container_width=True)

    with chart_col2:
        st.subheader("Revenue by Sales Channel")
        fig_channel = px.pie(
            channel_report,
            names="sales_channel",
            values="total_revenue",
            hole=0.45,
        )
        st.plotly_chart(fig_channel, use_container_width=True)

    st.subheader("Monthly Revenue Trend")
    fig_monthly = px.line(
        monthly_report,
        x="month",
        y="total_revenue",
        markers=True,
        labels={
            "month": "Month",
            "total_revenue": "Revenue",
        },
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.subheader("Filtered Sales Data")
    st.dataframe(
        filtered_df.sort_values("date", ascending=False),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
