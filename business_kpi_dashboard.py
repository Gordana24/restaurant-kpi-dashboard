import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Restaurant Performance Overview")
st.write("Business KPI Dashboard")

csv_path = Path("orders_final.csv")

df = pd.read_csv(csv_path)

st.success(f"Dataset loaded successfully: {len(df):,} rows")
# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Date filter
st.subheader("Select Date Range")

start_date = st.date_input(
    "Start date",
    value=df["date"].min().date()
)

end_date = st.date_input(
    "End date",
    value=df["date"].max().date()
)

# Filter dataset by selected date range
filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
].copy()

st.write(f"Filtered dataset: {len(filtered_df):,} rows")


# KPI 1 - Sales by Channel / Order Type
col1, col2 = st.columns(2)
with col1:
    
    st.subheader("Sales by Channel / Order Type")

    revenue_by_channel = (
        filtered_df.groupby("takeAway")["totalAmount"]
        .sum()
        .reset_index()
    )

    revenue_by_channel.columns = ["Order Type", "Total Revenue"]
    import altair as alt

    chart = alt.Chart(revenue_by_channel).mark_bar().encode(
        x=alt.X("Order Type:N", title="Order Type"),
        y=alt.Y("Total Revenue:Q", title="Revenue (DKK)"),
        tooltip=[
            alt.Tooltip("Order Type:N"),
            alt.Tooltip("Total Revenue:Q", format=",.0f")
        ]
    )
    st.altair_chart(chart, use_container_width=True)

# KPI 2 - Sales by Daypart
with col2:
    st.subheader("Sales by Daypart")

    filtered_df["hour"] = pd.to_datetime(
        filtered_df["time"].astype(str)
    ).dt.hour

    def get_daypart(hour):
        if 11 <= hour < 14:
            return "Lunch"
        elif 14 <= hour < 17:
            return "Afternoon"
        else:
            return "Evening"
        
    filtered_df["Daypart"] = filtered_df["hour"].apply(get_daypart)

    revenue_by_daypart = (
        filtered_df.groupby("Daypart")["totalAmount"]
        .sum()
        .reset_index()
    )

    daypart_chart = alt.Chart(revenue_by_daypart).mark_bar().encode(
        x=alt.X("Daypart:N", title="Daypart"),
        y=alt.Y("totalAmount:Q", title="Revenue (DKK)"),
        tooltip=[
            alt.Tooltip("Daypart:N"),
            alt.Tooltip("totalAmount:Q", format=",.0f")
        ]
    )

    st.altair_chart(daypart_chart, use_container_width=True)

# KPI 3 - Revenue by Category
col3, col4 = st.columns(2)
with col3:

    st.subheader("Revenue by Category")

    revenue_by_category = (
        filtered_df.groupby("category")["totalAmount"]
        .sum()
        .reset_index()
    )

    category_chart = alt.Chart(revenue_by_category).mark_bar().encode(
        x=alt.X("category:N", title="Category", sort="-y"),
        y=alt.Y("totalAmount:Q", title="Revenue (DKK)"),
        tooltip=[
            alt.Tooltip("category:N", title="Category"),
            alt.Tooltip("totalAmount:Q", title="Revenue (DKK)", format=",.0f")
        ]
    )

    st.altair_chart(category_chart, use_container_width=True)

# KPI 4 - Average Orders per Day
with col4:
    with st.container(border=True):
        st.subheader("Average Orders per Day")

        orders_per_day = (
            filtered_df.groupby(filtered_df["date"].dt.date)["orderNumber"]
            .nunique()
        )

        average_orders_per_day = orders_per_day.mean()

        st.metric(
            label="Average Orders per Day",
            value=f"{average_orders_per_day:,.0f}"
        )
