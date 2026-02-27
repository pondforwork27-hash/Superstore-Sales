import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Geographic Sales Insights",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Enhanced CSS with animations and better responsiveness ─────────────────
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #0a0f1a 0%, #0f1a2f 100%);
    }
    
    /* Animated filter bar */
    .filter-bar {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 40%, #1e3a5f 100%);
        border: 1px solid #2d4a6b;
        border-bottom: 1px solid rgba(66,153,225,0.25);
        border-radius: 0 0 20px 20px;
        padding: 16px 24px 12px 24px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.55);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .filter-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: shimmer 3s infinite;
        pointer-events: none;
    }
    
    @keyframes shimmer {
        100% { left: 100%; }
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
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(66,153,225,0.1) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-trend {
        font-size: 0.8rem;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Enhanced insight cards */
    .insight-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border-left: 4px solid #4299e1;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        color: #f0f0f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    
    .insight-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(66,153,225,0.05));
        pointer-events: none;
    }
    
    .insight-card.warn { border-left-color: #ed8936; }
    .insight-card.good { border-left-color: #48bb78; }
    .insight-card.alert { border-left-color: #e94560; }
    
    .insight-icon {
        font-size: 1.5rem;
        margin-bottom: 8px;
    }
    
    .insight-label {
        font-size: 0.75rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    
    .insight-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 6px;
    }
    
    .insight-detail {
        font-size: 0.85rem;
        color: #90cdf4;
        line-height: 1.5;
    }
    
    /* Animated pills */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #1e3a5f, #2d4a6b);
        border: 1px solid #4299e1;
        border-radius: 30px;
        padding: 6px 14px;
        font-size: 0.8rem;
        color: #e2f0fb;
        transition: all 0.2s ease;
        animation: pillPop 0.3s ease;
    }
    
    @keyframes pillPop {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .pill:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(66,153,225,0.3);
        background: linear-gradient(135deg, #2d4a6b, #1e3a5f);
    }
    
    .pill.state {
        background: linear-gradient(135deg, #97266d, #b83280);
        border-color: #f687b3;
    }
    
    /* Responsive table */
    .dataframe {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
        border: 1px solid #2d4a6b;
        border-radius: 16px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #1e3a5f;
        color: #fff;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 12px 16px;
        border-bottom: 2px solid #4299e1;
    }
    
    .dataframe td {
        padding: 10px 16px;
        color: #e2e8f0;
        border-bottom: 1px solid #2d4a6b;
    }
    
    .dataframe tr:hover td {
        background: rgba(66,153,225,0.1);
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: #4299e1 transparent transparent transparent !important;
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

# ── State Mapping ─────────────────────────────────────────────────────────────
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
abbrev_to_state = {v: k for k, v in us_state_to_abbrev.items()}

@st.cache_data(ttl=3600, show_spinner="Loading sales data...")
def load_data():
    """Load and preprocess sales data with caching"""
    df = pd.read_csv('cleaned_train.csv')
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    df['Month_Name'] = df['Order Date'].dt.strftime('%b %Y')
    
    # Add derived metrics
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    df['Order_Value'] = df['Sales'] / df['Quantity']
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Data file not found. Please ensure 'cleaned_train.csv' is in the current directory.")
    st.stop()

# ── Session state initialization ──────────────────────────────────────────────
defaults = {
    'clicked_state': None,
    'clicked_city': None,
    'sel_region': [],
    'sel_category': [],
    'sel_segment': [],
    'date_range': None,
    'view_mode': 'overview',
    'chart_animations': True
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Title with dynamic subtitle ──────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence Dashboard")
st.caption("Interactive analytics for strategic decision-making • Last updated: " + 
           datetime.now().strftime("%B %d, %Y"))

# ── Filter Bar with improved UX ──────────────────────────────────────────────
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        region_opts = sorted(df['Region'].unique().tolist())
        sel_region = st.multiselect(
            "🌎 Region",
            region_opts,
            default=st.session_state.sel_region,
            placeholder="All regions",
            help="Filter by geographic region"
        )
    
    with col2:
        category_opts = sorted(df['Category'].unique().tolist())
        sel_category = st.multiselect(
            "📦 Category",
            category_opts,
            default=st.session_state.sel_category,
            placeholder="All categories",
            help="Filter by product category"
        )
    
    with col3:
        segment_opts = sorted(df['Segment'].unique().tolist())
        sel_segment = st.multiselect(
            "👥 Segment",
            segment_opts,
            default=st.session_state.sel_segment,
            placeholder="All segments",
            help="Filter by customer segment"
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Clear All", use_container_width=True, type="secondary"):
            st.session_state.sel_region = []
            st.session_state.sel_category = []
            st.session_state.sel_segment = []
            st.session_state.clicked_state = None
            st.session_state.clicked_city = None
            st.rerun()
    
    # Update session state
    st.session_state.sel_region = list(sel_region)
    st.session_state.sel_category = list(sel_category)
    st.session_state.sel_segment = list(sel_segment)
    
    # Active filters display
    active_filters = []
    if sel_region:
        active_filters.extend([f"🌎 {r}" for r in sel_region])
    if sel_category:
        active_filters.extend([f"📦 {c}" for c in sel_category])
    if sel_segment:
        active_filters.extend([f"👥 {s}" for s in sel_segment])
    if st.session_state.clicked_state:
        active_filters.append(f"📍 {st.session_state.clicked_state}")
    
    if active_filters:
        filters_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">'
        for filter_text in active_filters:
            filters_html += f'<span class="pill">{filter_text}</span>'
        filters_html += '</div>'
        st.markdown(filters_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ── Build filtered dataframe with progress indication ───────────────────────
with st.spinner("Applying filters..."):
    mask = pd.Series([True] * len(df), index=df.index)
    if sel_region:
        mask &= df['Region'].isin(sel_region)
    if sel_category:
        mask &= df['Category'].isin(sel_category)
    if sel_segment:
        mask &= df['Segment'].isin(sel_segment)
    if st.session_state.clicked_state:
        mask &= df['State'] == st.session_state.clicked_state
    if st.session_state.clicked_city:
        mask &= df['City'] == st.session_state.clicked_city
    
    filtered_df = df[mask].copy()

if filtered_df.empty:
    st.warning("⚠️ No data matches the current filter combination. Try adjusting your selections.")
    st.stop()

# ── Quick Stats Row with enhanced metrics ───────────────────────────────────
st.markdown("### 📊 Key Performance Indicators")

# Calculate metrics
total_sales = filtered_df['Sales'].sum()
total_orders = filtered_df['Order ID'].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0
total_profit = filtered_df['Profit'].sum()
avg_margin = (filtered_df['Profit'].sum() / filtered_df['Sales'].sum() * 100) if total_sales > 0 else 0

# YoY comparison (if applicable)
current_year = filtered_df['Year'].max()
prev_year_sales = filtered_df[filtered_df['Year'] == current_year - 1]['Sales'].sum()
yoy_growth = ((total_sales - prev_year_sales) / prev_year_sales * 100) if prev_year_sales > 0 else 0

cols = st.columns(4)
metrics = [
    (f"${total_sales:,.0f}", "Total Sales", f"{yoy_growth:+.1f}% vs last year", "💰"),
    (f"{total_orders:,}", "Total Orders", f"{len(filtered_df):,} items", "📦"),
    (f"${avg_order_value:,.0f}", "Avg Order Value", f"{filtered_df['Quantity'].mean():.1f} items/order", "🧾"),
    (f"${total_profit:,.0f}", "Total Profit", f"{avg_margin:.1f}% margin", "💎")
]

for col, (value, label, trend, icon) in zip(cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <span class="metric-label">{label}</span>
                <span style="font-size: 1.5rem;">{icon}</span>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-trend">
                <span style="color: {'#48bb78' if '+' in trend else '#e94560' if '-' in trend else '#a0aec0'}">
                    {trend}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Map Section with enhanced interactivity ─────────────────────────────────
st.subheader("📍 Geographic Sales Distribution")

map_col1, map_col2 = st.columns([3, 1])

with map_col1:
    # Prepare map data
    all_state_sales = df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
    
    fig_map = px.choropleth(
        all_state_sales,
        locations='State Code',
        locationmode="USA-states",
        color='Sales',
        scope="usa",
        hover_name='State',
        color_continuous_scale=[[0, '#0d1b2a'], [0.3, '#1e3a5f'], [0.6, '#2b6cb0'], [1, '#90cdf4']],
        labels={'Sales': 'Total Sales ($)'}
    )
    
    fig_map.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Sales: $%{z:,.0f}<extra></extra>",
        marker_line_color='#1e3a5f',
        marker_line_width=1
    )
    
    # Highlight selected state
    if st.session_state.clicked_state:
        hl = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]
        if not hl.empty:
            fig_map.add_trace(go.Choropleth(
                locations=hl['State Code'],
                z=[1],
                locationmode="USA-states",
                colorscale=[[0, "rgba(233,69,96,0)"], [1, "rgba(233,69,96,0)"]],
                showscale=False,
                marker_line_color="#e94560",
                marker_line_width=3,
                hoverinfo='skip'
            ))
    
    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(
            title="Sales ($)",
            tickprefix="$",
            thickness=15,
            len=0.7,
            bgcolor='rgba(13,27,42,0.8)',
            tickfont=dict(color='white')
        ),
        height=500
    )
    
    map_event = st.plotly_chart(
        fig_map,
        use_container_width=True,
        on_select="rerun",
        key="choropleth_map",
        config={'displayModeBar': False}
    )

with map_col2:
    st.markdown("### 📌 Map Controls")
    
    if st.session_state.clicked_state:
        st.info(f"📍 Currently viewing: **{st.session_state.clicked_state}**")
        if st.button("🗑️ Clear State Filter", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()
    
    # Top states list
    st.markdown("### 🏆 Top States")
    top_states = all_state_sales.nlargest(5, 'Sales')[['State', 'Sales']]
    for idx, row in top_states.iterrows():
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; padding: 8px; 
                    border-bottom: 1px solid #2d4a6b;">
            <span>{idx+1}. {row['State']}</span>
            <span style="color: #90cdf4;">${row['Sales']:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Map insight
    top_state = all_state_sales.nlargest(1, 'Sales').iloc[0]
    st.markdown(f"""
    <div class="insight-card" style="margin-top: 16px;">
        <div class="insight-icon">💡</div>
        <div class="insight-label">Map Insight</div>
        <div class="insight-value">{top_state['State']}</div>
        <div class="insight-detail">
            Leads all states with ${top_state['Sales']:,.0f} in sales
        </div>
    </div>
    """, unsafe_allow_html=True)

# Handle map clicks
if map_event and map_event.selection and map_event.selection.get("points"):
    pt = map_event.selection["points"][0]
    clicked_abbrev = pt.get("location")
    if clicked_abbrev:
        new_state = abbrev_to_state.get(clicked_abbrev)
        if new_state and new_state != st.session_state.clicked_state:
            st.session_state.clicked_state = new_state
            st.rerun()
        elif new_state == st.session_state.clicked_state:
            st.session_state.clicked_state = None
            st.rerun()

st.markdown("---")

# ── Performance Breakdown with tabs ─────────────────────────────────────────
st.subheader("📈 Performance Analytics")

tab1, tab2, tab3 = st.tabs(["📊 Category Analysis", "👥 Segment Insights", "📅 Time Trends"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Category sales
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
            hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
        )
        fig_cat.update_layout(
            showlegend=False,
            margin=dict(t=40, b=0, l=0, r=0),
            height=350
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Sub-category ranking
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
            hovertemplate='<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>'
        )
        fig_subcat.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis=dict(title='Sales ($)', tickprefix='$'),
            coloraxis_showscale=False,
            height=350,
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_subcat, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment performance
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
            hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
        )
        fig_seg.update_layout(
            showlegend=False,
            xaxis=dict(title=''),
            yaxis=dict(title='Sales ($)', tickprefix='$'),
            height=350,
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_seg, use_container_width=True)
    
    with col2:
        # Segment × Category heatmap
        seg_cat_pivot = filtered_df.pivot_table(
            values='Sales',
            index='Segment',
            columns='Category',
            aggfunc='sum',
            fill_value=0
        )
        
        fig_heat = go.Figure(data=go.Heatmap(
            z=seg_cat_pivot.values,
            x=seg_cat_pivot.columns,
            y=seg_cat_pivot.index,
            colorscale='Blues',
            text=[[f"${v:,.0f}" for v in row] for row in seg_cat_pivot.values],
            texttemplate='%{text}',
            textfont=dict(size=10, color='white'),
            hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Sales: $%{z:,.0f}<extra></extra>'
        ))
        
        fig_heat.update_layout(
            title='Segment × Category Matrix',
            height=350,
            margin=dict(t=40, b=0, l=0, r=0),
            xaxis=dict(title=''),
            yaxis=dict(title='')
        )
        st.plotly_chart(fig_heat, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trend
        monthly_sales = filtered_df.groupby('Month_Name')['Sales'].sum().reset_index()
        
        fig_trend = px.line(
            monthly_sales,
            x='Month_Name',
            y='Sales',
            title='Monthly Sales Trend',
            markers=True
        )
        fig_trend.update_traces(
            line_color='#4299e1',
            line_width=3,
            marker=dict(size=8, color='#90cdf4', line=dict(color='white', width=1))
        )
        fig_trend.update_layout(
            xaxis_tickangle=-45,
            yaxis=dict(title='Sales ($)', tickprefix='$'),
            height=350,
            margin=dict(t=40, b=80, l=0, r=0)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Quarterly comparison
        quarterly_sales = filtered_df.groupby('Quarter')['Sales'].sum().reset_index()
        
        fig_quarter = px.bar(
            quarterly_sales,
            x='Quarter',
            y='Sales',
            title='Quarterly Performance',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_quarter.update_traces(
            hovertemplate='<b>Q%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
        )
        fig_quarter.update_layout(
            xaxis=dict(title=''),
            yaxis=dict(title='Sales ($)', tickprefix='$'),
            coloraxis_showscale=False,
            height=350,
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_quarter, use_container_width=True)

st.markdown("---")

# ── Cities Table with export ────────────────────────────────────────────────
st.subheader("🏙️ City Performance")

# City-level analysis
city_stats = filtered_df.groupby('City').agg({
    'Sales': 'sum',
    'Order ID': 'nunique',
    'Profit': 'sum',
    'Quantity': 'sum'
}).reset_index()

city_stats.columns = ['City', 'Total Sales', 'Order Count', 'Total Profit', 'Units Sold']
city_stats['Avg Order Value'] = city_stats['Total Sales'] / city_stats['Order Count']
city_stats['Profit Margin'] = (city_stats['Total Profit'] / city_stats['Total Sales'] * 100).round(1)

# Sort and format
city_stats = city_stats.nlargest(20, 'Total Sales').reset_index(drop=True)
city_stats.index = range(1, len(city_stats) + 1)

# Format columns
display_df = city_stats.copy()
display_df['Total Sales'] = display_df['Total Sales'].apply('${:,.0f}'.format)
display_df['Total Profit'] = display_df['Total Profit'].apply('${:,.0f}'.format)
display_df['Avg Order Value'] = display_df['Avg Order Value'].apply('${:,.0f}'.format)
display_df['Profit Margin'] = display_df['Profit Margin'].apply('{:.1f}%'.format)

# Add export button
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("📥 Export to CSV", use_container_width=True):
        csv = city_stats.to_csv(index=False)
        st.download_button(
            label="Download",
            data=csv,
            file_name=f"city_sales_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Display table
st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    column_config={
        "City": st.column_config.TextColumn("City", width="medium"),
        "Total Sales": st.column_config.TextColumn("Total Sales", width="small"),
        "Order Count": st.column_config.NumberColumn("Orders", width="small", format="%d"),
        "Total Profit": st.column_config.TextColumn("Profit", width="small"),
        "Units Sold": st.column_config.NumberColumn("Units", width="small", format="%d"),
        "Avg Order Value": st.column_config.TextColumn("Avg Order", width="small"),
        "Profit Margin": st.column_config.TextColumn("Margin", width="small")
    }
)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.8rem; padding: 20px;">
    🗺️ Regional Sales Intelligence Dashboard • Built with Streamlit • Data updates in real-time
</div>
""", unsafe_allow_html=True)
