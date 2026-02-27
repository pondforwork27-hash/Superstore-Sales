import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Geographic Sales Insights", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.insight-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-left: 4px solid #e94560;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    color: #f0f0f0;
}
.insight-card .icon { font-size: 1.4rem; }
.insight-card .label {
    font-size: 0.75rem;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.insight-card .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
}
.insight-card .detail {
    font-size: 0.85rem;
    color: #90cdf4;
    margin-top: 4px;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 8px;
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

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")
selected_region   = st.sidebar.multiselect("Region",   df['Region'].unique(),   default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
selected_segment  = st.sidebar.multiselect("Segment",  df['Segment'].unique(),  default=df['Segment'].unique())

filtered_df = df[
    df['Region'].isin(selected_region) &
    df['Category'].isin(selected_category) &
    df['Segment'].isin(selected_segment)
]

# ── DERIVED METRICS ───────────────────────────────────────────────────────────
state_sales   = filtered_df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
cat_sales     = filtered_df.groupby('Category')['Sales'].sum().reset_index()
subcat_sales  = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
region_sales  = filtered_df.groupby('Region')['Sales'].sum().reset_index()
segment_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
city_sales    = filtered_df.groupby('City')['Sales'].sum().reset_index()
monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index().sort_values('Month')

total_sales    = filtered_df['Sales'].sum()
total_orders   = filtered_df['Order ID'].nunique()
avg_order_val  = total_sales / total_orders if total_orders else 0
top_state      = state_sales.sort_values('Sales', ascending=False).iloc[0]
top_city_row   = city_sales.sort_values('Sales', ascending=False).iloc[0]
top_cat_row    = cat_sales.sort_values('Sales', ascending=False).iloc[0]
top_subcat_row = subcat_sales.sort_values('Sales', ascending=False).iloc[0]
top_region_row = region_sales.sort_values('Sales', ascending=False).iloc[0]
top_seg_row    = segment_sales.sort_values('Sales', ascending=False).iloc[0]

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Interactive insights across geography, category, and customer segment.")

# ── KPI ROW ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Sales",    f"${total_sales:,.0f}")
k2.metric("📦 Total Orders",   f"{total_orders:,}")
k3.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")
k4.metric("🏆 #1 Region",      top_region_row['Region'])

st.markdown("---")

# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State")
fig_map = px.choropleth(
    state_sales,
    locations='State Code', locationmode="USA-states",
    color='Sales', scope="usa", hover_name='State',
    color_continuous_scale="Blues",
    labels={'Sales': 'Total Sales ($)'}
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, geo_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_map, use_container_width=True)

# Narrative insight under the map
state_share = (top_state['Sales'] / total_sales * 100) if total_sales else 0
st.markdown(f"""
<div class="insight-card">
  <div class="icon">📌</div>
  <div class="label">Map Insight</div>
  <div class="value">{top_state['State']} leads all states</div>
  <div class="detail">
    Generating <strong>${top_state['Sales']:,.0f}</strong> in sales —
    that's <strong>{state_share:.1f}%</strong> of total revenue across your current filter selection.
    Focus distribution and logistics investments here for maximum impact.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── INSIGHT CARDS ROW ─────────────────────────────────────────────────────────
st.header("💡 Key Business Insights")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">🏅</div>
      <div class="label">Top State</div>
      <div class="value">{top_state['State']}</div>
      <div class="detail">${top_state['Sales']:,.0f} in sales ({state_share:.1f}% of total)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">🏙️</div>
      <div class="label">Top City</div>
      <div class="value">{top_city_row['City']}</div>
      <div class="detail">${top_city_row['Sales']:,.0f} — highest city-level revenue driver</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">📦</div>
      <div class="label">Dominant Category</div>
      <div class="value">{top_cat_row['Category']}</div>
      <div class="detail">${top_cat_row['Sales']:,.0f} — prime candidate for increased marketing spend</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">🔖</div>
      <div class="label">Top Sub-Category</div>
      <div class="value">{top_subcat_row['Sub-Category']}</div>
      <div class="detail">${top_subcat_row['Sales']:,.0f} — highest-earning product sub-group</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">👥</div>
      <div class="label">Leading Segment</div>
      <div class="value">{top_seg_row['Segment']}</div>
      <div class="detail">${top_seg_row['Sales']:,.0f} — your most valuable customer segment</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">🌎</div>
      <div class="label">Top Region</div>
      <div class="value">{top_region_row['Region']}</div>
      <div class="detail">${top_region_row['Sales']:,.0f} — strongest regional market</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── CHARTS ROW ────────────────────────────────────────────────────────────────
st.header("📊 Performance Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Sales")
    top_states_df = state_sales.sort_values('Sales', ascending=False).head(10)
    fig_bar = px.bar(
        top_states_df, x='Sales', y='State', orientation='h',
        color='Sales', color_continuous_scale='Blues',
        labels={'Sales': 'Total Sales ($)'}
    )
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Category & Segment Mix")
    fig_pie = px.sunburst(
        filtered_df.groupby(['Category', 'Segment'])['Sales'].sum().reset_index(),
        path=['Category', 'Segment'], values='Sales',
        color='Sales', color_continuous_scale='Blues'
    )
    fig_pie.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ── TREND + REGION ────────────────────────────────────────────────────────────
st.header("📈 Sales Trends & Regional Deep Dive")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Monthly Sales Trend")
    fig_line = px.line(
        monthly_sales, x='Month', y='Sales',
        markers=True,
        labels={'Sales': 'Total Sales ($)', 'Month': ''}
    )
    fig_line.update_traces(line_color='#4299e1', line_width=2.5)
    fig_line.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_line, use_container_width=True)

    # Trend narrative
    if len(monthly_sales) >= 2:
        first_m = monthly_sales.iloc[0]['Sales']
        last_m  = monthly_sales.iloc[-1]['Sales']
        pct_chg = ((last_m - first_m) / first_m * 100) if first_m else 0
        trend_word = "grown" if pct_chg > 0 else "declined"
        st.markdown(f"""
        <div class="insight-card">
          <div class="icon">📈</div>
          <div class="label">Trend Insight</div>
          <div class="value">{abs(pct_chg):.1f}% {'▲' if pct_chg > 0 else '▼'} over period</div>
          <div class="detail">
            Sales have <strong>{trend_word} by {abs(pct_chg):.1f}%</strong> from the first to the last
            recorded month in this selection. {'Momentum is positive — consider scaling inventory.' if pct_chg > 0 else 'Investigate demand drivers and revisit pricing strategy.'}
          </div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    st.subheader("Sub-Category Sales Ranking")
    subcat_sorted = subcat_sales.sort_values('Sales', ascending=False)
    fig_subcat = px.bar(
        subcat_sorted, x='Sub-Category', y='Sales',
        color='Sales', color_continuous_scale='Teal',
        labels={'Sales': 'Total Sales ($)'}
    )
    fig_subcat.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig_subcat, use_container_width=True)

    # Bottom sub-category insight
    bottom_subcat = subcat_sorted.iloc[-1]
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">⚠️</div>
      <div class="label">Underperformer Alert</div>
      <div class="value">{bottom_subcat['Sub-Category']}</div>
      <div class="detail">
        Only <strong>${bottom_subcat['Sales']:,.0f}</strong> in sales — the lowest sub-category.
        Review pricing, promotion, and placement strategy or consider deprioritizing stock.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── REGIONAL COMPARISON ───────────────────────────────────────────────────────
st.header("🌎 Region vs. Segment Matrix")

region_seg = filtered_df.groupby(['Region', 'Segment'])['Sales'].sum().reset_index()
fig_grouped = px.bar(
    region_seg, x='Region', y='Sales', color='Segment',
    barmode='group', color_discrete_sequence=px.colors.qualitative.Set2,
    labels={'Sales': 'Total Sales ($)'}
)
st.plotly_chart(fig_grouped, use_container_width=True)

# Narrative
best_region_seg = region_seg.sort_values('Sales', ascending=False).iloc[0]
worst_region_seg = region_seg.sort_values('Sales').iloc[0]
st.markdown(f"""
<div class="insight-card">
  <div class="icon">🎯</div>
  <div class="label">Strategic Insight</div>
  <div class="value">Best combo: {best_region_seg['Region']} × {best_region_seg['Segment']}</div>
  <div class="detail">
    The <strong>{best_region_seg['Segment']}</strong> segment in the <strong>{best_region_seg['Region']}</strong> region
    delivers the highest sales at <strong>${best_region_seg['Sales']:,.0f}</strong>.
    Conversely, <strong>{worst_region_seg['Segment']}</strong> in <strong>{worst_region_seg['Region']}</strong> is the
    lowest-performing combination (${worst_region_seg['Sales']:,.0f}) — a clear opportunity for targeted growth campaigns.
  </div>
</div>
""", unsafe_allow_html=True)

# ── TOP CITIES TABLE ──────────────────────────────────────────────────────────
st.markdown("---")
st.header("🏙️ Top 10 Cities by Revenue")
top_cities = city_sales.sort_values('Sales', ascending=False).head(10).reset_index(drop=True)
top_cities.index += 1
top_cities['Sales'] = top_cities['Sales'].map('${:,.0f}'.format)
st.dataframe(top_cities, use_container_width=True)
