
import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# APP CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Sales Performance & Customer Insights")
st.caption(
    "Interactive business intelligence dashboard | "
    "Python · pandas · SQL · Streamlit · Plotly"
)

st.info(
    "Demo mode: this dashboard uses synthetic data generated "
    "for portfolio and educational purposes. It does not "
    "represent the performance of a real company."
)


# =========================================================
# SYNTHETIC DATA GENERATION
# =========================================================
@st.cache_data
def generate_demo_data():
    """Create reproducible synthetic sales data."""
    import random

    rng = random.Random(42)
    customer_rows = []
    product_rows = []
    order_rows = []

    segments = ["Consumer", "Corporate", "Small Business"]
    regions = ["North", "Central", "South"]
    categories = {
        "Technology": [
            ("Wireless Mouse", 25.0),
            ("Keyboard", 45.0),
            ("Monitor", 220.0),
            ("Headphones", 85.0),
        ],
        "Office Supplies": [
            ("Notebook", 5.0),
            ("Desk Organizer", 18.0),
            ("Printer Paper", 9.0),
            ("Pen Set", 7.0),
        ],
        "Furniture": [
            ("Office Chair", 180.0),
            ("Standing Desk", 350.0),
            ("Bookshelf", 140.0),
            ("Desk Lamp", 40.0),
        ],
    }

    for customer_id in range(1, 151):
        customer_rows.append({
            "customer_id": customer_id,
            "customer_name": f"Customer {customer_id:03d}",
            "segment": rng.choice(segments),
            "region": rng.choice(regions),
        })

    product_id = 1
    for category, items in categories.items():
        for product_name, price in items:
            product_rows.append({
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "unit_price": price,
            })
            product_id += 1

    # Each order contains one product line in this demo.
    for order_id in range(1, 1801):
        customer = rng.choice(customer_rows)
        product = rng.choice(product_rows)

        year = rng.choice([2024, 2025, 2026])
        month = rng.randint(1, 12)
        day = rng.randint(1, 28)

        order_rows.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "order_date": date(year, month, day).isoformat(),
            "quantity": rng.randint(1, 8),
            "discount": rng.choice([0.0, 0.0, 0.05, 0.10, 0.15]),
            "order_status": rng.choices(
                ["Completed", "Cancelled"],
                weights=[95, 5],
                k=1,
            )[0],
        })

    return (
        pd.DataFrame(customer_rows),
        pd.DataFrame(product_rows),
        pd.DataFrame(order_rows),
    )


customers, products, orders = generate_demo_data()


# =========================================================
# SQLITE DATABASE AND SQL QUERY
# =========================================================
@st.cache_data
def load_sales_data():
    customer_df, product_df, order_df = generate_demo_data()

    with sqlite3.connect(":memory:") as connection:
        customer_df.to_sql(
            "customers", connection, index=False, if_exists="replace"
        )
        product_df.to_sql(
            "products", connection, index=False, if_exists="replace"
        )
        order_df.to_sql(
            "orders", connection, index=False, if_exists="replace"
        )

        query = """
            SELECT
                o.order_id,
                o.order_date,
                o.customer_id,
                c.customer_name,
                c.segment,
                c.region,
                p.product_id,
                p.product_name,
                p.category,
                o.quantity,
                p.unit_price,
                o.discount,
                o.order_status,
                ROUND(
                    o.quantity * p.unit_price * (1 - o.discount), 2
                ) AS revenue
            FROM orders AS o
            JOIN customers AS c
                ON o.customer_id = c.customer_id
            JOIN products AS p
                ON o.product_id = p.product_id
            WHERE o.order_status = 'Completed'
        """

        sales_df = pd.read_sql_query(query, connection)

    sales_df["order_date"] = pd.to_datetime(sales_df["order_date"])
    return sales_df


sales = load_sales_data()


# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("Dashboard Filters")

min_date = sales["order_date"].min().date()
max_date = sales["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=sorted(sales["category"].unique()),
    default=sorted(sales["category"].unique()),
)

selected_segments = st.sidebar.multiselect(
    "Customer segments",
    options=sorted(sales["segment"].unique()),
    default=sorted(sales["segment"].unique()),
)

selected_regions = st.sidebar.multiselect(
    "Regions",
    options=sorted(sales["region"].unique()),
    default=sorted(sales["region"].unique()),
)


# =========================================================
# FILTERING
# =========================================================
filtered = sales.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["order_date"].dt.date.between(start_date, end_date)
    ]

if selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]
else:
    filtered = filtered.iloc[0:0]

if selected_segments:
    filtered = filtered[filtered["segment"].isin(selected_segments)]
else:
    filtered = filtered.iloc[0:0]

if selected_regions:
    filtered = filtered[filtered["region"].isin(selected_regions)]
else:
    filtered = filtered.iloc[0:0]


# =========================================================
# KPI CARDS
# =========================================================
st.subheader("Business Performance Overview")

total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
unique_customers = filtered["customer_id"].nunique()

average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Completed Orders", f"{total_orders:,}")
kpi3.metric("Unique Customers", f"{unique_customers:,}")
kpi4.metric("Average Order Value", f"${average_order_value:,.2f}")

st.caption(
    "Revenue is calculated as quantity × unit price × (1 − discount). "
    "Cancelled orders are excluded. Average order value is total "
    "revenue divided by the number of completed orders."
)

if filtered.empty:
    st.warning("No sales records match the selected filters.")
    st.stop()


# =========================================================
# REVENUE TREND
# =========================================================
st.subheader("Revenue Trends")

monthly = (
    filtered.assign(
        month=filtered["order_date"].dt.to_period("M").astype(str)
    )
    .groupby("month", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("month")
)

fig_trend = px.line(
    monthly,
    x="month",
    y="revenue",
    markers=True,
    title="Monthly Revenue",
    labels={
        "month": "Month",
        "revenue": "Revenue (USD)",
    },
)
fig_trend.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (USD)",
    hovermode="x unified",
)
st.plotly_chart(fig_trend, use_container_width=True)


# =========================================================
# CATEGORY AND SEGMENT ANALYSIS
# =========================================================
left, right = st.columns(2)

with left:
    category_summary = (
        filtered.groupby("category", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    fig_category = px.bar(
        category_summary,
        x="category",
        y="revenue",
        title="Revenue by Product Category",
        labels={
            "category": "Category",
            "revenue": "Revenue (USD)",
        },
    )
    st.plotly_chart(fig_category, use_container_width=True)

with right:
    segment_summary = (
        filtered.groupby("segment", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    fig_segment = px.pie(
        segment_summary,
        names="segment",
        values="revenue",
        title="Revenue Share by Customer Segment",
        hole=0.4,
    )
    st.plotly_chart(fig_segment, use_container_width=True)


# =========================================================
# PRODUCT PERFORMANCE
# =========================================================
st.subheader("Product Performance")

product_summary = (
    filtered.groupby(
        ["product_name", "category"], as_index=False
    )
    .agg(
        revenue=("revenue", "sum"),
        units_sold=("quantity", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

st.dataframe(
    product_summary,
    use_container_width=True,
    hide_index=True,
)

# =========================================================
# CUSTOMER INSIGHTS
# =========================================================
st.subheader("Customer Insights")

customer_summary = (
    filtered.groupby(
        ["customer_id", "customer_name", "segment", "region"],
        as_index=False,
    )
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        units_purchased=("quantity", "sum"),
    )
    .sort_values("revenue", ascending=False)
)

top_n = st.slider(
    "Number of customers to display",
    min_value=5,
    max_value=20,
    value=10,
)

st.markdown("**Top customers by revenue in the selected period**")
st.dataframe(
    customer_summary.head(top_n),
    use_container_width=True,
    hide_index=True,
)

# =========================================================
# AUTOMATED DESCRIPTIVE INSIGHTS
# =========================================================
st.subheader("Key Observations")

best_category = category_summary.iloc[0]
best_segment = segment_summary.sort_values(
    "revenue", ascending=False
).iloc[0]
best_product = product_summary.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"- **Leading category:** {best_category['category']} "
        f"generated ${best_category['revenue']:,.2f} in revenue."
    )
    st.markdown(
        f"- **Top product:** {best_product['product_name']} "
        f"generated ${best_product['revenue']:,.2f} in revenue."
    )

with col2:
    st.markdown(
        f"- **Leading segment:** {best_segment['segment']} "
        f"contributed ${best_segment['revenue']:,.2f} in revenue."
    )
    st.markdown(
        f"- **Customer coverage:** {unique_customers:,} unique "
        "customers purchased within the selected filters."
    )

st.caption(
    "Observations are calculated from the filtered synthetic dataset. "
    "They are descriptive findings, not causal conclusions or forecasts."
)


# =========================================================
# EXPORT
# =========================================================
st.subheader("Export Data")

csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Download Filtered Sales Data (CSV)",
    data=csv_bytes,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "Portfolio project | Python · pandas · SQLite SQL · Streamlit · Plotly"
)
