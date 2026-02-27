import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Geographic Sales Insights", layout="wide")

# State Mapping for the Map
us_state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.header("Geography Filters")
selected_region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

# --- MAIN DASHBOARD ---
st.title("🗺️ Regional Sales Intelligence")

# 1. MAP SECTION
st.subheader("Sales Distribution by State")
state_sales = filtered_df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()

fig_map = px.choropleth(
    state_sales,
    locations='State Code',
    locationmode="USA-states",
    color='Sales',
    scope="usa",
    hover_name='State',
    color_continuous_scale="Viridis",
    labels={'Sales': 'Total Sales ($)'}
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# 2. INSIGHTS SECTION
st.markdown("---")
st.header("💡 Key Business Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Performing States")
    top_states = state_sales.sort_values(by='Sales', ascending=False).head(5)
    st.table(top_states[['State', 'Sales']])
    
    # Automated Text Insight
    best_state = top_states.iloc[0]['State']
    st.info(f"**Insight:** {best_state} is your strongest market, contributing the highest volume of sales in the current selection.")

with col2:
    st.subheader("Category Performance")
    cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig_pie = px.pie(cat_sales, values='Sales', names='Category', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Automated Text Insight
    top_cat = cat_sales.sort_values(by='Sales', ascending=False).iloc[0]['Category']
    st.success(f"**Insight:** {top_cat} is the dominant category. Focus marketing efforts here to maximize ROI.")

# 3. DEEP DIVE INSIGHT
st.markdown("---")
st.subheader("City-Level Leaders")
top_city = filtered_df.groupby('City')['Sales'].sum().sort_values(ascending=False).head(1).index[0]
st.write(f"Across the selected filters, **{top_city}** stands out as the #1 city for revenue generation.")

