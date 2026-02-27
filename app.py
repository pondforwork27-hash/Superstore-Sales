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

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Sticky filter wrapper ───────────────────────────────────────── */
.sticky-filter-wrap {
    position: sticky;
    top: 0;
    z-index: 999;
    /* pull it flush to the Streamlit page edges */
    margin-left:  -1rem;
    margin-right: -1rem;
    padding: 0 1rem;
    /* glass-like backdrop so charts don't bleed through */
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    background: rgba(10, 18, 30, 0.82);
    border-bottom: 1px solid rgba(66, 153, 225, 0.18);
    padding-bottom: 4px;
}
/* ── Filter card inside ─────────────────────────────────────────── */
.filter-bar {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 40%, #1e3a5f 100%);
    border: 1px solid #2d4a6b;
    border-radius: 0 0 12px 12px;
    padding: 14px 20px 12px 20px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
.filter-bar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 15% 60%, rgba(66,153,225,0.07) 0%, transparent 55%),
        radial-gradient(circle at 85% 20%, rgba(99,179,237,0.05) 0%, transparent 45%);
    pointer-events: none;
}
.filter-title {
    font-size: 0.68rem;
    font-weight: 700;
    color: #63b3ed;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    margin-bottom: 8px;
}
/* pending badge shown when filters differ from applied */
.pending-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(237,137,54,0.15);
    border: 1px solid #ed8936;
    border-radius: 16px;
    padding: 3px 10px;
    font-size: 0.74rem;
    color: #fbd38d;
    margin-left: 8px;
    vertical-align: middle;
}
/* active filter pills */
.active-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
    margin-bottom: 2px;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(30,58,95,0.9);
    border: 1px solid #2d5a8a;
    border-radius: 16px;
    padding: 3px 10px;
    font-size: 0.73rem;
    color: #90cdf4;
}
.pill.state { border-color: #e94560; color: #feb2b2; }
/* ── State click badge ──────────────────────────────────────────── */
.state-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(90deg,#1e3a5f,#2d5a8a);
    border: 1px solid #4299e1;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #90cdf4;
    margin-bottom: 10px;
}
.state-badge strong { color:#fff; }
/* ── Insight cards ─────────────────────────────────────────────── */
.insight-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a3b 100%);
    border-left: 4px solid #4299e1;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #f0f0f0;
}
.insight-card.warn  { border-left-color: #ed8936; }
.insight-card.good  { border-left-color: #48bb78; }
.insight-card.alert { border-left-color: #e94560; }
.insight-card .icon { font-size: 1.3rem; }
.insight-card .label {
    font-size: 0.7rem; color: #a0aec0;
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: 3px;
}
.insight-card .value { font-size: 1.35rem; font-weight: 700; color: #fff; }
.insight-card .detail { font-size: 0.82rem; color: #90cdf4; margin-top: 3px; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ── JS: make the sticky-filter-wrap actually sticky inside Streamlit ──────────
# Streamlit wraps everything in block containers; we hoist the filter section
# up to the app-level so `position:sticky; top:0` works correctly.
st.markdown("""
<script>
(function() {
  function stickyInit() {
    var wrap = document.querySelector('.sticky-filter-wrap');
    if (!wrap) return;
    // walk up until we find the stVerticalBlock direct child of the app view
    var el = wrap;
    for (var i = 0; i < 8; i++) {
      if (!el.parentElement) break;
      el = el.parentElement;
      if (el.classList.contains('stVerticalBlock')) {
        el.style.position = 'sticky';
        el.style.top      = '0';
        el.style.zIndex   = '999';
        break;
      }
    }
  }
  if (document.readyState === 'complete') { stickyInit(); }
  else { window.addEventListener('load', stickyInit); }
  // also fire on Streamlit re-renders
  var obs = new MutationObserver(stickyInit);
  obs.observe(document.body, { childList: true, subtree: false });
})();
</script>
""", unsafe_allow_html=True)

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
    'clicked_state':   None,
    # "staged" = what the widgets currently show
    'staged_region':   'All Regions',
    'staged_category': 'All Categories',
    'staged_segment':  'All Segments',
    # "applied" = what the charts actually use (only updated on Apply)
    'applied_region':   'All Regions',
    'applied_category': 'All Categories',
    'applied_segment':  'All Segments',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Set filters → click **Apply** to update all charts. Click a state on the map to drill down.")

# ── STICKY FILTER BAR ─────────────────────────────────────────────────────────
st.markdown('<div class="sticky-filter-wrap"><div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)

region_opts   = ["All Regions"]   + sorted(df['Region'].unique().tolist())
category_opts = ["All Categories"]+ sorted(df['Category'].unique().tolist())
segment_opts  = ["All Segments"]  + sorted(df['Segment'].unique().tolist())

fc1, fc2, fc3, fc4, fc5 = st.columns([1.1, 1.1, 1.1, 0.65, 0.65])

with fc1:
    staged_region = st.selectbox(
        "Region", region_opts,
        index=region_opts.index(st.session_state.staged_region),
        key='_w_region'
    )
with fc2:
    staged_category = st.selectbox(
        "Category", category_opts,
        index=category_opts.index(st.session_state.staged_category),
        key='_w_category'
    )
with fc3:
    staged_segment = st.selectbox(
        "Segment", segment_opts,
        index=segment_opts.index(st.session_state.staged_segment),
        key='_w_segment'
    )
with fc4:
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    apply_clicked = st.button("✅ Apply", use_container_width=True, type="primary")
with fc5:
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    reset_clicked = st.button("↺ Reset", use_container_width=True)

# ── Handle Apply / Reset ──────────────────────────────────────────────────────
if apply_clicked:
    st.session_state.staged_region   = staged_region
    st.session_state.staged_category = staged_category
    st.session_state.staged_segment  = staged_segment
    st.session_state.applied_region   = staged_region
    st.session_state.applied_category = staged_category
    st.session_state.applied_segment  = staged_segment
    st.rerun()

if reset_clicked:
    st.session_state.staged_region   = 'All Regions'
    st.session_state.staged_category = 'All Categories'
    st.session_state.staged_segment  = 'All Segments'
    st.session_state.applied_region   = 'All Regions'
    st.session_state.applied_category = 'All Categories'
    st.session_state.applied_segment  = 'All Segments'
    st.session_state.clicked_state    = None
    st.rerun()

# Detect if staged differs from applied (pending changes)
pending = (
    staged_region   != st.session_state.applied_region or
    staged_category != st.session_state.applied_category or
    staged_segment  != st.session_state.applied_segment
)
if pending:
    st.markdown('<div style="margin-top:4px;"><span class="pending-badge">⚠️ Unapplied changes — click Apply</span></div>', unsafe_allow_html=True)

# Active filter pills
pills_html = '<div class="active-pills">'
r = st.session_state.applied_region
c = st.session_state.applied_category
s = st.session_state.applied_segment
cs = st.session_state.clicked_state
if r != 'All Regions':   pills_html += f'<div class="pill">🌎 {r}</div>'
if c != 'All Categories':pills_html += f'<div class="pill">📦 {c}</div>'
if s != 'All Segments':  pills_html += f'<div class="pill">👥 {s}</div>'
if cs:                    pills_html += f'<div class="pill state">📍 {cs}</div>'
if r == 'All Regions' and c == 'All Categories' and s == 'All Segments' and not cs:
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

# ── BUILD filtered_df from APPLIED values ────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)
ar = st.session_state.applied_region
ac = st.session_state.applied_category
as_ = st.session_state.applied_segment
if ar  != 'All Regions':    mask &= df['Region']   == ar
if ac  != 'All Categories': mask &= df['Category'] == ac
if as_ != 'All Segments':   mask &= df['Segment']  == as_
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
    fig_sun = px.sunburst(
        filtered_df.groupby(['Category','Segment'])['Sales'].sum().reset_index(),
        path=['Category','Segment'], values='Sales', color='Segment',
        color_discrete_map={"Consumer":"#1a56a0","Corporate":"#4299e1","Home Office":"#90cdf4"}
    )
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>",
        textfont=dict(size=11)
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
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10)),
        yaxis=dict(ticksuffix="%"),
        margin=dict(l=10, r=10, t=40, b=10), height=280
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

# ── TOP CITIES ────────────────────────────────────────────────────────────────
st.header("🏙️ Top 10 Cities by Revenue")
top_cities = city_sales.sort_values('Sales', ascending=False).head(10).reset_index(drop=True)
top_cities.index += 1
top_cities['Sales'] = top_cities['Sales'].map('${:,.0f}'.format)
st.dataframe(top_cities, use_container_width=True)
