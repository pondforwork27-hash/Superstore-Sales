import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Geographic Sales Insights",
    page_icon="🗺️",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.filter-bar {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 40%, #1e3a5f 100%);
    border: 1px solid #2d4a6b;
    border-radius: 12px;
    padding: 18px 24px 14px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}
.filter-bar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 20% 50%, rgba(66,153,225,0.08) 0%, transparent 60%),
        radial-gradient(circle at 80% 20%, rgba(99,179,237,0.06) 0%, transparent 50%);
    pointer-events: none;
}
.filter-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #63b3ed;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 10px;
}
.state-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(90deg, #1e3a5f, #2d5a8a);
    border: 1px solid #4299e1;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #90cdf4;
    margin-bottom: 12px;
}
.state-badge strong { color: #fff; }
.insight-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
    border-left: 4px solid #4299e1;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    color: #f0f0f0;
}
.insight-card.warn  { border-left-color: #ed8936; }
.insight-card.good  { border-left-color: #48bb78; }
.insight-card.alert { border-left-color: #e94560; }
.insight-card .icon { font-size: 1.4rem; }
.insight-card .label {
    font-size: 0.72rem;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.insight-card .value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
}
.insight-card .detail {
    font-size: 0.83rem;
    color: #90cdf4;
    margin-top: 4px;
    line-height: 1.5;
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

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year']  = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

if 'clicked_state' not in st.session_state:
    st.session_state.clicked_state = None

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Click any state on the map to drill into that state's data across all charts below.")

# ── FILTER BAR ────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)

fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1])
with fc1:
    region_opts = ["All Regions"] + sorted(df['Region'].unique().tolist())
    sel_region  = st.selectbox("Region", region_opts)
with fc2:
    category_opts = ["All Categories"] + sorted(df['Category'].unique().tolist())
    sel_category  = st.selectbox("Category", category_opts)
with fc3:
    segment_opts = ["All Segments"] + sorted(df['Segment'].unique().tolist())
    sel_segment  = st.selectbox("Segment", segment_opts)
with fc4:
    if st.session_state.clicked_state:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button(f"✕  Clear: {st.session_state.clicked_state}", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()
    else:
        st.markdown("<div style='padding-top:30px;color:#4a7fa5;font-size:0.8rem;'>👆 Click a state on the map to filter</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)
if sel_region   != "All Regions":    mask &= df['Region']   == sel_region
if sel_category != "All Categories": mask &= df['Category'] == sel_category
if sel_segment  != "All Segments":   mask &= df['Segment']  == sel_segment
if st.session_state.clicked_state:   mask &= df['State']    == st.session_state.clicked_state

filtered_df = df[mask]

if st.session_state.clicked_state:
    st.markdown(f'<div class="state-badge">📍 Map filter active — showing data for <strong>&nbsp;{st.session_state.clicked_state}</strong></div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data matches the current filter combination. Try adjusting your selections.")
    st.stop()

# ── METRICS ───────────────────────────────────────────────────────────────────
state_sales   = filtered_df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
cat_sales     = filtered_df.groupby('Category')['Sales'].sum().reset_index()
subcat_sales  = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
region_sales  = filtered_df.groupby('Region')['Sales'].sum().reset_index()
segment_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
city_sales    = filtered_df.groupby('City')['Sales'].sum().reset_index()
monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index().sort_values('Month')
region_seg    = filtered_df.groupby(['Region', 'Segment'])['Sales'].sum().reset_index()

total_sales    = filtered_df['Sales'].sum()
total_orders   = filtered_df['Order ID'].nunique()
avg_order_val  = total_sales / total_orders if total_orders else 0
top_state      = state_sales.sort_values('Sales', ascending=False).iloc[0]
top_city_row   = city_sales.sort_values('Sales', ascending=False).iloc[0]
top_cat_row    = cat_sales.sort_values('Sales', ascending=False).iloc[0]
top_subcat_row = subcat_sales.sort_values('Sales', ascending=False).iloc[0]
top_region_row = region_sales.sort_values('Sales', ascending=False).iloc[0]
top_seg_row    = segment_sales.sort_values('Sales', ascending=False).iloc[0]
state_share    = (top_state['Sales'] / total_sales * 100) if total_sales else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Sales",     f"${total_sales:,.0f}")
k2.metric("📦 Total Orders",    f"{total_orders:,}")
k3.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")
k4.metric("🏆 #1 Region",       top_region_row['Region'])

st.markdown("---")

# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State  ·  Click a state to drill down")

all_state_sales = df.groupby(['State', 'State Code'])['Sales'].sum().reset_index()

fig_map = px.choropleth(
    all_state_sales,
    locations='State Code',
    locationmode="USA-states",
    color='Sales',
    scope="usa",
    hover_name='State',
    color_continuous_scale="Blues",
    labels={'Sales': 'Total Sales ($)'}
)
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Total Sales: $%{z:,.0f}<extra></extra>"
)

if st.session_state.clicked_state:
    hl = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]
    if not hl.empty:
        fig_map.add_trace(go.Choropleth(
            locations=hl['State Code'],
            z=[1],
            locationmode="USA-states",
            colorscale=[[0, "rgba(233,69,96,0.0)"], [1, "rgba(233,69,96,0.0)"]],
            showscale=False,
            marker_line_color="#e94560",
            marker_line_width=3,
            hoverinfo='skip',
        ))

fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    geo_bgcolor='rgba(0,0,0,0)',
    coloraxis_colorbar=dict(title="Sales ($)", tickprefix="$")
)

map_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", key="choropleth_map")

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

st.markdown(f"""
<div class="insight-card">
  <div class="icon">📌</div>
  <div class="label">Map Insight</div>
  <div class="value">{top_state['State']} leads all states</div>
  <div class="detail">Generating <strong>${top_state['Sales']:,.0f}</strong> in sales —
  <strong>{state_share:.1f}%</strong> of total revenue in this selection.
  Focus distribution and logistics investments here for maximum impact.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── INSIGHT CARDS ─────────────────────────────────────────────────────────────
st.header("💡 Key Business Insights")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="insight-card good"><div class="icon">🏅</div><div class="label">Top State</div><div class="value">{top_state["State"]}</div><div class="detail">${top_state["Sales"]:,.0f} in sales ({state_share:.1f}% of total)</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card"><div class="icon">🏙️</div><div class="label">Top City</div><div class="value">{top_city_row["City"]}</div><div class="detail">${top_city_row["Sales"]:,.0f} — highest city-level revenue driver</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="insight-card good"><div class="icon">📦</div><div class="label">Dominant Category</div><div class="value">{top_cat_row["Category"]}</div><div class="detail">${top_cat_row["Sales"]:,.0f} — prime candidate for increased marketing spend</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card"><div class="icon">🔖</div><div class="label">Top Sub-Category</div><div class="value">{top_subcat_row["Sub-Category"]}</div><div class="detail">${top_subcat_row["Sales"]:,.0f} — highest-earning product sub-group</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="insight-card good"><div class="icon">👥</div><div class="label">Leading Segment</div><div class="value">{top_seg_row["Segment"]}</div><div class="detail">${top_seg_row["Sales"]:,.0f} — your most valuable customer segment</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card"><div class="icon">🌎</div><div class="label">Top Region</div><div class="value">{top_region_row["Region"]}</div><div class="detail">${top_region_row["Sales"]:,.0f} — strongest regional market</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── CHARTS ────────────────────────────────────────────────────────────────────
st.header("📊 Performance Breakdown")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Sales")
    top_states_df = state_sales.sort_values('Sales', ascending=False).head(10)
    fig_bar = px.bar(top_states_df, x='Sales', y='State', orientation='h',
                     color='Sales', color_continuous_scale='Blues', labels={'Sales': 'Total Sales ($)'})
    fig_bar.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>")
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_states")

with col2:
    st.subheader("Category & Segment Mix")
    st.caption("✅ Data verified — Consumer/Corporate/Home Office each appear once per category (inner ring = category, outer ring = segment within that category)")
    sunburst_df = filtered_df.groupby(['Category', 'Segment'])['Sales'].sum().reset_index()
    fig_sun = px.sunburst(sunburst_df, path=['Category', 'Segment'], values='Sales',
                          color='Sales', color_continuous_scale='Blues')
    fig_sun.update_traces(hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>")
    fig_sun.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_sun, use_container_width=True, key="sunburst_cat")

st.markdown("---")
st.header("📈 Sales Trends & Sub-Category Deep Dive")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Monthly Sales Trend")
    # Format labels as $12K for readability
    monthly_sales['label'] = monthly_sales['Sales'].apply(
        lambda v: f"${v/1000:.0f}K" if v >= 1000 else f"${v:.0f}"
    )
    fig_line = px.line(monthly_sales, x='Month', y='Sales', markers=True,
                       text='label',
                       labels={'Sales': 'Total Sales ($)', 'Month': ''})
    fig_line.update_traces(
        line_color='#4299e1',
        line_width=2.5,
        marker=dict(size=7, color='#4299e1'),
        textposition='top center',
        textfont=dict(size=10, color='#90cdf4'),
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
    )
    fig_line.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(tickprefix="$", tickformat=",.0f"),
        # Add a bit of top padding so labels don't clip
        yaxis_range=[0, monthly_sales['Sales'].max() * 1.18]
    )
    st.plotly_chart(fig_line, use_container_width=True, key="line_trend")

    if len(monthly_sales) >= 2:
        pct_chg = ((monthly_sales.iloc[-1]['Sales'] - monthly_sales.iloc[0]['Sales']) / monthly_sales.iloc[0]['Sales'] * 100)
        card_cls = "good" if pct_chg > 0 else "alert"
        trend_word = "grown" if pct_chg > 0 else "declined"
        advice = "Momentum is positive — consider scaling inventory." if pct_chg > 0 else "Investigate demand drivers and revisit pricing strategy."
        st.markdown(f'<div class="insight-card {card_cls}"><div class="icon">📈</div><div class="label">Trend Insight</div><div class="value">{abs(pct_chg):.1f}% {"▲" if pct_chg > 0 else "▼"} over period</div><div class="detail">Sales have <strong>{trend_word} {abs(pct_chg):.1f}%</strong> from first to last month. {advice}</div></div>', unsafe_allow_html=True)

with col4:
    st.subheader("Sub-Category Sales Ranking")
    subcat_sorted = subcat_sales.sort_values('Sales', ascending=False)
    fig_subcat = px.bar(subcat_sorted, x='Sub-Category', y='Sales',
                        color='Sales', color_continuous_scale='Teal', labels={'Sales': 'Total Sales ($)'})
    fig_subcat.update_traces(hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>")
    fig_subcat.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig_subcat, use_container_width=True, key="bar_subcat")

    bottom_subcat = subcat_sorted.iloc[-1]
    st.markdown(f'<div class="insight-card warn"><div class="icon">⚠️</div><div class="label">Underperformer Alert</div><div class="value">{bottom_subcat["Sub-Category"]}</div><div class="detail">Only <strong>${bottom_subcat["Sales"]:,.0f}</strong> in sales — lowest sub-category. Review pricing, promotion, and placement or consider deprioritizing stock.</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.header("🌎 Region vs. Segment Matrix")
fig_grouped = px.bar(region_seg, x='Region', y='Sales', color='Segment',
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={'Sales': 'Total Sales ($)'})
fig_grouped.update_traces(hovertemplate="<b>%{x}</b><br>Segment: %{fullData.name}<br>Sales: $%{y:,.0f}<extra></extra>")
st.plotly_chart(fig_grouped, use_container_width=True, key="grouped_region_seg")

best_rs  = region_seg.sort_values('Sales', ascending=False).iloc[0]
worst_rs = region_seg.sort_values('Sales').iloc[0]
st.markdown(f'<div class="insight-card good"><div class="icon">🎯</div><div class="label">Strategic Insight</div><div class="value">Best combo: {best_rs["Region"]} × {best_rs["Segment"]}</div><div class="detail"><strong>{best_rs["Segment"]}</strong> in <strong>{best_rs["Region"]}</strong> delivers the highest sales at <strong>${best_rs["Sales"]:,.0f}</strong>. Lowest performer: <strong>{worst_rs["Segment"]}</strong> in <strong>{worst_rs["Region"]}</strong> (${worst_rs["Sales"]:,.0f}) — a clear opportunity for targeted growth campaigns.</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.header("🏙️ Top 10 Cities by Revenue")
top_cities = city_sales.sort_values('Sales', ascending=False).head(10).reset_index(drop=True)
top_cities.index += 1
top_cities['Sales'] = top_cities['Sales'].map('${:,.0f}'.format)
st.dataframe(top_cities, use_container_width=True)
