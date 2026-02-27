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
    background: linear-gradient(135deg, #3a6f8f 0%, #4a85a8 50%, #5a9abf 100%);
    border: 1px solid #7ab3d0;
    border-bottom: 1px solid rgba(180,220,255,0.3);
    border-radius: 0 0 14px 14px;
    padding: 12px 20px 10px 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    position: relative; overflow: hidden;
}
/* ── Filter label and input text colors ── */
.filter-bar label { color: #ffffff !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.filter-bar [data-baseweb="select"] input { color: #ffffff !important; }
.filter-bar [data-baseweb="select"] input::placeholder { color: #ffffff !important; opacity: 1 !important; }
.filter-bar [data-baseweb="select"] [class$="placeholder"],
.filter-bar [data-baseweb="select"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
[data-testid="stMultiSelect"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
/* ── Multiselect selected tags ── */
span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #2d6080, #3a7a9e) !important;
    border: 1px solid #a8d4f0 !important;
    border-radius: 20px !important;
    color: #ffffff !important;
}
span[data-baseweb="tag"] span { color: #ffffff !important; }
span[data-baseweb="tag"] [role="presentation"] svg { fill: #d0eeff !important; }
/* multiselect container — match filter bar tone */
[data-baseweb="select"] > div {
    background: rgba(58,111,143,0.75) !important;
    border: 1px solid #7ab3d0 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #d0eeff !important;
    box-shadow: 0 0 0 2px rgba(200,230,255,0.3) !important;
}
/* dropdown menu */
[data-baseweb="popover"] ul { background: #3a6f8f !important; border: 1px solid #7ab3d0 !important; }
[data-baseweb="popover"] li { color: #e8f4ff !important; }
[data-baseweb="popover"] li:hover { background: #2d6080 !important; color: #fff !important; }
[data-baseweb="popover"] li[aria-selected="true"] {
    background: #245070 !important;
    color: #d0eeff !important;
}
.filter-bar::before {
    content: '';
    position: absolute; top:0; left:0; right:0; bottom:0;
    background:
        radial-gradient(circle at 15% 60%, rgba(66,153,225,0.07) 0%, transparent 55%),
        radial-gradient(circle at 85% 20%, rgba(99,179,237,0.05) 0%, transparent 45%);
    pointer-events: none;
}
.filter-title {
    font-size: 0.68rem; font-weight: 700; color: #63b3ed;
    text-transform: uppercase; letter-spacing: 0.13em; margin-bottom: 8px;
}
.pending-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(237,137,54,0.15); border: 1px solid #ed8936;
    border-radius: 16px; padding: 3px 10px;
    font-size: 0.74rem; color: #fbd38d; margin-left: 8px; vertical-align: middle;
}
.active-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; margin-bottom:2px; }
.pill {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(30,58,95,0.9); border:1px solid #2d5a8a;
    border-radius:16px; padding:3px 10px; font-size:0.73rem; color:#90cdf4;
}
.pill.state { border-color:#e94560; color:#feb2b2; }
.state-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:linear-gradient(90deg,#1e3a5f,#2d5a8a);
    border:1px solid #4299e1; border-radius:20px;
    padding:5px 14px; font-size:0.8rem; color:#90cdf4; margin-bottom:10px;
}
.state-badge strong { color:#fff; }
.insight-card {
    background:linear-gradient(135deg,#0d1b2a 0%,#1b2a3b 100%);
    border-left:4px solid #4299e1; border-radius:8px;
    padding:14px 18px; margin-bottom:10px; color:#f0f0f0;
}
.insight-card.warn  { border-left-color:#ed8936; }
.insight-card.good  { border-left-color:#48bb78; }
.insight-card.alert { border-left-color:#e94560; }
.insight-card .icon { font-size:1.3rem; }
.insight-card .label {
    font-size:0.7rem; color:#a0aec0;
    text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px;
}
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
      if (block.getAttribute('data-testid') === 'stVerticalBlock') {
        if (block.querySelector('.filter-bar')) { found = true; break; }
      }
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
        'position:fixed',
        'top:0',
        'left:' + parentRect.left + 'px',
        'width:' + parentRect.width + 'px',
        'z-index:9999',
        'background:rgba(8,15,26,0.96)',
        'backdrop-filter:blur(8px)',
        '-webkit-backdrop-filter:blur(8px)',
      ].join(';');
    }

    applyFixed();
    window.addEventListener('resize', applyFixed);
  }

  fixFilter();
  new MutationObserver(function(muts) {
    muts.forEach(function(m) { if (m.addedNodes.length) fixFilter(); });
  }).observe(document.body, { childList: true, subtree: true });
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
    'sel_region':    [],
    'sel_category':  [],
    'sel_segment':   [],
    'sel_year':      [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Select filters to update all charts instantly. Click a state on the map or use the search box to drill down.")

# ── STICKY FILTER BAR ─────────────────────────────────────────────────────────
st.markdown('<div class="sticky-filter-wrap"><div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)

region_opts   = sorted(df['Region'].unique().tolist())
category_opts = sorted(df['Category'].unique().tolist())
segment_opts  = sorted(df['Segment'].unique().tolist())
year_opts     = sorted(df['Year'].unique().tolist())

fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    sel_region = st.multiselect(
        "Region", region_opts,
        default=[v for v in st.session_state.sel_region if v in region_opts],
        placeholder="All regions", key='_w_region'
    )
with fc2:
    sel_category = st.multiselect(
        "Category", category_opts,
        default=[v for v in st.session_state.sel_category if v in category_opts],
        placeholder="All categories", key='_w_category'
    )
with fc3:
    sel_segment = st.multiselect(
        "Segment", segment_opts,
        default=[v for v in st.session_state.sel_segment if v in segment_opts],
        placeholder="All segments", key='_w_segment'
    )
with fc4:
    sel_year = st.multiselect(
        "Year", year_opts,
        default=[v for v in st.session_state.sel_year if v in year_opts],
        placeholder="All years", key='_w_year'
    )

# Sync session state immediately
st.session_state.sel_region   = list(sel_region)
st.session_state.sel_category = list(sel_category)
st.session_state.sel_segment  = list(sel_segment)
st.session_state.sel_year     = list(sel_year)

# Active filter pills
pills_html = '<div class="active-pills">'
cs = st.session_state.clicked_state
for v in sel_region:   pills_html += f'<div class="pill">🌎 {v}</div>'
for v in sel_category: pills_html += f'<div class="pill">📦 {v}</div>'
for v in sel_segment:  pills_html += f'<div class="pill">👥 {v}</div>'
for v in sel_year:     pills_html += f'<div class="pill">📅 {v}</div>'
if cs:                  pills_html += f'<div class="pill state">📍 {cs}</div>'
if not sel_region and not sel_category and not sel_segment and not sel_year and not cs:
    pills_html += '<div class="pill" style="color:#4a7fa5;border-color:#2d4a6b;">Showing all data</div>'
pills_html += '</div>'
st.markdown(pills_html, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ── MAP CLICK handler ────────────────────────────────────────────────────────
if st.session_state.clicked_state:
    col_badge, col_clear = st.columns([5, 1])
    with col_badge:
        st.markdown(f'<div class="state-badge">📍 Map filter active — <strong>{st.session_state.clicked_state}</strong></div>', unsafe_allow_html=True)
    with col_clear:
        if st.button("✕ Clear state", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()

# ── BUILD filtered_df ───────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)
if sel_region:   mask &= df['Region'].isin(sel_region)
if sel_category: mask &= df['Category'].isin(sel_category)
if sel_segment:  mask &= df['Segment'].isin(sel_segment)
if sel_year:     mask &= df['Year'].isin(sel_year)
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
top_state     = state_sales.sort_values('Sales', ascending=False).iloc[0]
top_city_row  = city_sales.sort_values('Sales', ascending=False).iloc[0]
top_cat_row   = cat_sales.sort_values('Sales', ascending=False).iloc[0]
top_subcat_row= subcat_sales.sort_values('Sales', ascending=False).iloc[0]
top_region_row= region_sales.sort_values('Sales', ascending=False).iloc[0]
top_seg_row   = segment_sales.sort_values('Sales', ascending=False).iloc[0]
state_share   = (top_state['Sales'] / total_sales * 100) if total_sales else 0

# ── KPI ───────────────────────────────────────────────────────────────────────
k1,k2,k3,k4 = st.columns(4)
k1.metric("💰 Total Sales",     f"${total_sales:,.0f}")
k2.metric("📦 Total Orders",    f"{total_orders:,}")
k3.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")
k4.metric("🏆 #1 Region",       top_region_row['Region'])

st.markdown("---")

# ── MAP without Search Box ───────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State  ·  Click a state to drill down")

# Calculate all state sales first
all_state_sales = df.groupby(['State','State Code'])['Sales'].sum().reset_index()

# Quick state filters as pills
if not st.session_state.clicked_state:
    st.markdown("""
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px; align-items:center;">
        <span style="color:#90cdf4; font-size:0.8rem;">⚡ Quick select:</span>
    """, unsafe_allow_html=True)
    
    # Show top 5 states as quick filters
    top_states_quick = all_state_sales.nlargest(5, 'Sales')['State'].tolist()
    quick_cols = st.columns(len(top_states_quick))
    for i, state in enumerate(top_states_quick):
        with quick_cols[i]:
            if st.button(f"🏆 {state}", key=f"quick_{state}", use_container_width=True):
                st.session_state.clicked_state = state
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Show selected state info if any
if st.session_state.clicked_state:
    col_info, col_clear_map = st.columns([5, 1])
    with col_info:
        # Get sales for selected state
        state_sales_val = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]['Sales'].values
        sales_text = f"${state_sales_val[0]:,.0f}" if len(state_sales_val) > 0 else "N/A"
        
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e3a5f,#2d5a8a); border:1px solid #4299e1; border-radius:10px; padding:8px 15px; margin-bottom:15px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#90cdf4; font-size:0.8rem;">📍 SELECTED:</span>
                <span style="color:white; font-weight:700; font-size:1rem;">{st.session_state.clicked_state}</span>
                <span style="color:#48bb78; font-size:0.9rem; margin-left:auto;">{sales_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_clear_map:
        st.markdown("<div style='margin-top:0;'>", unsafe_allow_html=True)
        if st.button("✕ Clear", key="clear_state_btn", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Create the map
fig_map = px.choropleth(
    all_state_sales, locations='State Code', locationmode="USA-states",
    color='Sales', scope="usa", hover_name='State',
    color_continuous_scale="Blues", labels={'Sales':'Total Sales ($)'}
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
    margin={"r":0,"t":0,"l":0,"b":0}, geo_bgcolor='rgba(0,0,0,0)',
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
c1,c2,c3 = st.columns(3)
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

# ── PERFORMANCE BREAKDOWN ─────────────────────────────────────────────────────
st.header("📊 Performance Breakdown")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Sales")
    top_states_df = state_sales.sort_values('Sales', ascending=False).head(10)
    fig_bar = px.bar(top_states_df, x='Sales', y='State', orientation='h',
                     color='Sales', color_continuous_scale='Blues', labels={'Sales':'Total Sales ($)'})
    fig_bar.update_traces(hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>")
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_states")

with col2:
    st.subheader("Category & Segment Mix")
    _sun_df = filtered_df.groupby(['Category','Segment'])['Sales'].sum().reset_index()
    # Assign explicit colors: segments get blues, parent category ring gets steel tones
    _sun_cmap = {
        # outer ring — segments (consistent across all charts)
        "Consumer":        "#1a56a0",
        "Corporate":       "#4299e1",
        "Home Office":     "#90cdf4",
        # inner ring — categories (darker steel so inner ring reads as structure)
        "Furniture":       "#1a365d",
        "Office Supplies": "#1e4a6e",
        "Technology":      "#17364f",
        # root node (center)
        "(?)":             "#0d1b2a",
    }
    fig_sun = px.sunburst(
        _sun_df, path=['Category','Segment'], values='Sales',
        color='Segment',
        color_discrete_map=_sun_cmap
    )
    # Override the inner category ring colours via marker patches
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>",
        textfont=dict(size=11),
        insidetextorientation='radial',
        # Darken parent (category) sectors manually
        marker=dict(
            colors=[
                _sun_cmap.get(lbl, "#1e3a5f")
                for lbl in fig_sun.data[0].labels
            ]
        )
    )
    fig_sun.update_layout(showlegend=True, legend=dict(
        orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
        font=dict(size=11), title=dict(text="Segment  ", font=dict(size=11))
    ))
    st.plotly_chart(fig_sun, use_container_width=True, key="sunburst_cat")
    st.markdown('''
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:-8px;margin-bottom:4px;">
      <div style="display:flex;align-items:center;gap:6px;background:#0d1b2a;border:1px solid #2d4a6b;border-radius:20px;padding:4px 12px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#1a56a0;"></div>
        <span style="font-size:0.78rem;color:#e2e8f0;font-weight:600;">Consumer</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;background:#0d1b2a;border:1px solid #2d4a6b;border-radius:20px;padding:4px 12px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#4299e1;"></div>
        <span style="font-size:0.78rem;color:#e2e8f0;font-weight:600;">Corporate</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;background:#0d1b2a;border:1px solid #2d4a6b;border-radius:20px;padding:4px 12px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#90cdf4;"></div>
        <span style="font-size:0.78rem;color:#e2e8f0;font-weight:600;">Home Office</span>
      </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("---")

# ── A/B TEST ──────────────────────────────────────────────────────────────────
st.header("🧪 A/B Segment Comparison")
st.caption("Pick two groups across any dimension — compare their sales, order volume, and avg order value side by side.")

ab_c1, ab_c2 = st.columns(2)

_ab_dims = {
    "Region":       "Region",
    "Category":     "Category",
    "Sub-Category": "Sub-Category",
    "Segment":      "Segment",
    "Ship Mode":    "Ship Mode",
    "State":        "State",
}

with ab_c1:
    st.markdown("#### 🔵 Group A")
    dim_a  = st.selectbox("Dimension", list(_ab_dims.keys()), key="ab_dim_a")
    opts_a = sorted(filtered_df[_ab_dims[dim_a]].unique().tolist())
    val_a  = st.selectbox("Value", opts_a, key="ab_val_a")

with ab_c2:
    st.markdown("#### 🔴 Group B")
    dim_b  = st.selectbox("Dimension", list(_ab_dims.keys()), key="ab_dim_b", index=list(_ab_dims.keys()).index("Segment") if "Segment" in _ab_dims else 0)
    opts_b = sorted(filtered_df[_ab_dims[dim_b]].unique().tolist())
    val_b  = st.selectbox("Value", opts_b, key="ab_val_b", index=min(1, len(opts_b)-1))

# Slice the two groups
grp_a = filtered_df[filtered_df[_ab_dims[dim_a]] == val_a]
grp_b = filtered_df[filtered_df[_ab_dims[dim_b]] == val_b]

def _ab_stats(grp):
    total   = grp["Sales"].sum()
    orders  = grp["Order ID"].nunique()
    avg_ord = total / orders if orders else 0
    top_cat = grp.groupby("Category")["Sales"].sum().idxmax() if not grp.empty else "—"
    top_sub = grp.groupby("Sub-Category")["Sales"].sum().idxmax() if not grp.empty else "—"
    top_st  = grp.groupby("State")["Sales"].sum().idxmax() if not grp.empty else "—"
    return dict(total=total, orders=orders, avg_ord=avg_ord,
                top_cat=top_cat, top_sub=top_sub, top_st=top_st)

sa, sb = _ab_stats(grp_a), _ab_stats(grp_b)

# ── KPI comparison row ────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)

def _delta(a, b):
    if b == 0: return 0
    return (a - b) / b * 100

for col, label, ka, kb in [
    (k1, "💰 Total Sales",      sa["total"],   sb["total"]),
    (k2, "📦 Total Orders",     sa["orders"],  sb["orders"]),
    (k3, "🧾 Avg Order Value",  sa["avg_ord"], sb["avg_ord"]),
]:
    with col:
        d = _delta(ka, kb)
        arrow = "▲" if d > 0 else "▼"
        color = "#48bb78" if d > 0 else "#e94560"
        fa = f"${ka:,.0f}" if label != "📦 Total Orders" else f"{int(ka):,}"
        fb = f"${kb:,.0f}" if label != "📦 Total Orders" else f"{int(kb):,}"
        st.markdown(f"""
        <div class="insight-card" style="text-align:center;padding:12px 8px;">
          <div class="label">{label}</div>
          <div style="display:flex;justify-content:center;gap:20px;margin-top:8px;">
            <div>
              <div style="font-size:0.7rem;color:#90cdf4;margin-bottom:2px;">🔵 {val_a}</div>
              <div style="font-size:1.2rem;font-weight:700;color:#fff;">{fa}</div>
            </div>
            <div style="display:flex;align-items:center;">
              <div style="font-size:1rem;color:{color};font-weight:700;">{arrow} {abs(d):.1f}%</div>
            </div>
            <div>
              <div style="font-size:0.7rem;color:#e94560;margin-bottom:2px;">🔴 {val_b}</div>
              <div style="font-size:1.2rem;font-weight:700;color:#fff;">{fb}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Monthly trend overlay ─────────────────────────────────────────────────────
ma = grp_a.groupby("Month")["Sales"].sum().reset_index().sort_values("Month")
mb = grp_b.groupby("Month")["Sales"].sum().reset_index().sort_values("Month")

fig_ab = go.Figure()
fig_ab.add_trace(go.Scatter(
    x=ma["Month"], y=ma["Sales"], name=f"🔵 {val_a}",
    line=dict(color="#4299e1", width=2.5), mode="lines+markers",
    hovertemplate=f"<b>{val_a}</b><br>%{{x}}<br>Sales: $%{{y:,.0f}}<extra></extra>"
))
fig_ab.add_trace(go.Scatter(
    x=mb["Month"], y=mb["Sales"], name=f"🔴 {val_b}",
    line=dict(color="#e94560", width=2.5), mode="lines+markers",
    hovertemplate=f"<b>{val_b}</b><br>%{{x}}<br>Sales: $%{{y:,.0f}}<extra></extra>"
))
fig_ab.update_layout(
    title=dict(text="Monthly Sales — A vs B", font=dict(size=13), x=0.5),
    xaxis_tickangle=-45,
    yaxis=dict(tickprefix="$", tickformat=",.0f"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10), height=320
)
st.plotly_chart(fig_ab, use_container_width=True, key="ab_trend")

# ── Category breakdown side by side (FIXED HOVER) ──────────────────────────
# Calculate both sales and order counts for each category
ab_cat_a_sales = grp_a.groupby("Category")["Sales"].sum().reset_index().assign(Group=val_a)
ab_cat_b_sales = grp_b.groupby("Category")["Sales"].sum().reset_index().assign(Group=val_b)

# Add order count data
ab_cat_a_orders = grp_a.groupby("Category")["Order ID"].nunique().reset_index().rename(columns={"Order ID": "Order Count"})
ab_cat_b_orders = grp_b.groupby("Category")["Order ID"].nunique().reset_index().rename(columns={"Order ID": "Order Count"})

# Merge sales and order data
ab_cat_a = ab_cat_a_sales.merge(ab_cat_a_orders, on="Category", how="left")
ab_cat_b = ab_cat_b_sales.merge(ab_cat_b_orders, on="Category", how="left")

# Fill any missing order counts with 0
ab_cat_a["Order Count"] = ab_cat_a["Order Count"].fillna(0).astype(int)
ab_cat_b["Order Count"] = ab_cat_b["Order Count"].fillna(0).astype(int)

# Combine for plotting
ab_cat = pd.concat([ab_cat_a, ab_cat_b])

# Create lookup dictionaries for hover data
cat_a_sales_dict = ab_cat_a.set_index('Category')['Sales'].to_dict()
cat_a_orders_dict = ab_cat_a.set_index('Category')['Order Count'].to_dict()
cat_b_sales_dict = ab_cat_b.set_index('Category')['Sales'].to_dict()
cat_b_orders_dict = ab_cat_b.set_index('Category')['Order Count'].to_dict()

fig_cat_ab = px.bar(
    ab_cat, 
    x="Category", 
    y="Sales", 
    color="Group", 
    barmode="group",
    color_discrete_map={val_a: "#4299e1", val_b: "#e94560"},
    labels={"Sales": "Total Sales ($)", "Group": ""},
)

# Fix hover template for Group A bars
fig_cat_ab.update_traces(
    hovertemplate="<b>%{x}</b><br>" +
                  f"<span style='color:#4299e1'>🔵 {val_a}</span><br>" +
                  "Sales: $%{y:,.0f}<br>" +
                  "Orders: %{customdata[0]:,.0f}<br>" +
                  "<extra></extra>",
    customdata=ab_cat_a[['Order Count']].values,
    selector={"name": val_a}
)

# Fix hover template for Group B bars
fig_cat_ab.update_traces(
    hovertemplate="<b>%{x}</b><br>" +
                  f"<span style='color:#e94560'>🔴 {val_b}</span><br>" +
                  "Sales: $%{y:,.0f}<br>" +
                  "Orders: %{customdata[0]:,.0f}<br>" +
                  "<extra></extra>",
    customdata=ab_cat_b[['Order Count']].values,
    selector={"name": val_b}
)

fig_cat_ab.update_layout(
    title=dict(text="Category Breakdown — A vs B", font=dict(size=13), x=0.5),
    legend=dict(
        orientation="h", 
        yanchor="bottom", 
        y=-0.25, 
        xanchor="center", 
        x=0.5,
    ),
    plot_bgcolor="rgba(0,0,0,0)", 
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        tickprefix="$", 
        tickformat=",.0f",
        gridcolor='rgba(128,128,128,0.2)'
    ),
    # HIDE THE X-AXIS CATEGORY LABELS
    xaxis=dict(
        showticklabels=False,    # Hide tick labels
        showgrid=False,          # Hide grid lines
        zeroline=False,          # Hide zero line
        showline=False,          # Hide axis line
        title=""                 # Remove title
    ),
    margin=dict(l=10, r=10, t=40, b=30), 
    height=350,
    hovermode="x",  # Changed from 'x unified' to 'x' for better individual bar hovering
    hoverlabel=dict(
        bgcolor="#1e3a5f",
        font_size=12,
        font_color="white",
        bordercolor="#4299e1"
    )
)

st.plotly_chart(fig_cat_ab, use_container_width=True, key="ab_cat")

# Add custom category labels below the chart
categories = sorted(filtered_df['Category'].unique())
category_icons = {
    'Furniture': '📦',
    'Office Supplies': '📎',
    'Technology': '💻'
}

labels_html = '<div style="display:flex; justify-content:space-around; margin-top:-15px; margin-bottom:10px; padding:0 20px;">'
for cat in categories:
    icon = category_icons.get(cat, '📊')
    labels_html += f'''
    <div style="text-align:center; background:#0d1b2a; padding:5px 15px; border-radius:20px; border:1px solid #2d4a6b;">
        <span style="color:#90cdf4; font-size:0.85rem;">{icon} {cat}</span>
    </div>
    '''
labels_html += '</div>'

st.markdown(labels_html, unsafe_allow_html=True)
# Add custom category labels below the chart
st.markdown(f"""
<div style="display:flex; justify-content:space-around; margin-top:-15px; margin-bottom:10px; padding:0 20px;">
    <div style="text-align:center; background:#0d1b2a; padding:5px 15px; border-radius:20px; border:1px solid #2d4a6b;">
        <span style="color:#90cdf4; font-size:0.85rem;">📦 Furniture</span>
    </div>
    <div style="text-align:center; background:#0d1b2a; padding:5px 15px; border-radius:20px; border:1px solid #2d4a6b;">
        <span style="color:#90cdf4; font-size:0.85rem;">📎 Office Supplies</span>
    </div>
    <div style="text-align:center; background:#0d1b2a; padding:5px 15px; border-radius:20px; border:1px solid #2d4a6b;">
        <span style="color:#90cdf4; font-size:0.85rem;">💻 Technology</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Insight summary ───────────────────────────────────────────────────────────
winner     = val_a if sa["total"] > sb["total"] else val_b
winner_tot = max(sa["total"], sb["total"])
loser_tot  = min(sa["total"], sb["total"])
gap_pct    = abs(_delta(sa["total"], sb["total"]))

st.markdown(f"""
<div class="insight-card good">
  <div class="icon">🏆</div>
  <div class="label">A/B Winner — Total Sales</div>
  <div class="value">{winner}</div>
  <div class="detail">
    <strong>{winner}</strong> outperforms by <strong>{gap_pct:.1f}%</strong>
    (${winner_tot:,.0f} vs ${loser_tot:,.0f}).
    Top category: <strong>{sa["top_cat"] if winner == val_a else sb["top_cat"]}</strong> ·
    Top sub-category: <strong>{sa["top_sub"] if winner == val_a else sb["top_sub"]}</strong> ·
    Strongest state: <strong>{sa["top_st"] if winner == val_a else sb["top_st"]}</strong>.
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── TRENDS ────────────────────────────────────────────────────────────────────
st.header("📈 Sales Trends & Sub-Category Deep Dive")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Monthly Sales Trend")
    monthly_sales['label'] = monthly_sales['Sales'].apply(
        lambda v: f"${v/1000:.0f}K" if v >= 1000 else f"${v:.0f}"
    )
    fig_line = px.line(monthly_sales, x='Month', y='Sales', markers=True,
                       text='label', labels={'Sales':'Total Sales ($)','Month':''})
    fig_line.update_traces(
        line_color='#4299e1', line_width=2.5,
        marker=dict(size=7, color='#4299e1'),
        textposition='top center', textfont=dict(size=10, color='#90cdf4'),
        hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>"
    )
    fig_line.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(tickprefix="$", tickformat=",.0f"),
        yaxis_range=[0, monthly_sales['Sales'].max() * 1.18]
    )
    st.plotly_chart(fig_line, use_container_width=True, key="line_trend")

    if len(monthly_sales) >= 2:
        pct_chg = ((monthly_sales.iloc[-1]['Sales'] - monthly_sales.iloc[0]['Sales'])
                   / monthly_sales.iloc[0]['Sales'] * 100)
        card_cls   = "good" if pct_chg > 0 else "alert"
        trend_word = "grown" if pct_chg > 0 else "declined"
        advice     = "Momentum is positive — consider scaling inventory." if pct_chg > 0 else "Investigate demand drivers and revisit pricing strategy."
        st.markdown(f'<div class="insight-card {card_cls}"><div class="icon">📈</div><div class="label">Trend Insight</div><div class="value">{abs(pct_chg):.1f}% {"▲" if pct_chg > 0 else "▼"} over period</div><div class="detail">Sales have <strong>{trend_word} {abs(pct_chg):.1f}%</strong> from first to last month. {advice}</div></div>', unsafe_allow_html=True)

with col4:
    st.subheader("Sub-Category Sales Ranking")
    subcat_sorted = subcat_sales.sort_values('Sales', ascending=False)
    fig_subcat = px.bar(subcat_sorted, x='Sub-Category', y='Sales',
                        color='Sales', color_continuous_scale='Teal', labels={'Sales':'Total Sales ($)'})
    fig_subcat.update_traces(hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>")
    fig_subcat.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig_subcat, use_container_width=True, key="bar_subcat")

    bottom_subcat = subcat_sorted.iloc[-1]
    st.markdown(f'<div class="insight-card warn"><div class="icon">⚠️</div><div class="label">Underperformer Alert</div><div class="value">{bottom_subcat["Sub-Category"]}</div><div class="detail">Only <strong>${bottom_subcat["Sales"]:,.0f}</strong> in sales — lowest sub-category. Review pricing, promotion, and placement or consider deprioritizing stock.</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── REGION × SEGMENT ──────────────────────────────────────────────────────────
st.header("🌎 Region vs. Segment Matrix")
fig_grouped = px.bar(region_seg, x='Region', y='Sales', color='Segment',
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={'Sales':'Total Sales ($)'})
fig_grouped.update_traces(hovertemplate="<b>%{x}</b><br>Segment: %{fullData.name}<br>Sales: $%{y:,.0f}<extra></extra>")
st.plotly_chart(fig_grouped, use_container_width=True, key="grouped_region_seg")

best_rs  = region_seg.sort_values('Sales', ascending=False).iloc[0]
worst_rs = region_seg.sort_values('Sales').iloc[0]
st.markdown(f'<div class="insight-card good"><div class="icon">🎯</div><div class="label">Strategic Insight</div><div class="value">Best combo: {best_rs["Region"]} × {best_rs["Segment"]}</div><div class="detail"><strong>{best_rs["Segment"]}</strong> in <strong>{best_rs["Region"]}</strong> delivers the highest sales at <strong>${best_rs["Sales"]:,.0f}</strong>. Lowest performer: <strong>{worst_rs["Segment"]}</strong> in <strong>{worst_rs["Region"]}</strong> (${worst_rs["Sales"]:,.0f}) — a clear opportunity for targeted growth campaigns.</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── CITIES TABLE with STATE column ────────────────────────────────────────────
st.header("🏙️ Top Cities by Sales")

_city_mask = pd.Series([True] * len(df), index=df.index)
if sel_region:   _city_mask &= df['Region'].isin(sel_region)
if sel_category: _city_mask &= df['Category'].isin(sel_category)
if sel_segment:  _city_mask &= df['Segment'].isin(sel_segment)
if st.session_state.clicked_state: _city_mask &= df['State'] == st.session_state.clicked_state
_city_base = df[_city_mask]

# Updated aggregation to include State
_agg = _city_base.groupby(['City', 'State']).agg(
    **{
        'Total Sales': ('Sales',       'sum'),
        'Orders':      ('Order ID',    'nunique'),
        'Customers':   ('Customer ID', 'nunique'),
    }
).reset_index()
_agg['Avg Order'] = _agg['Total Sales'] / _agg['Orders']
_agg = _agg.sort_values('Total Sales', ascending=False).reset_index(drop=True)
_agg.index += 1

# Reorder columns to show State after City
_agg = _agg[['City', 'State', 'Total Sales', 'Orders', 'Customers', 'Avg Order']]

st.dataframe(
    _agg.style.format({
        'Total Sales': '${:,.2f}',
        'Avg Order':   '${:,.2f}',
        'Orders':      '{:,}',
        'Customers':   '{:,}',
    }),
    use_container_width=True,
    height=420,
)


