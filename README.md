
# Sales Performance & Customer Insights Dashboard

An interactive business intelligence portfolio project built with
Python, pandas, SQLite SQL, Streamlit, and Plotly.

## Project Overview

This project explores how sales data can be transformed into
business insights through data processing, SQL queries, interactive
visualizations, and KPI monitoring.

The dashboard uses synthetic data generated for educational
and portfolio purposes. It does not represent a real company.

## Features

- Revenue, completed orders, unique customers, and average order value KPIs
- Monthly revenue trend analysis
- Revenue breakdown by product category and customer segment
- Product performance analysis
- Customer-level revenue analysis
- Interactive filters for dates, regions, categories, and segments
- SQL joins across orders, customers, and products
- CSV export of filtered sales data
- Automatically generated descriptive observations

## Technology Stack

- Python
- pandas
- SQLite SQL
- Streamlit
- Plotly

## Project Structure

```text
sales-performance-dashboard/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/sales-performance-dashboard.git
cd sales-performance-dashboard
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The application will open in your browser.

## Analytical Approach

1. Generate reproducible synthetic customer, product, and order data.
2. Store the data in an in-memory SQLite database.
3. Join related tables using SQL.
4. Calculate revenue and business performance metrics.
5. Apply interactive filters to the resulting dataset.
6. Visualize trends, category performance, and customer contributions.
7. Export filtered records for further analysis.

## Business Questions

- How does revenue change over time?
- Which product categories contribute the most revenue?
- Which customer segments generate the highest revenue?
- Which products perform best during the selected period?
- Which customers contribute the most revenue?

## Key Metric Definitions

Revenue = Quantity × Unit Price × (1 − Discount)

Average Order Value = Total Revenue / Number of Completed Orders

Cancelled orders are excluded from the main analysis.

## Limitations

- The dataset is synthetic and should not be interpreted as real
  commercial performance.
- The dashboard focuses on descriptive analytics rather than
  forecasting or causal inference.
- Customer identifiers are generated for demonstration purposes.
- Results should be validated against business definitions when
  adapting the project to real datasets.

## Future Improvements

- Add automated data-quality checks.
- Connect to a persistent database.
- Implement customer RFM segmentation.
- Add sales forecasting and anomaly detection.
- Develop automated reporting for business stakeholders.
- Add unit tests for metric calculations and SQL queries.

## Author

Do Khanh Hien

Interests: Business Analysis, Data Analytics, AI Applications,
and Business Intelligence.
