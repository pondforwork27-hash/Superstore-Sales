import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

# --- SIDEBAR FILTERING ---
st.sidebar.header("Filter Data")
region = st.sidebar.multiselect("Select Region", options=df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Select Category", options=df["Category"].unique(), default=df["Category"].unique())

# Filter the dataframe based on selection
df_selection = df.query("Region == @region & Category == @category")

# --- MAIN PAGE ---
st.title("📊 Sales Performance Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Sales"].sum())
average_sale = round(df_selection["Sales"].mean(), 2)
total_orders = df_selection["Order ID"].nunique()

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Sale:")
    st.subheader(f"US $ {average_sale}")
with right_column:
    st.subheader("Total Orders:")
    st.subheader(f"{total_orders}")

st.markdown("""---""")

# --- CHARTS ---

# Sales by Product Category [Bar Chart]
sales_by_category = df_selection.groupby(by=["Sub-Category"]).sum()[["Sales"]].sort_values(by="Sales")
fig_category = px.bar(
    sales_by_category,
    x="Sales",
    y=sales_by_category.index,
    orientation="h",
    title="<b>Sales by Sub-Category</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_category),
    template="plotly_white",
)

# Sales by Month [Line Chart]
sales_by_date = df_selection.groupby(df_selection['Order Date'].dt.to_period('M')).sum()[['Sales']]
sales_by_date.index = sales_by_date.index.to_timestamp()
fig_date = px.line(
    sales_by_date,
    x=sales_by_date.index,
    y="Sales",
    title="<b>Monthly Sales Trend</b>",
    template="plotly_white",
)

left_chart, right_chart = st.columns(2)
left_chart.plotly_chart(fig_category, use_container_width=True)
right_chart.plotly_chart(fig_date, use_container_width=True)

# Data Table
with st.expander("View Raw Filtered Data"):
    st.dataframe(df_selection)