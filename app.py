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
# We mark the filter with an id, walk the Streamlit DOM tree to its containing
# stVerticalBlock, set position:fixed + top:0, and insert an equal-height
# spacer so the content underneath doesn't jump.
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

    // Walk up the DOM to find the stVerticalBlock that wraps our filter widgets
    var block = sentinel;
    var found = false;
    for (var i = 0; i < 12; i++) {
      if (!block.parentElement) return;
      block = block.parentElement;
      if (block.getAttribute('data-testid') === 'stVerticalBlock') {
        // Make sure this block actually contains the filter-bar div
        if (block.querySelector('.filter-bar')) { found = true; break; }
      }
    }
    if (!found) return;

    // Prevent double-execution across re-renders
    if (block.getAttribute('data-filter-fixed') === '1') return;
    block.setAttribute('data-filter-fixed', '1');
    DONE = true;

    // Insert spacer before the block so content doesn't jump up
    var spacer = document.createElement('div');
    spacer.id = 'filter-spacer';
    block.parentNode.insertBefore(spacer, block);

    function applyFixed() {
      var h = block.scrollHeight;
      spacer.style.height = h + 'px';

      // Detect left offset from Streamlit's layout padding
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

  // Fire on load and on every Streamlit re-render (MutationObserver)
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

region_opts   = sorted(df['Region'].unique().tolist())
category_opts = sorted(df['Category'].unique().tolist())
segment_opts  = sorted(df['Segment'].unique().tolist())

fc1, fc2, fc3, fc4 = st.columns([1.2, 1.2, 1.2, 0.7])

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
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    if st.button("↺ Reset all", use_container_width=True):
        st.session_state.sel_region   = []
        st.session_state.sel_category = []
        st.session_state.sel_segment  = []
        st.session_state.clicked_state = None
        st.rerun()

# Sync session state immediately (no Apply needed)
st.session_state.sel_region   = list(sel_region)
st.session_state.sel_category = list(sel_category)
st.session_state.sel_segment  = list(sel_segment)

# Active filter pills
pills_html = '<div class="active-pills">'
cs = st.session_state.clicked_state
for v in sel_region:   pills_html += f'<div class="pill">🌎 {v}</div>'
for v in sel_category: pills_html += f'<div class="pill">📦 {v}</div>'
for v in sel_segment:  pills_html += f'<div class="pill">👥 {v}</div>'
if cs:                  pills_html += f'<div class="pill state">📍 {cs}</div>'
if not sel_region and not sel_category and not sel_segment and not cs:
    pills_html += '<div class="pill" style="color:#4a7fa5;border-color:#2d4a6b;">Showing all data</div>'
pills_html += '</div>'
st.markdown(pills_html, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)  # close filter-bar + sticky-filter-wrap

# ── MAP CLICK handler (state clear button appears below filter bar) ────────────
if st.session_state.clicked_state:
    col_badge, col_clear = st.columns([5, 1])
    with col_badge:
        st.markdown(f'<div class="state-badge">📍 Map filter active — <strong>{st.session_state.clicked_state}</strong></div>', unsafe_allow_html=True)
    with col_clear:
        if st.button("✕ Clear state", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()

# ── BUILD filtered_df ───────────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)
if sel_region:   mask &= df['Region'].isin(sel_region)
if sel_category: mask &= df['Category'].isin(sel_category)
if sel_segment:  mask &= df['Segment'].isin(sel_segment)
if st.session_state.clicked_state: mask &= df['State'] == st.session_state.clicked_state

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

# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State  ·  Click a state to drill down")

all_state_sales = df.groupby(['State','State Code'])['Sales'].sum().reset_index()
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

# ── CORRELATION ───────────────────────────────────────────────────────────────
st.header("🔗 Segment × Category Correlation")
st.caption("How strongly do spending patterns across segments track each other? A score near 1.0 means the two segments rise and fall together.")

corr_cols = st.columns([1.1, 1, 0.9])

with corr_cols[0]:
    monthly_seg_pivot = filtered_df.groupby(['Month','Segment'])['Sales'].sum().unstack(fill_value=0)
    corr_matrix = monthly_seg_pivot.corr()
    fig_heat = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0,"#0d1b2a"],[0.4,"#1e3a5f"],[0.7,"#2b6cb0"],[1,"#90cdf4"]],
        zmin=0, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
        texttemplate="%{text}", textfont=dict(size=14, color="white"),
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
        showscale=True, colorbar=dict(title="r", thickness=12, len=0.7)
    ))
    fig_heat.update_layout(
        title=dict(text="Monthly Sales Correlation by Segment", font=dict(size=13), x=0.5),
        margin=dict(l=10, r=10, t=40, b=10), height=280
    )
    st.plotly_chart(fig_heat, use_container_width=True, key="corr_heatmap")

with corr_cols[1]:
    seg_cat_df = filtered_df.groupby(['Segment','Category'])['Sales'].sum().reset_index()
    seg_cat_df['Share'] = seg_cat_df.groupby('Segment')['Sales'].transform(lambda x: x/x.sum()*100)
    fig_segcat = px.bar(
        seg_cat_df, x='Segment', y='Share', color='Category', barmode='stack',
        color_discrete_sequence=["#1a56a0","#4299e1","#90cdf4"],
        labels={'Share':'% of Segment Sales','Segment':''}
    )
    fig_segcat.update_traces(hovertemplate="<b>%{x}</b><br>Category: %{fullData.name}<br>Share: %{y:.1f}%<extra></extra>")
    fig_segcat.update_layout(
        title=dict(text="Category Mix per Segment (%)", font=dict(size=13), x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=-0.52, xanchor="center", x=0.5, font=dict(size=10)),
        xaxis=dict(title=None, tickfont=dict(size=11)),
        yaxis=dict(ticksuffix="%"),
        margin=dict(l=10, r=10, t=40, b=70), height=300
    )
    st.plotly_chart(fig_segcat, use_container_width=True, key="seg_cat_mix")

with corr_cols[2]:
    segs  = corr_matrix.columns.tolist()
    pairs = [(segs[i], segs[j], corr_matrix.iloc[i,j])
             for i in range(len(segs)) for j in range(i+1, len(segs))]
    pairs.sort(key=lambda x: x[2], reverse=True)
    strongest = pairs[0]
    weakest   = pairs[-1]
    st.markdown(f"""
    <div class="insight-card good" style="margin-top:8px;">
      <div class="icon">📈</div><div class="label">Strongest Correlation</div>
      <div class="value" style="font-size:1.1rem;">{strongest[0]} × {strongest[1]}</div>
      <div class="detail">r = <strong>{strongest[2]:.2f}</strong> — these segments move almost in lockstep. Campaigns that boost one will likely lift the other.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-card warn">
      <div class="icon">📉</div><div class="label">Weakest Correlation</div>
      <div class="value" style="font-size:1.1rem;">{weakest[0]} × {weakest[1]}</div>
      <div class="detail">r = <strong>{weakest[2]:.2f}</strong> — these segments behave more independently. Tailored strategies recommended.</div>
    </div>""", unsafe_allow_html=True)
    cat_pivot = filtered_df.groupby(['Segment','Category'])['Sales'].sum().unstack(fill_value=0)
    most_balanced = (cat_pivot.div(cat_pivot.sum(axis=1), axis=0).std(axis=1)).idxmin()
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">⚖️</div><div class="label">Most Balanced Buyer</div>
      <div class="value" style="font-size:1.1rem;">{most_balanced}</div>
      <div class="detail">Distributes spend most evenly across all three categories — lowest variance in category mix.</div>
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

# ── TOP 10 CITIES + RAW DATA ──────────────────────────────────────────────────
st.header("🏙️ Top 10 Cities by Revenue")
top_cities = city_sales.sort_values('Sales', ascending=False).head(10).reset_index(drop=True)
top_cities.index += 1
st.dataframe(
    top_cities.style.format({'Sales': '${:,.0f}'}),
    use_container_width=True
)
