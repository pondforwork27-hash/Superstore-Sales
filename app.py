import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Geographic Sales Insights",
    page_icon="🗺️",
    layout="wide"
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#filter-spacer { display: block; }
.filter-bar {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 40%, #1e3a5f 100%);
    border: 1px solid #2d4a6b;
    border-bottom: 1px solid rgba(66,153,225,0.25);
    border-radius: 0 0 14px 14px;
    padding: 12px 20px 10px 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.55);
    position: relative; overflow: hidden;
}
.filter-bar label { color: #ffffff !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.filter-bar [data-baseweb="select"] input { color: #ffffff !important; }
.filter-bar [data-baseweb="select"] input::placeholder { color: #ffffff !important; opacity: 1 !important; }
.filter-bar [data-baseweb="select"] [class$="placeholder"],
.filter-bar [data-baseweb="select"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
[data-testid="stMultiSelect"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }

span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #1e3a5f, #2d5a8a) !important;
    border: 1px solid #4299e1 !important;
    border-radius: 20px !important;
    color: #e2f0fb !important;
}
span[data-baseweb="tag"] span { color: #e2f0fb !important; }
span[data-baseweb="tag"] [role="presentation"] svg { fill: #90cdf4 !important; }
[data-baseweb="select"] > div {
    background: rgba(13,27,42,0.85) !important;
    border: 1px solid #2d5a8a !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] > div:focus-within { border-color: #4299e1 !important; box-shadow: 0 0 0 2px rgba(66,153,225,0.25) !important; }
[data-baseweb="popover"] ul { background: #0d1b2a !important; border: 1px solid #2d5a8a !important; }
[data-baseweb="popover"] li { color: #cbd5e0 !important; }
[data-baseweb="popover"] li:hover { background: #1e3a5f !important; color: #fff !important; }
[data-baseweb="popover"] li[aria-selected="true"] { background: #1a3a6b !important; color: #90cdf4 !important; }

.filter-bar::before {
    content: ''; position: absolute; top:0; left:0; right:0; bottom:0;
    background: radial-gradient(circle at 15% 60%, rgba(66,153,225,0.07) 0%, transparent 55%),
                radial-gradient(circle at 85% 20%, rgba(99,179,237,0.05) 0%, transparent 45%);
    pointer-events: none;
}
.filter-title { font-size: 0.68rem; font-weight: 700; color: #63b3ed; text-transform: uppercase; letter-spacing: 0.13em; margin-bottom: 8px; }
.active-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; margin-bottom:2px; }
.pill { display:inline-flex; align-items:center; gap:5px; background:rgba(30,58,95,0.9); border:1px solid #2d5a8a; border-radius:16px; padding:3px 10px; font-size:0.73rem; color:#90cdf4; }
.pill.state { border-color:#e94560; color:#feb2b2; }
.state-badge { display:inline-flex; align-items:center; gap:8px; background:linear-gradient(90deg,#1e3a5f,#2d5a8a); border:1px solid #4299e1; border-radius:20px; padding:5px 14px; font-size:0.8rem; color:#90cdf4; margin-bottom:10px; }
.state-badge strong { color:#fff; }

.insight-card { background:linear-gradient(135deg,#0d1b2a 0%,#1b2a3b 100%); border-left:4px solid #4299e1; border-radius:8px; padding:14px 18px; margin-bottom:10px; color:#f0f0f0; }
.insight-card.warn  { border-left-color:#ed8936; }
.insight-card.good  { border-left-color:#48bb78; }
.insight-card.alert { border-left-color:#e94560; }
.insight-card .icon { font-size:1.3rem; }
.insight-card .label { font-size:0.7rem; color:#a0aec0; text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px; }
.insight-card .value { font-size:1.35rem; font-weight:700; color:#fff; }
.insight-card .detail { font-size:0.82rem; color:#90cdf4; margin-top:3px; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Sentinel + JS: true fixed-position filter ─────────────────────────────────
st.markdown('<span id="filter-sentinel"></span>', unsafe_allow_html=True)

import streamlit.components.v1 as _stc
_stc.html("""
<script>
(function () {
  var DONE = false;
  function fixFilter() {
    if (DONE) return;
    var sentinel = document.getElementById('filter-sentinel');
    if (!sentinel) return;
    var block = sentinel;
    var found = false;
    for (var i = 0; i < 12; i++) {
      if (!block.parentElement) return;
      block = block.parentElement;
      if (block.getAttribute('data-testid') === 'stVerticalBlock' && block.querySelector('.filter-bar')) { found = true; break; }
    }
    if (!found) return;
    if (block.getAttribute('data-filter-fixed') === '1') return;
    block.setAttribute('data-filter-fixed', '1');
    DONE = true;

    var spacer = document.createElement('div');
    spacer.id = 'filter-spacer';
    block.parentNode.insertBefore(spacer, block);

    function applyFixed() {
      var h = block.scrollHeight;
      spacer.style.height = h + 'px';
      var parentRect = block.parentElement.getBoundingClientRect();
      block.style.cssText = [
        'position:fixed', 'top:0', 'left:' + parentRect.left + 'px', 'width:' + parentRect.width + 'px',
        'z-index:9999', 'background:rgba(8,15,26,0.96)', 'backdrop-filter:blur(8px)', '-webkit-backdrop-filter:blur(8px)',
      ].join(';');
    }
    applyFixed();
    window.addEventListener('resize', applyFixed);
  }
  fixFilter();
  new MutationObserver(function(muts) { muts.forEach(function(m) { if (m.addedNodes.length) fixFilter(); }); }).observe(document.body, { childList: true, subtree: true });
})();
</script>
""", height=0)


# ── State Mapping ─────────────────────────────────────────────────────────────
us_state_to_abbrev = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
    "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO",
    "Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ",
    "New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH",
    "Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
    "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
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

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    'clicked_state': None,
    'clicked_city':  None,
    'sel_year':      [],
    'sel_region':    [],
    'sel_category':  [],
    'sel_segment':   [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Select filters to update all charts instantly. Click a state on the map to drill down.")

# ── STICKY FILTER BAR ─────────────────────────────────────────────────────────
st.markdown('<div class="sticky-filter-wrap"><div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)

year_opts     = sorted(df['Year'].unique().tolist(), reverse=True)
region_opts   = sorted(df['Region'].unique().tolist())
category_opts = sorted(df['Category'].unique().tolist())
segment_opts  = sorted(df['Segment'].unique().tolist())

fc0, fc1, fc2, fc3 = st.columns(4)

with fc0:
    sel_year = st.multiselect("Year", year_opts, default=[v for v in st.session_state.sel_year if v in year_opts], placeholder="All Years")
with fc1:
    sel_region = st.multiselect("Region", region_opts, default=[v for v in st.session_state.sel_region if v in region_opts], placeholder="All Regions")
with fc2:
    sel_category = st.multiselect("Category", category_opts, default=[v for v in st.session_state.sel_category if v in category_opts], placeholder="All Categories")
with fc3:
    sel_segment = st.multiselect("Segment", segment_opts, default=[v for v in st.session_state.sel_segment if v in segment_opts], placeholder="All Segments")

# Sync session state immediately
st.session_state.sel_year     = list(sel_year)
st.session_state.sel_region   = list(sel_region)
st.session_state.sel_category = list(sel_category)
st.session_state.sel_segment  = list(sel_segment)

# Active filter pills
pills_html = '<div class="active-pills">'
cs = st.session_state.clicked_state
for v in sel_year:     pills_html += f'<div class="pill">📅 {v}</div>'
for v in sel_region:   pills_html += f'<div class="pill">🌎 {v}</div>'
for v in sel_category: pills_html += f'<div class="pill">📦 {v}</div>'
for v in sel_segment:  pills_html += f'<div class="pill">👥 {v}</div>'
if cs:                 pills_html += f'<div class="pill state">📍 {cs}</div>'
if not any([sel_year, sel_region, sel_category, sel_segment, cs]):
    pills_html += '<div class="pill" style="color:#4a7fa5;border-color:#2d4a6b;">Showing all data</div>'
pills_html += '</div></div></div>'
st.markdown(pills_html, unsafe_allow_html=True)

# ── MAP CLICK handler ─────────────────────────────────────────────────────────
if st.session_state.clicked_state:
    col_badge, col_clear = st.columns([5, 1])
    with col_badge:
        st.markdown(f'<div class="state-badge">📍 Map filter active — <strong>{st.session_state.clicked_state}</strong></div>', unsafe_allow_html=True)
    with col_clear:
        if st.button("✕ Clear state", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()

# ── BUILD filtered_df ─────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)
if sel_year:     mask &= df['Year'].isin(sel_year)
if sel_region:   mask &= df['Region'].isin(sel_region)
if sel_category: mask &= df['Category'].isin(sel_category)
if sel_segment:  mask &= df['Segment'].isin(sel_segment)
if st.session_state.clicked_state: mask &= df['State'] == st.session_state.clicked_state
if st.session_state.clicked_city:  mask &= df['City']  == st.session_state.clicked_city

filtered_df = df[mask]

if filtered_df.empty:
    st.warning("No data matches the current filter combination. Try adjusting your selections.")
    st.stop()

# ── METRICS ───────────────────────────────────────────────────────────────────
state_sales   = filtered_df.groupby(['State','State Code'])['Sales'].sum().reset_index()
cat_sales     = filtered_df.groupby('Category')['Sales'].sum().reset_index()
subcat_sales  = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()
region_sales  = filtered_df.groupby('Region')['Sales'].sum().reset_index()
segment_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
city_sales    = filtered_df.groupby('City')['Sales'].sum().reset_index()
monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index().sort_values('Month')
region_seg    = filtered_df.groupby(['Region','Segment'])['Sales'].sum().reset_index()

total_sales   = filtered_df['Sales'].sum()
total_orders  = filtered_df['Order ID'].nunique()
avg_order_val = total_sales / total_orders if total_orders else 0

top_state      = state_sales.sort_values('Sales', ascending=False).iloc[0] if not state_sales.empty else None
top_city_row   = city_sales.sort_values('Sales', ascending=False).iloc[0] if not city_sales.empty else None
top_cat_row    = cat_sales.sort_values('Sales', ascending=False).iloc[0] if not cat_sales.empty else None
top_subcat_row = subcat_sales.sort_values('Sales', ascending=False).iloc[0] if not subcat_sales.empty else None
top_region_row = region_sales.sort_values('Sales', ascending=False).iloc[0] if not region_sales.empty else None
top_seg_row    = segment_sales.sort_values('Sales', ascending=False).iloc[0] if not segment_sales.empty else None
state_share    = (top_state['Sales'] / total_sales * 100) if top_state is not None and total_sales else 0

# ── KPI ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Sales",     f"${total_sales:,.0f}")
k2.metric("📦 Total Orders",    f"{total_orders:,}")
k3.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")
if top_region_row is not None:
    k4.metric("🏆 #1 Region",       top_region_row['Region'])

st.markdown("---")

# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State  ·  Click a state to drill down")

all_state_sales = df.groupby(['State','State Code'])['Sales'].sum().reset_index()
fig_map = px.choropleth(
    all_state_sales, locations='State Code', locationmode="USA-states",
    color='Sales', scope="usa", hover_name='State',
    color_continuous_scale="Blues", labels={'Sales':'Total Sales ($)'},
    template="plotly_dark"
)
fig_map.update_traces(hovertemplate="<b>%{hovertext}</b><br>Total Sales: $%{z:,.0f}<extra></extra>")

if st.session_state.clicked_state:
    hl = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]
    if not hl.empty:
        fig_map.add_trace(go.Choropleth(
            locations=hl['State Code'], z=[1], locationmode="USA-states",
            colorscale=[[0,"rgba(233,69,96,0)"], [1,"rgba(233,69,96,0)"]],
            showscale=False, marker_line_color="#e94560",
            marker_line_width=3, hoverinfo='skip',
        ))

fig_map.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0}, geo_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
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
        elif new_state == st.session_state.clicked_state:
            st.session_state.clicked_state = None
        st.rerun()

if top_state is not None:
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">📌</div><div class="label">Map Insight</div>
      <div class="value">{top_state['State']} leads all states</div>
      <div class="detail">Generating <strong>${top_state['Sales']:,.0f}</strong> in sales —
      <strong>{state_share:.1f}%</strong> of total revenue in this selection.
      Focus distribution and logistics investments here for maximum impact.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── INSIGHT CARDS ─────────────────────────────────────────────────────────────
st.header("💡 Key Business Insights")
c1,c2,c3 = st.columns(3)
if top_state is not None and top_city_row is not None:
    with c1:
        st.markdown(f'<div class="insight-card good"><div class="icon">🏅</div><div class="label">Top State</div><div class="value">{top_state["State"]}</div><div class="detail">${top_state["Sales"]:,.0f} in sales ({state_share:.1f}% of total)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card"><div class="icon">🏙️</div><div class="label">Top City</div><div class="value">{top_city_row["City"]}</div><div class="detail">${top_city_row["Sales"]:,.0f} — highest city-level revenue driver</div></div>', unsafe_allow_html=True)
if top_cat_row is not None and top_subcat_row is not None:
    with c2:
        st.markdown(f'<div class="insight-card good"><div class="icon">📦</div><div class="label">Dominant Category</div><div class="value">{top_cat_row["Category"]}</div><div class="detail">${top_cat_row["Sales"]:,.0f} — prime candidate for increased marketing spend</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card"><div class="icon">🔖</div><div class="label">Top Sub-Category</div><div class="value">{top_subcat_row["Sub-Category"]}</div><div class="detail">${top_subcat_row["Sales"]:,.0f} — highest-earning product sub-group</div></div>', unsafe_allow_html=True)
if top_seg_row is not None and top_region_row is not None:
    with c3:
        st.markdown(f'<div class="insight-card good"><div class="icon">👥</div><div class="label">Leading Segment</div><div class="value">{top_seg_row["Segment"]}</div><div class="detail">${top_seg_row["Sales"]:,.0f} — your most valuable customer segment</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card"><div class="icon">🌎</div><div class="label">Top Region</div><div class="value">{top_region_row["Region"]}</div><div class="detail">${top_region_row["Sales"]:,.0f} — strongest regional market</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── PERFORMANCE BREAKDOWN ─────────────────────────────────────────────────────
st.header("📊 Performance Breakdown")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Sales")
    top_states_df = state_sales.sort_values('Sales', ascending=False).head(10)
    fig_bar = px.bar(
        top_states_df, x='Sales', y='State', orientation='h',
        color='Sales', color_continuous_scale='Blues', labels={'Sales':'Total Sales ($)'},
        text_auto=".2s", template="plotly_dark"
    )
    fig_bar.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>", textposition="outside")
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_states")

with col2:
    st.subheader("Category & Segment Mix")
    _sun_df = filtered_df.groupby(['Category','Segment'])['Sales'].sum().reset_index()
    _sun_cmap = {
        "Consumer": "#1a56a0", "Corporate": "#4299e1", "Home Office": "#90cdf4",
        "Furniture": "#1a365d", "Office Supplies": "#1e4a6e", "Technology": "#17364f", "(?)": "#0d1b2a",
    }
    fig_sun = px.sunburst(_sun_df, path=['Category','Segment'], values='Sales', color='Segment', color_discrete_map=_sun_cmap, template="plotly_dark")
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>",
        textfont=dict(size=11), insidetextorientation='radial',
        marker=dict(colors=[_sun_cmap.get(lbl, "#1e3a5f") for lbl in fig_sun.data[0].labels])
    )
    fig_sun.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)))
    st.plotly_chart(fig_sun, use_container_width=True, key="sunburst_cat")

st.markdown("---")

# ── TRENDS & CORRELATION ──────────────────────────────────────────────────────
st.header("📈 Sales Trends & Insights")
col3, col4 = st.columns([1.5, 1])

with col3:
    st.subheader("Monthly Revenue Growth")
    # Swapped to an area chart for a more modern "dashboard" look
    monthly_sales['label'] = monthly_sales['Sales'].apply(lambda v: f"${v/1000:.0f}K" if v >= 1000 else f"${v:.0f}")
    fig_line = px.area(
        monthly_sales, x='Month', y='Sales', markers=True,
        labels={'Sales':'Total Sales ($)','Month':''}, template="plotly_dark"
    )
    fig_line.update_traces(
        line_color='#4299e1', fillcolor='rgba(66, 153, 225, 0.2)',
        marker=dict(size=6, color='#90cdf4'),
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
    )
    fig_line.update_layout(
        xaxis_tickangle=-45, yaxis=dict(tickprefix="$", tickformat=",.0f"),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_line, use_container_width=True, key="line_trend")

with col4:
    st.subheader("Sub-Category Ranking")
    subcat_sorted = subcat_sales.sort_values('Sales', ascending=True).tail(8) # Show top 8 for clean UI
    fig_subcat = px.bar(
        subcat_sorted, x='Sales', y='Sub-Category', orientation='h',
        color='Sales', color_continuous_scale='Teal', labels={'Sales':'Total Sales ($)'},
        text_auto=".2s", template="plotly_dark"
    )
    fig_subcat.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>", textposition="outside")
    fig_subcat.update_layout(coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_subcat, use_container_width=True, key="bar_subcat")

st.markdown("---")

# ── CITIES TABLE ────────────────────────────────────────────────────────────
st.header("🏙️ Cities by Revenue")

# Using streamlit's native column config format keeps the underlying data numeric (enabling column sorting!)
city_table = filtered_df.groupby('City')['Sales'].sum().reset_index()
city_table = city_table.sort_values('Sales', ascending=False).reset_index(drop=True)
city_table.index += 1
city_table.insert(0, 'Rank', city_table.index)
city_table['Share %'] = (city_table['Sales'] / city_table['Sales'].sum() * 100).round(2)

st.dataframe(
    city_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank"),
        "City": st.column_config.TextColumn("City Name"),
        "Sales": st.column_config.NumberColumn("Total Sales", format="$%d"),
        "Share %": st.column_config.NumberColumn("Share %", format="%.1f%%")
    }
)
