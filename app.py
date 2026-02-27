import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Superstore Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Enhanced CSS with animations ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #0a0f1a 0%, #0f1a2f 100%);
    }
    
    /* Animated metric cards */
    .metric-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border: 1px solid #2d4a6b;
        border-radius: 16px;
        padding: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(66,153,225,0.2);
        border-color: #4299e1;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border-left: 4px solid #4299e1;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        color: #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    
    .insight-card.warn { border-left-color: #ed8936; }
    .insight-card.good { border-left-color: #48bb78; }
    .insight-card.alert { border-left-color: #e94560; }
    
    .insight-icon { font-size: 1.5rem; margin-bottom: 8px; }
    .insight-label { font-size: 0.75rem; color: #a0aec0; text-transform: uppercase; }
    .insight-value { font-size: 1.5rem; font-weight: 700; color: #fff; }
    .insight-detail { font-size: 0.85rem; color: #90cdf4; }
    
    /* Filter bar */
    .filter-bar {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border: 1px solid #2d4a6b;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d1b2a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2d4a6b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4299e1;
    }
</style>
""", unsafe_allow_html=True)

# ── Data Loading and Preprocessing ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    """Load and preprocess Superstore data"""
    df = pd.read_csv('cleaned_train.csv')
    
    # Convert dates
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    # Extract date features
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Quarter'] = df['Order Date'].dt.quarter
    df['DayOfWeek'] = df['Order Date'].dt.day_name()
    df['Month_Year'] = df['Order Date'].dt.strftime('%b %Y')
    df['Year_Month'] = df['Order Date'].dt.to_period('M')
    df['Year_Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    
    # Calculate shipping time
    df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    # State mapping for map
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
    
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# ── Sidebar Filters ────────────────────────────────────────────────────────
st.sidebar.title("🎯 Dashboard Filters")
st.sidebar.markdown("---")

# Date range filter
min_date = df['Order Date'].min()
max_date = df['Order Date'].max()
date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['Order Date'] >= pd.Timestamp(start_date)) & (df['Order Date'] <= pd.Timestamp(end_date))
else:
    mask = pd.Series([True] * len(df))

# Categorical filters
col1, col2 = st.sidebar.columns(2)

with col1:
    selected_regions = st.multiselect(
        "🌎 Region",
        options=sorted(df['Region'].unique()),
        default=[]
    )
    
    selected_segments = st.multiselect(
        "👥 Segment",
        options=sorted(df['Segment'].unique()),
        default=[]
    )

with col2:
    selected_categories = st.multiselect(
        "📦 Category",
        options=sorted(df['Category'].unique()),
        default=[]
    )
    
    selected_ship_modes = st.multiselect(
        "🚚 Ship Mode",
        options=sorted(df['Ship Mode'].unique()),
        default=[]
    )

# Apply filters
if selected_regions:
    mask &= df['Region'].isin(selected_regions)
if selected_categories:
    mask &= df['Category'].isin(selected_categories)
if selected_segments:
    mask &= df['Segment'].isin(selected_segments)
if selected_ship_modes:
    mask &= df['Ship Mode'].isin(selected_ship_modes)

filtered_df = df[mask].copy()

# Quick stats in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Total Records", f"{len(filtered_df):,}")
st.sidebar.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
st.sidebar.metric("Unique Orders", f"{filtered_df['Order ID'].nunique():,}")
st.sidebar.metric("Unique Customers", f"{filtered_df['Customer ID'].nunique():,}")

if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
    st.stop()

# ── Main Dashboard ─────────────────────────────────────────────────────────
st.title("📊 Superstore Sales Analytics Dashboard")
st.markdown(f"*Analyzing {len(filtered_df):,} transactions from {filtered_df['Order Date'].min().strftime('%B %Y')} to {filtered_df['Order Date'].max().strftime('%B %Y')}*")

# ── KPI Row ────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_sales = filtered_df['Sales'].sum()
total_orders = filtered_df['Order ID'].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0
total_customers = filtered_df['Customer ID'].nunique()
avg_shipping = filtered_df['Shipping_Days'].mean()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total Sales</div>
        <div class="metric-value">${total_sales:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📦 Total Orders</div>
        <div class="metric-value">{total_orders:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🧾 Avg Order Value</div>
        <div class="metric-value">${avg_order_value:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">👥 Unique Customers</div>
        <div class="metric-value">{total_customers:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🚚 Avg Shipping</div>
        <div class="metric-value">{avg_shipping:.1f} days</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Sales Overview ─────────────────────────────────────────────────────────
st.header("📈 Sales Overview")

tab1, tab2, tab3 = st.tabs(["📅 Time Series", "🏷️ Category Analysis", "🌍 Geographic"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Year-over-Year Monthly Comparison
        monthly_sales = filtered_df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
        monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(day=1))
        monthly_sales = monthly_sales.sort_values('Date')
        
        fig_monthly = px.line(
            monthly_sales,
            x='Date',
            y='Sales',
            color='Year',
            title='Monthly Sales by Year (Year-over-Year Comparison)',
            markers=True,
            color_discrete_sequence=['#4299e1', '#48bb78', '#ed8936', '#9f7aea']
        )
        fig_monthly.update_traces(
            line_width=3,
            marker=dict(size=8),
            hovertemplate='<b>%{x|%B %Y}</b><br>Sales: $%{y:,.2f}<extra></extra>'
        )
        fig_monthly.update_layout(
            xaxis_title='',
            yaxis_title='Sales ($)',
            height=400,
            hovermode='x unified',
            xaxis=dict(
                tickformat='%b %Y',
                tickangle=-45
            )
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Quarterly trend
        quarterly_sales = filtered_df.groupby(['Year', 'Quarter'])['Sales'].sum().reset_index()
        quarterly_sales['Quarter_Label'] = quarterly_sales['Year'].astype(str) + '-Q' + quarterly_sales['Quarter'].astype(str)
        quarterly_sales = quarterly_sales.sort_values(['Year', 'Quarter'])
        
        fig_quarterly = px.bar(
            quarterly_sales,
            x='Quarter_Label',
            y='Sales',
            title='Quarterly Sales Performance',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_quarterly.update_traces(
            hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>'
        )
        fig_quarterly.update_layout(
            xaxis_title='',
            yaxis_title='Sales ($)',
            height=400,
            coloraxis_showscale=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_quarterly, use_container_width=True)

with tab2:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category distribution
        cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        
        fig_cat = px.pie(
            cat_sales,
            values='Sales',
            names='Category',
            title='Sales by Category',
            color_discrete_sequence=['#1e3a5f', '#2b6cb0', '#4299e1'],
            hole=0.4
        )
        fig_cat.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>'
        )
        fig_cat.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Top sub-categories
        subcat_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
        subcat_sales = subcat_sales.nlargest(10, 'Sales')
        
        fig_subcat = px.bar(
            subcat_sales,
            x='Sales',
            y='Sub-Category',
            orientation='h',
            title='Top 10 Sub-Categories',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_subcat.update_traces(
            hovertemplate='<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>'
        )
        fig_subcat.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Sales ($)',
            height=350,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_subcat, use_container_width=True)
    
    with col3:
        # Segment distribution
        seg_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        
        fig_seg = px.bar(
            seg_sales,
            x='Segment',
            y='Sales',
            title='Sales by Customer Segment',
            color='Segment',
            color_discrete_sequence=['#1e3a5f', '#2b6cb0', '#4299e1']
        )
        fig_seg.update_traces(
            hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>'
        )
        fig_seg.update_layout(
            xaxis_title='',
            yaxis_title='Sales ($)',
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig_seg, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # State-wise sales map
        state_sales = filtered_df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
        
        fig_map = px.choropleth(
            state_sales,
            locations='State Code',
            locationmode="USA-states",
            color='Sales',
            scope="usa",
            hover_name='State',
            hover_data={'Sales': ':,.2f', 'State Code': False},
            color_continuous_scale=[[0, '#0d1b2a'], [0.3, '#1e3a5f'], [0.6, '#2b6cb0'], [1, '#90cdf4']],
            title='Sales by State'
        )
        fig_map.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>Sales: $%{z:,.2f}<extra></extra>'
        )
        fig_map.update_layout(
            height=400,
            margin={"r":0,"t":30,"l":0,"b":0},
            coloraxis_colorbar=dict(title="Sales ($)", tickprefix="$", tickformat=",.0f")
        )
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col2:
        # Top states bar chart
        top_states = state_sales.nlargest(10, 'Sales')
        
        fig_top_states = px.bar(
            top_states,
            x='Sales',
            y='State',
            orientation='h',
            title='Top 10 States by Sales',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_top_states.update_traces(
            hovertemplate='<b>%{y}</b><br>Sales: $%{x:,.2f}<extra></extra>'
        )
        fig_top_states.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Sales ($)',
            height=400,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_top_states, use_container_width=True)

st.markdown("---")

# ── Shipping Analysis ──────────────────────────────────────────────────────
st.header("🚚 Shipping Performance")

col1, col2, col3 = st.columns(3)

with col1:
    # Shipping mode distribution (by sales)
    ship_sales = filtered_df.groupby('Ship Mode')['Sales'].sum().reset_index()
    
    fig_ship = px.pie(
        ship_sales,
        values='Sales',
        names='Ship Mode',
        title='Sales by Shipping Mode',
        color_discrete_sequence=['#1e3a5f', '#2b6cb0', '#4299e1', '#90cdf4']
    )
    fig_ship.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    )
    fig_ship.update_layout(height=350)
    st.plotly_chart(fig_ship, use_container_width=True)

with col2:
    # Average shipping days by ship mode
    ship_days = filtered_df.groupby('Ship Mode')['Shipping_Days'].mean().reset_index()
    ship_days = ship_days.sort_values('Shipping_Days', ascending=False)
    
    fig_ship_days = px.bar(
        ship_days,
        x='Ship Mode',
        y='Shipping_Days',
        title='Average Shipping Time by Mode',
        color='Shipping_Days',
        color_continuous_scale='Blues'
    )
    fig_ship_days.update_traces(
        hovertemplate='<b>%{x}</b><br>Avg Shipping: %{y:.1f} days<extra></extra>'
    )
    fig_ship_days.update_layout(
        xaxis_title='',
        yaxis_title='Days',
        height=350,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_ship_days, use_container_width=True)

with col3:
    # Order count by shipping mode
    ship_counts = filtered_df.groupby('Ship Mode')['Order ID'].nunique().reset_index()
    ship_counts.columns = ['Ship Mode', 'Order Count']
    ship_counts = ship_counts.sort_values('Order Count', ascending=False)
    
    fig_ship_counts = px.bar(
        ship_counts,
        x='Ship Mode',
        y='Order Count',
        title='Orders by Shipping Mode',
        color='Order Count',
        color_continuous_scale='Blues'
    )
    fig_ship_counts.update_traces(
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    )
    fig_ship_counts.update_layout(
        xaxis_title='',
        yaxis_title='Number of Orders',
        height=350,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_ship_counts, use_container_width=True)

st.markdown("---")

# ── Customer Analysis ──────────────────────────────────────────────────────
st.header("👥 Customer Insights")

col1, col2 = st.columns(2)

with col1:
    # Top customers
    customer_sales = filtered_df.groupby('Customer Name').agg({
        'Sales': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    customer_sales.columns = ['Customer', 'Total Sales', 'Order Count']
    customer_sales = customer_sales.nlargest(10, 'Total Sales')
    
    fig_customers = px.bar(
        customer_sales,
        x='Total Sales',
        y='Customer',
        orientation='h',
        title='Top 10 Customers by Sales',
        color='Total Sales',
        color_continuous_scale='Blues'
    )
    fig_customers.update_traces(
        hovertemplate='<b>%{y}</b><br>Total Sales: $%{x:,.2f}<br>Orders: %{customdata[0]:,}<extra></extra>',
        customdata=customer_sales[['Order Count']]
    )
    fig_customers.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Sales ($)',
        height=400,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_customers, use_container_width=True)

with col2:
    # Customer order frequency
    order_freq = filtered_df.groupby('Customer ID')['Order ID'].nunique().reset_index()
    order_freq.columns = ['Customer ID', 'Order Count']
    
    freq_dist = order_freq['Order Count'].value_counts().reset_index()
    freq_dist.columns = ['Orders per Customer', 'Number of Customers']
    freq_dist = freq_dist.sort_values('Orders per Customer')
    
    fig_freq = px.bar(
        freq_dist,
        x='Orders per Customer',
        y='Number of Customers',
        title='Customer Order Frequency Distribution',
        color='Number of Customers',
        color_continuous_scale='Blues'
    )
    fig_freq.update_traces(
        hovertemplate='<b>%{x} order(s) per customer</b><br>Number of Customers: %{y:,}<extra></extra>'
    )
    fig_freq.update_layout(
        xaxis_title='Number of Orders',
        yaxis_title='Number of Customers',
        height=400,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_freq, use_container_width=True)

st.markdown("---")

# ── Product Analysis ────────────────────────────────────────────────────────
st.header("📦 Product Analysis")

col1, col2 = st.columns(2)

with col1:
    # FIXED: Product sub-category performance scatter plot with correct hover
    subcat_stats = filtered_df.groupby('Sub-Category').agg({
        'Sales': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    subcat_stats['Avg Order Value'] = subcat_stats['Sales'] / subcat_stats['Order ID']
    subcat_stats = subcat_stats.sort_values('Sales', ascending=False).head(15)
    
    # Create a simple scatter plot with correct hover
    fig_subcat_perf = px.scatter(
        subcat_stats,
        x='Order ID',
        y='Sales',
        size='Avg Order Value',
        color='Sub-Category',
        title='Sub-Category Performance (Top 15)',
        hover_name='Sub-Category',
        hover_data={
            'Sales': ':,.2f',
            'Order ID': ':,.0f',
            'Avg Order Value': ':,.2f',
            'Sub-Category': False
        },
        size_max=30
    )
    
    fig_subcat_perf.update_traces(
        marker=dict(line=dict(width=1, color='white'))
    )
    
    fig_subcat_perf.update_layout(
        height=500,
        xaxis_title='Number of Orders',
        yaxis_title='Total Sales ($)',
        hoverlabel=dict(
            bgcolor='#0d1b2a',
            font_size=12,
            font_color='white'
        )
    )
    st.plotly_chart(fig_subcat_perf, use_container_width=True)

with col2:
    # Segment Correlation Analysis
    # Create monthly sales for each segment
    monthly_segment = filtered_df.groupby(['Year', 'Month', 'Segment'])['Sales'].sum().reset_index()
    monthly_segment['Date'] = pd.to_datetime(monthly_segment[['Year', 'Month']].assign(day=1))
    
    # Pivot for correlation
    segment_pivot = monthly_segment.pivot(index='Date', columns='Segment', values='Sales').fillna(0)
    segment_corr = segment_pivot.corr()
    
    # Create correlation heatmap
    fig_seg_corr = go.Figure(data=go.Heatmap(
        z=segment_corr.values,
        x=segment_corr.columns,
        y=segment_corr.index,
        colorscale=[[0, '#0d1b2a'], [0.25, '#1e3a5f'], [0.5, '#2b6cb0'], [0.75, '#4299e1'], [1, '#90cdf4']],
        zmin=0.5,
        zmax=1.0,
        text=[[f"{v:.3f}" for v in row] for row in segment_corr.values],
        texttemplate='%{text}',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig_seg_corr.update_layout(
        title='Segment Sales Correlation<br><sup>How customer segments move together over time</sup>',
        height=500,
        xaxis_title='',
        yaxis_title=''
    )
    st.plotly_chart(fig_seg_corr, use_container_width=True)
    
    # Find strongest and weakest correlations
    segs = segment_corr.columns.tolist()
    corr_pairs = []
    for i in range(len(segs)):
        for j in range(i+1, len(segs)):
            corr_pairs.append((segs[i], segs[j], segment_corr.iloc[i, j]))
    
    corr_pairs.sort(key=lambda x: x[2], reverse=True)
    strongest = corr_pairs[0] if corr_pairs else None
    weakest = corr_pairs[-1] if corr_pairs else None
    
    col_a, col_b = st.columns(2)
    with col_a:
        if strongest:
            st.markdown(f"""
            <div class="insight-card good" style="margin-top: 10px;">
                <div class="insight-icon">📈</div>
                <div class="insight-label">Strongest Correlation</div>
                <div class="insight-value">{strongest[0]} & {strongest[1]}</div>
                <div class="insight-detail">r = <strong>{strongest[2]:.3f}</strong> — These segments move together. Campaigns that boost one will likely lift the other.</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_b:
        if weakest:
            st.markdown(f"""
            <div class="insight-card warn" style="margin-top: 10px;">
                <div class="insight-icon">📉</div>
                <div class="insight-label">Weakest Correlation</div>
                <div class="insight-value">{weakest[0]} & {weakest[1]}</div>
                <div class="insight-detail">r = <strong>{weakest[2]:.3f}</strong> — These segments behave independently. Tailored strategies recommended.</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ── Regional Analysis ──────────────────────────────────────────────────────
st.header("🌎 Regional Performance")

col1, col2 = st.columns(2)

with col1:
    # Region performance
    region_stats = filtered_df.groupby('Region').agg({
        'Sales': 'sum',
        'Order ID': 'nunique',
        'Customer ID': 'nunique'
    }).reset_index()
    
    fig_region = px.bar(
        region_stats,
        x='Region',
        y='Sales',
        title='Sales by Region',
        color='Sales',
        color_continuous_scale='Blues'
    )
    fig_region.update_traces(
        hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.2f}<br>Orders: %{customdata[0]:,.0f}<br>Customers: %{customdata[1]:,.0f}<extra></extra>',
        customdata=region_stats[['Order ID', 'Customer ID']]
    )
    fig_region.update_layout(
        xaxis_title='',
        yaxis_title='Sales ($)',
        height=400,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    # Region vs Category
    region_cat = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
    
    fig_region_cat = px.bar(
        region_cat,
        x='Region',
        y='Sales',
        color='Category',
        title='Sales by Region and Category',
        barmode='group',
        color_discrete_sequence=['#1e3a5f', '#2b6cb0', '#4299e1']
    )
    fig_region_cat.update_traces(
        hovertemplate='<b>%{x}</b><br>Category: %{fullData.name}<br>Sales: $%{y:,.2f}<extra></extra>'
    )
    fig_region_cat.update_layout(
        xaxis_title='',
        yaxis_title='Sales ($)',
        height=400,
        legend_title='Category'
    )
    st.plotly_chart(fig_region_cat, use_container_width=True)

st.markdown("---")

# ── City Performance Table ─────────────────────────────────────────────────
st.header("🏙️ Top Cities by Sales")

city_stats = filtered_df.groupby('City').agg({
    'Sales': 'sum',
    'Order ID': 'nunique',
    'Customer ID': 'nunique'
}).reset_index()

city_stats.columns = ['City', 'Total Sales', 'Orders', 'Customers']
city_stats['Avg Order Value'] = city_stats['Total Sales'] / city_stats['Orders']
city_stats = city_stats.nlargest(20, 'Total Sales').reset_index(drop=True)
city_stats.index = range(1, len(city_stats) + 1)

# Format for display
display_df = city_stats.copy()
display_df['Total Sales'] = display_df['Total Sales'].apply('${:,.2f}'.format)
display_df['Avg Order Value'] = display_df['Avg Order Value'].apply('${:,.2f}'.format)

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    column_config={
        "City": "City",
        "Total Sales": "Total Sales",
        "Orders": "Orders",
        "Customers": "Customers",
        "Avg Order Value": "Avg Order"
    }
)

# ── Download filtered data ─────────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns([2, 2, 2])

with col2:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"superstore_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.8rem; padding: 20px;">
    📊 Superstore Sales Analytics Dashboard • Built with Streamlit
</div>
""", unsafe_allow_html=True)
