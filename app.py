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
.filter-bar label { color: #ffffff !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.filter-bar [data-baseweb="select"] input { color: #ffffff !important; }
.filter-bar [data-baseweb="select"] input::placeholder { color: #ffffff !important; opacity: 1 !important; }
.filter-bar [data-baseweb="select"] [class$="placeholder"],
.filter-bar [data-baseweb="select"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
[data-testid="stMultiSelect"] [class*="placeholder"] { color: #ffffff !important; opacity: 1 !important; }
span[data-baseweb="tag"] {
    background: linear-gradient(135deg, #2d6080, #3a7a9e) !important;
    border: 1px solid #a8d4f0 !important;
    border-radius: 20px !important;
    color: #ffffff !important;
}
span[data-baseweb="tag"] span { color: #ffffff !important; }
span[data-baseweb="tag"] [role="presentation"] svg { fill: #d0eeff !important; }
[data-baseweb="select"] > div {
    background: rgba(58,111,143,0.75) !important;
    border: 1px solid #7ab3d0 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #d0eeff !important;
    box-shadow: 0 0 0 2px rgba(200,230,255,0.3) !important;
}
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
        'position:fixed','top:0',
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
    'sel_region_card': [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")
st.caption("Select filters to update all charts instantly. Click a state on the map to drill down.")

# ── STICKY FILTER BAR ─────────────────────────────────────────────────────────
st.markdown('<div class="sticky-filter-wrap"><div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)

category_opts = sorted(df['Category'].unique().tolist())
segment_opts  = sorted(df['Segment'].unique().tolist())
year_opts     = sorted(df['Year'].unique().tolist())

fc1, fc2, fc3 = st.columns(3)
with fc1:
    sel_category = st.multiselect("Category", category_opts, default=[v for v in st.session_state.sel_category if v in category_opts], placeholder="All categories", key='_w_category')
with fc2:
    sel_segment = st.multiselect("Segment", segment_opts, default=[v for v in st.session_state.sel_segment if v in segment_opts], placeholder="All segments", key='_w_segment')
with fc3:
    sel_year = st.multiselect("Year", year_opts, default=[v for v in st.session_state.sel_year if v in year_opts], placeholder="All years", key='_w_year')

st.session_state.sel_category = list(sel_category)
st.session_state.sel_segment  = list(sel_segment)
st.session_state.sel_year     = list(sel_year)

pills_html = '<div class="active-pills">'
cs = st.session_state.clicked_state
for v in sel_category: pills_html += f'<div class="pill">📦 {v}</div>'
for v in sel_segment:  pills_html += f'<div class="pill">👥 {v}</div>'
for v in sel_year:     pills_html += f'<div class="pill">📅 {v}</div>'
if cs:                  pills_html += f'<div class="pill state">📍 {cs}</div>'
if not sel_category and not sel_segment and not sel_year and not cs and not st.session_state.sel_region_card:
    pills_html += '<div class="pill" style="color:#4a7fa5;border-color:#2d4a6b;">Showing all data</div>'
pills_html += '</div>'
st.markdown(pills_html, unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

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
_active_regions = list(st.session_state.sel_region_card)
if _active_regions: mask &= df['Region'].isin(_active_regions)
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

k1,k2,k3,k4 = st.columns(4)
k1.metric("💰 Total Sales",     f"${total_sales:,.0f}")
k2.metric("📦 Total Orders",    f"{total_orders:,}")
k3.metric("🧾 Avg Order Value", f"${avg_order_val:,.0f}")
k4.metric("🏆 #1 Region",       top_region_row['Region'])

st.markdown("---")


# ── REGION FILTER CARDS ─────────────────────────────────────────────────────
st.subheader("🌎 Filter by Region")
st.caption("Click a card to filter — click again to deselect. Multiple regions can be active.")

# Apply year / category / segment filters so cards stay in sync with the filter bar
_card_base = df.copy()
if sel_year:     _card_base = _card_base[_card_base['Year'].isin(sel_year)]
if sel_category: _card_base = _card_base[_card_base['Category'].isin(sel_category)]
if sel_segment:  _card_base = _card_base[_card_base['Segment'].isin(sel_segment)]

_all_region_stats = _card_base.groupby('Region').agg(
    Sales=('Sales', 'sum'),
    Orders=('Order ID', 'nunique'),
).reset_index().sort_values('Sales', ascending=False).reset_index(drop=True)
_grand_total = _all_region_stats['Sales'].sum()

_region_meta = {
    'East':    ('🏙️', '#0d2240', '#1a4a80', '#4299e1', '#90cdf4'),
    'West':    ('🌄', '#0d2a1a', '#1a5c36', '#48bb78', '#9ae6b4'),
    'Central': ('🌾', '#2a1500', '#a04010', '#ed8936', '#fbd38d'),
    'South':   ('🌴', '#1e0f38', '#5a35a8', '#9f7aea', '#d6bcfa'),
}

import streamlit.components.v1 as _stcv1, json as _json

_rc_cols = st.columns(len(_all_region_stats))
for _idx, _row in _all_region_stats.iterrows():
    _region   = _row['Region']
    _sales    = _row['Sales']
    _orders   = int(_row['Orders'])
    _share    = _sales / _grand_total * 100 if _grand_total else 0
    _icon     = _region_meta[_region][0]
    _is_act   = _region in st.session_state.sel_region_card
    _check    = "  ✓" if _is_act else ""
    _label    = f"{_icon}  {_region}{_check}\n${_sales:,.0f}\n{_orders:,} orders · {_share:.1f}%"

    with _rc_cols[_idx]:
        if st.button(_label, key=f"rcard_{_region}", use_container_width=True):
            _cards = list(st.session_state.sel_region_card)
            if _region in _cards:
                _cards.remove(_region)
            else:
                _cards.append(_region)
            st.session_state.sel_region_card = _cards
            st.rerun()

if st.session_state.sel_region_card:
    _, _clr_col = st.columns([4, 1])
    with _clr_col:
        if st.button("✕ Clear region filter", key="clear_region_cards", use_container_width=True):
            st.session_state.sel_region_card = []
            st.rerun()

_js_cards = []
for _, _r in _all_region_stats.iterrows():
    _reg = _r['Region']
    _icon, _bg1, _bg2, _border, _accent = _region_meta.get(_reg, ('🌎','#0d1b2a','#1b2a3b','#4299e1','#90cdf4'))
    _act = _reg in st.session_state.sel_region_card
    _js_cards.append({
        'region': _reg, 'bg1': _bg1, 'bg2': _bg2,
        'border': _border, 'accent': _accent, 'active': _act
    })

_stcv1.html(f"""<script>
(function() {{
  var cards = {_json.dumps(_js_cards)};

  function styleAll() {{
    var doc = window.parent.document;
    cards.forEach(function(c) {{
      var allBtns = doc.querySelectorAll('button');
      var btn = null;
      for (var i = 0; i < allBtns.length; i++) {{
        if (allBtns[i].innerText && allBtns[i].innerText.indexOf(c.region) !== -1) {{
          btn = allBtns[i];
          break;
        }}
      }}
      if (!btn) return;

      var want = c.active ? '1' : '0';
      if (btn.getAttribute('data-rs') === want) return;
      btn.setAttribute('data-rs', want);

      var s = btn.style;
      s.setProperty('background', 'linear-gradient(145deg,' + c.bg1 + ' 0%,' + c.bg2 + ' 100%)', 'important');
      s.setProperty('border-radius', '16px', 'important');
      s.setProperty('color', c.accent, 'important');
      s.setProperty('min-height', '130px', 'important');
      s.setProperty('height', 'auto', 'important');
      s.setProperty('width', '100%', 'important');
      s.setProperty('padding', '18px 12px 14px', 'important');
      s.setProperty('font-size', '0.85rem', 'important');
      s.setProperty('white-space', 'pre-line', 'important');
      s.setProperty('line-height', '1.8', 'important');
      s.setProperty('cursor', 'pointer', 'important');
      s.setProperty('text-align', 'center', 'important');
      s.setProperty('transition', 'transform 0.15s ease, opacity 0.15s ease', 'important');
      s.setProperty('will-change', 'transform, box-shadow', 'important');

      if (c.active) {{
        s.setProperty('border', '3px solid ' + c.border, 'important');
        s.setProperty('opacity', '1', 'important');
        var kfId = 'gkf-' + c.region.toLowerCase();
        if (!doc.getElementById(kfId)) {{
          var el = doc.createElement('style');
          el.id = kfId;
          el.textContent =
            '@keyframes ' + kfId + '{{' +
            '0%,100%{{box-shadow:0 0 8px ' + c.border + '55,0 0 18px ' + c.border + '22}}' +
            '50%{{box-shadow:0 0 30px ' + c.border + 'ff,0 0 60px ' + c.border + 'bb,0 0 90px ' + c.border + '44}}' +
            '}}';
          doc.head.appendChild(el);
        }}
        s.setProperty('animation', kfId + ' 2.5s ease-in-out infinite', 'important');
      }} else {{
        s.setProperty('border', '1.5px solid ' + c.border, 'important');
        s.setProperty('opacity', '0.72', 'important');
        s.setProperty('animation', 'none', 'important');
        s.setProperty('box-shadow', 'none', 'important');
      }}

      if (!btn._rsHover) {{
        btn._rsHover = true;
        var border = c.border;
        var isAct = c.active;
        btn.addEventListener('mouseenter', function() {{
          btn.style.setProperty('opacity', '1', 'important');
          btn.style.setProperty('transform', 'translateY(-4px) scale(1.02)', 'important');
          btn.style.setProperty('box-shadow', '0 0 32px ' + border + 'dd, 0 10px 28px rgba(0,0,0,.5)', 'important');
          btn.style.setProperty('animation', 'none', 'important');
        }});
        btn.addEventListener('mouseleave', function() {{
          btn.style.setProperty('transform', '', 'important');
          if (isAct) {{
            btn.style.setProperty('animation', 'gkf-' + c.region.toLowerCase() + ' 2.5s ease-in-out infinite', 'important');
          }}
        }});
      }}
    }});
  }}

  styleAll();
  var obs = new MutationObserver(function(muts) {{
    var hasNew = muts.some(function(m) {{ return m.addedNodes.length > 0; }});
    if (hasNew) styleAll();
  }});
  obs.observe(window.parent.document.body, {{childList:true, subtree:true}});
}})();
</script>""", height=0)

st.markdown("---")


# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("📍 Sales Distribution by State  ·  Click a state to drill down")

# Map base: respect year/category/segment but NOT region-card or clicked_state
# so all states remain visible on the map for geographic context
_map_base = df.copy()
if sel_year:     _map_base = _map_base[_map_base['Year'].isin(sel_year)]
if sel_category: _map_base = _map_base[_map_base['Category'].isin(sel_category)]
if sel_segment:  _map_base = _map_base[_map_base['Segment'].isin(sel_segment)]

all_state_sales = _map_base.groupby(['State', 'State Code'])['Sales'].sum().reset_index()
_map_total = all_state_sales['Sales'].sum()
all_state_sales['Share'] = all_state_sales['Sales'] / _map_total * 100

if not st.session_state.clicked_state and not st.session_state.sel_region_card:
    st.markdown("""<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:15px;align-items:center;">
        <span style="color:#90cdf4;font-size:0.8rem;">⚡ Quick select:</span>""", unsafe_allow_html=True)
    top_states_quick = all_state_sales.nlargest(5, 'Sales')['State'].tolist()
    quick_cols = st.columns(len(top_states_quick))
    for i, state in enumerate(top_states_quick):
        with quick_cols[i]:
            if st.button(f"🏆 {state}", key=f"quick_{state}", use_container_width=True):
                st.session_state.clicked_state = state
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.clicked_state:
    col_info, col_clear_map = st.columns([5, 1])
    with col_info:
        _sv = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]['Sales'].values
        _st = f"${_sv[0]:,.0f}" if len(_sv) > 0 else "N/A"
        st.markdown(f"""<div style="background:linear-gradient(135deg,#1e3a5f,#2d5a8a);border:1px solid #4299e1;
border-radius:10px;padding:8px 15px;margin-bottom:15px;">
<div style="display:flex;align-items:center;gap:8px;">
<span style="color:#90cdf4;font-size:0.8rem;">📍 SELECTED STATE:</span>
<span style="color:white;font-weight:700;font-size:1rem;">{st.session_state.clicked_state}</span>
<span style="color:#48bb78;font-size:0.9rem;margin-left:auto;">{_st}</span>
</div></div>""", unsafe_allow_html=True)
    with col_clear_map:
        if st.button("✕ Clear", key="clear_state_btn", use_container_width=True):
            st.session_state.clicked_state = None
            st.rerun()

# ── Build map with region-aware coloring ──────────────────────────────────
_region_fill_colors = {
    'East':    [[0, 'rgba(66,153,225,0.12)'],  [1, 'rgba(66,153,225,0.55)']],
    'West':    [[0, 'rgba(72,187,120,0.12)'],  [1, 'rgba(72,187,120,0.55)']],
    'Central': [[0, 'rgba(237,137,54,0.12)'],  [1, 'rgba(237,137,54,0.55)']],
    'South':   [[0, 'rgba(159,122,234,0.12)'], [1, 'rgba(159,122,234,0.55)']],
}
_region_border_colors = {'East':'#4299e1','West':'#48bb78','Central':'#ed8936','South':'#9f7aea'}

_sel_regions = st.session_state.sel_region_card

if _sel_regions:
    fig_map = px.choropleth(
        all_state_sales, locations='State Code', locationmode="USA-states",
        color='Sales', scope="usa", hover_name='State',
        color_continuous_scale=[[0,'rgba(40,40,60,0.5)'],[1,'rgba(80,80,100,0.5)']],
        labels={'Sales': 'Total Sales ($)'},
        custom_data=['Share']
    )
    fig_map.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Total Sales: $%{z:,.0f}<br>"
            "Revenue Share: %{customdata[0]:.1f}%"
            "<extra></extra>"
        ),
        marker_line_color='rgba(100,100,120,0.3)', marker_line_width=0.5
    )
    for _sreg in _sel_regions:
        _reg_df = all_state_sales[all_state_sales['State'].isin(
            _map_base[_map_base['Region'] == _sreg]['State'].unique()
        )].copy()
        if not _reg_df.empty:
            _fcol   = _region_fill_colors.get(_sreg, [[0,'rgba(255,255,255,0.1)'],[1,'rgba(255,255,255,0.5)']])
            _bcol   = _region_border_colors.get(_sreg, '#ffffff')
            fig_map.add_trace(go.Choropleth(
                locations=_reg_df['State Code'].tolist(),
                z=_reg_df['Sales'].tolist(),
                locationmode="USA-states",
                colorscale=_fcol,
                showscale=False,
                marker_line_color=_bcol,
                marker_line_width=2.5,
                text=_reg_df['State'].tolist(),
                customdata=_reg_df[['Share']].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Sales: $%{z:,.0f}<br>"
                    "Revenue Share: %{customdata[0]:.1f}%<br>"
                    "Region: " + _sreg +
                    "<extra></extra>"
                ),
                name=_sreg,
            ))
else:
    fig_map = px.choropleth(
        all_state_sales, locations='State Code', locationmode="USA-states",
        color='Sales', scope="usa", hover_name='State',
        color_continuous_scale="Blues", labels={'Sales': 'Total Sales ($)'},
        custom_data=['Share']
    )
    fig_map.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Total Sales: $%{z:,.0f}<br>"
            "Revenue Share: %{customdata[0]:.1f}%"
            "<extra></extra>"
        )
    )

if st.session_state.clicked_state:
    _hl = all_state_sales[all_state_sales['State'] == st.session_state.clicked_state]
    if not _hl.empty:
        fig_map.add_trace(go.Choropleth(
            locations=_hl['State Code'], z=[1], locationmode="USA-states",
            colorscale=[[0,"rgba(233,69,96,0)"],[1,"rgba(233,69,96,0)"]],
            showscale=False, marker_line_color="#e94560",
            marker_line_width=3, hoverinfo='skip',
        ))

fig_map.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0}, geo_bgcolor='rgba(0,0,0,0)',
    coloraxis_colorbar=dict(title="Sales ($)", tickprefix="$"),
    showlegend=False,
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

# ── Smart map insight banner ──────────────────────────────────────────────────
_n_active_states   = len(state_sales[state_sales['Sales'] > 0])
_top5_share        = state_sales.nlargest(5, 'Sales')['Sales'].sum() / total_sales * 100 if total_sales else 0
_bottom_state      = state_sales.sort_values('Sales').iloc[0]
_avg_state_sales   = state_sales['Sales'].mean()
_above_avg_states  = len(state_sales[state_sales['Sales'] > _avg_state_sales])
_concentration_lbl = "Highly Concentrated" if _top5_share > 60 else "Moderately Spread" if _top5_share > 40 else "Well Distributed"
_concentration_cls = "#e94560" if _top5_share > 60 else "#ed8936" if _top5_share > 40 else "#48bb78"

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0a1628 0%, #0f2040 50%, #0a1628 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
">
  <!-- Glow accent -->
  <div style="position:absolute;top:-40px;right:-40px;width:160px;height:160px;
    background:radial-gradient(circle, rgba(66,153,225,0.12) 0%, transparent 70%);
    pointer-events:none;"></div>

  <!-- Header row -->
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
    <div style="width:6px;height:28px;background:linear-gradient(180deg,#4299e1,#63b3ed);border-radius:3px;"></div>
    <span style="color:#63b3ed;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;">
      Geographic Intelligence
    </span>
    <div style="margin-left:auto;background:rgba(66,153,225,0.1);border:1px solid #2d5a8a;
      border-radius:20px;padding:3px 10px;">
      <span style="color:#90cdf4;font-size:0.72rem;">{_n_active_states} active states</span>
    </div>
  </div>

  <!-- 4-stat grid -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">

    <!-- Stat 1: Top state -->
    <div style="background:rgba(66,153,225,0.08);border:1px solid #1e3a5f;border-radius:10px;padding:14px 12px;">
      <div style="color:#718096;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
        👑 Revenue Leader
      </div>
      <div style="color:#fff;font-size:1.15rem;font-weight:700;line-height:1.2;">{top_state['State']}</div>
      <div style="color:#48bb78;font-size:0.8rem;margin-top:4px;font-weight:600;">
        ${top_state['Sales']:,.0f}
      </div>
      <div style="margin-top:8px;background:rgba(255,255,255,0.06);border-radius:4px;height:4px;">
        <div style="width:{min(state_share*2, 100):.0f}%;height:4px;background:linear-gradient(90deg,#4299e1,#63b3ed);border-radius:4px;"></div>
      </div>
      <div style="color:#90cdf4;font-size:0.7rem;margin-top:4px;">{state_share:.1f}% of total</div>
    </div>

    <!-- Stat 2: Top-5 concentration -->
    <div style="background:rgba(66,153,225,0.08);border:1px solid #1e3a5f;border-radius:10px;padding:14px 12px;">
      <div style="color:#718096;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
        🎯 Top-5 Concentration
      </div>
      <div style="color:#fff;font-size:1.15rem;font-weight:700;line-height:1.2;">{_top5_share:.1f}%</div>
      <div style="font-size:0.78rem;margin-top:4px;font-weight:600;color:{_concentration_cls};">
        {_concentration_lbl}
      </div>
      <div style="margin-top:8px;background:rgba(255,255,255,0.06);border-radius:4px;height:4px;">
        <div style="width:{_top5_share:.0f}%;height:4px;background:linear-gradient(90deg,{_concentration_cls},{_concentration_cls}88);border-radius:4px;"></div>
      </div>
      <div style="color:#90cdf4;font-size:0.7rem;margin-top:4px;">5 states drive majority</div>
    </div>

    <!-- Stat 3: States above average -->
    <div style="background:rgba(66,153,225,0.08);border:1px solid #1e3a5f;border-radius:10px;padding:14px 12px;">
      <div style="color:#718096;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
        📈 Above-Average States
      </div>
      <div style="color:#fff;font-size:1.15rem;font-weight:700;line-height:1.2;">{_above_avg_states} <span style="font-size:0.8rem;color:#718096;">/ {_n_active_states}</span></div>
      <div style="color:#ed8936;font-size:0.78rem;margin-top:4px;font-weight:600;">
        Avg ${_avg_state_sales:,.0f}
      </div>
      <div style="margin-top:8px;background:rgba(255,255,255,0.06);border-radius:4px;height:4px;">
        <div style="width:{_above_avg_states/_n_active_states*100 if _n_active_states else 0:.0f}%;height:4px;background:linear-gradient(90deg,#ed8936,#f6ad55);border-radius:4px;"></div>
      </div>
      <div style="color:#90cdf4;font-size:0.7rem;margin-top:4px;">{_above_avg_states/_n_active_states*100 if _n_active_states else 0:.0f}% outperforming</div>
    </div>

    <!-- Stat 4: Weakest link -->
    <div style="background:rgba(233,69,96,0.06);border:1px solid #3d1a22;border-radius:10px;padding:14px 12px;">
      <div style="color:#718096;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
        ⚠️ Lowest Performer
      </div>
      <div style="color:#fff;font-size:1.15rem;font-weight:700;line-height:1.2;">{_bottom_state['State']}</div>
      <div style="color:#e94560;font-size:0.8rem;margin-top:4px;font-weight:600;">
        ${_bottom_state['Sales']:,.0f}
      </div>
      <div style="margin-top:8px;background:rgba(255,255,255,0.06);border-radius:4px;height:4px;">
        <div style="width:{_bottom_state['Sales']/top_state['Sales']*100 if top_state['Sales'] else 0:.1f}%;height:4px;background:linear-gradient(90deg,#e94560,#fc8181);border-radius:4px;"></div>
      </div>
      <div style="color:#90cdf4;font-size:0.7rem;margin-top:4px;">
        {_bottom_state['Sales']/top_state['Sales']*100 if top_state['Sales'] else 0:.1f}% of leader's sales
      </div>
    </div>

  </div>
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
    _sun_cmap = {
        "Consumer":        "#1a56a0",
        "Corporate":       "#4299e1",
        "Home Office":     "#90cdf4",
        "Furniture":       "#1a365d",
        "Office Supplies": "#1e4a6e",
        "Technology":      "#17364f",
        "(?)":             "#0d1b2a",
    }
    fig_sun = px.sunburst(
        _sun_df, path=['Category','Segment'], values='Sales',
        color='Segment', color_discrete_map=_sun_cmap
    )
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>",
        textfont=dict(size=11),
        insidetextorientation='radial',
        marker=dict(colors=[_sun_cmap.get(lbl, "#1e3a5f") for lbl in fig_sun.data[0].labels])
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

# ── Category breakdown A vs B ─────────────────────────────────────────────────
ab_cat_a = grp_a.groupby("Category").agg(Sales=("Sales","sum"), **{"Order Count":("Order ID","nunique")}).reset_index().assign(Group=val_a)
ab_cat_b = grp_b.groupby("Category").agg(Sales=("Sales","sum"), **{"Order Count":("Order ID","nunique")}).reset_index().assign(Group=val_b)
ab_cat   = pd.concat([ab_cat_a, ab_cat_b], ignore_index=True)

group_a_color = "#4299e1"
group_b_color = "#e94560"

fig_cat_ab = px.bar(
    ab_cat,
    x="Category",
    y="Sales",
    color="Group",
    barmode="group",
    color_discrete_map={val_a: group_a_color, val_b: group_b_color},
    labels={"Sales": "Total Sales ($)", "Group": ""},
    custom_data=["Order Count", "Group"],
)

fig_cat_ab.for_each_trace(
    lambda t: t.update(
        hovertemplate=(
            f"<b>{t.name}</b><br>"
            "<b>%{x}</b><br>"
            "Sales: $%{y:,.0f}<br>"
            "Orders: %{customdata[0]:,}"
            "<extra></extra>"
        )
    )
)

fig_cat_ab.update_layout(
    title=dict(text="Category Breakdown — A vs B", font=dict(size=13, color="white"), x=0.5),
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        tickprefix="$", tickformat=",.0f",
        gridcolor='rgba(128,128,128,0.2)',
        title=dict(text="Sales ($)", font=dict(color="white")),
        tickfont=dict(color="white")
    ),
    xaxis=dict(title="", showticklabels=False, showgrid=False, zeroline=False, showline=False),
    margin=dict(l=10, r=10, t=40, b=30),
    height=350,
    hovermode="closest",
)

st.plotly_chart(fig_cat_ab, use_container_width=True, key="ab_cat")

st.markdown(f"""
<div style="display:flex; justify-content:center; gap:20px; margin-bottom:15px;">
    <div style="display:flex; align-items:center; gap:8px; background:{group_a_color}; padding:5px 15px; border-radius:20px; box-shadow:0 2px 4px rgba(0,0,0,0.2);">
        <span style="color:white; font-weight:600;">🔵 {val_a}</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px; background:{group_b_color}; padding:5px 15px; border-radius:20px; box-shadow:0 2px 4px rgba(0,0,0,0.2);">
        <span style="color:white; font-weight:600;">🔴 {val_b}</span>
    </div>
</div>
""", unsafe_allow_html=True)

categories = sorted(filtered_df['Category'].unique())
category_colors = {'Furniture': '#48bb78', 'Office Supplies': '#f39c12', 'Technology': '#9b59b6'}
cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    color = category_colors.get(cat, '#4299e1')
    icon = '📦' if cat == 'Furniture' else '📎' if cat == 'Office Supplies' else '💻'
    with cols[i]:
        st.markdown(f"""
        <div style="background:{color};border-radius:20px;padding:6px 0;text-align:center;margin-top:-15px;margin-bottom:10px;box-shadow:0 2px 4px rgba(0,0,0,0.2);">
            <span style="color:white;font-weight:600;font-size:0.85rem;">{icon} {cat}</span>
        </div>
        """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
for col, cat_name, icon in [(col1,'Furniture','📦'), (col2,'Office Supplies','📎'), (col3,'Technology','💻')]:
    a_row = ab_cat_a[ab_cat_a['Category'] == cat_name]
    b_row = ab_cat_b[ab_cat_b['Category'] == cat_name]
    a_orders = int(a_row['Order Count'].values[0]) if not a_row.empty else 0
    b_orders = int(b_row['Order Count'].values[0]) if not b_row.empty else 0
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1b2a3b);border:1px solid #2d4a6b;border-radius:10px;padding:12px;text-align:center;">
            <div style="color:#63b3ed;font-size:0.75rem;text-transform:uppercase;margin-bottom:5px;">{icon} {cat_name} Orders</div>
            <div style="display:flex;justify-content:center;gap:25px;margin-top:5px;">
                <div><span style="color:{group_a_color};font-weight:600;">🔵</span> <span style="color:white;">{a_orders}</span></div>
                <div><span style="color:{group_b_color};font-weight:600;">🔴</span> <span style="color:white;">{b_orders}</span></div>
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
    st.markdown(f'<div class="insight-card warn"><div class="icon">⚠️</div><div class="label">Underperformer Alert</div><div class="value">{bottom_subcat["Sub-Category"]}</div><div class="detail">Only <strong>${bottom_subcat["Sales"]:,.0f}</strong> in sales — lowest sub-category. Review pricing, promotion, and placement.</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── REGION × SEGMENT ──────────────────────────────────────────────────────────
st.header("🌎 Region vs. Segment Matrix")
fig_grouped = px.bar(region_seg, x='Region', y='Sales', color='Segment',
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={'Sales':'Total Sales ($)'})
fig_grouped.for_each_trace(
    lambda t: t.update(
        hovertemplate=f"<b>%{{x}}</b><br>Segment: {t.name}<br>Sales: $%{{y:,.0f}}<extra></extra>"
    )
)
st.plotly_chart(fig_grouped, use_container_width=True, key="grouped_region_seg")

best_rs  = region_seg.sort_values('Sales', ascending=False).iloc[0]
worst_rs = region_seg.sort_values('Sales').iloc[0]
st.markdown(f'<div class="insight-card good"><div class="icon">🎯</div><div class="label">Strategic Insight</div><div class="value">Best combo: {best_rs["Region"]} × {best_rs["Segment"]}</div><div class="detail"><strong>{best_rs["Segment"]}</strong> in <strong>{best_rs["Region"]}</strong> delivers the highest sales at <strong>${best_rs["Sales"]:,.0f}</strong>. Lowest: <strong>{worst_rs["Segment"]}</strong> in <strong>{worst_rs["Region"]}</strong> (${worst_rs["Sales"]:,.0f}).</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── SALES FORECAST ────────────────────────────────────────────────────────────
st.header("🔮 Sales Forecast")
st.caption("Linear trend + seasonal decomposition forecast based on historical data in current filter.")

_fc_col1, _fc_col2 = st.columns([3, 1])
with _fc_col2:
    _fc_months = st.selectbox("Forecast horizon", [3, 6, 12], index=1, key="fc_months",
                               format_func=lambda x: f"{x} months")
    _fc_dim = st.selectbox("Breakdown by", ["Total", "Category", "Region"], key="fc_dim")

_fc_df = filtered_df.copy()
_fc_df['Month_dt'] = pd.to_datetime(_fc_df['Order Date']).dt.to_period('M').dt.to_timestamp()

if _fc_dim == "Total":
    _series_dict = {"Total": _fc_df.groupby('Month_dt')['Sales'].sum()}
elif _fc_dim == "Category":
    _series_dict = {cat: grp.groupby('Month_dt')['Sales'].sum()
                    for cat, grp in _fc_df.groupby('Category')}
else:
    _series_dict = {reg: grp.groupby('Month_dt')['Sales'].sum()
                    for reg, grp in _fc_df.groupby('Region')}

def _forecast_series(series, n_months):
    series = series.sort_index().asfreq('MS', fill_value=0)
    if len(series) < 4:
        return None, None, None
    y = series.values.astype(float)
    x = np.arange(len(y))
    coeffs = np.polyfit(x, y, 1)
    trend  = np.poly1d(coeffs)
    detrended = y - trend(x)
    months = series.index.month
    seasonal = np.array([detrended[months == m].mean() if (months == m).any() else 0 for m in range(1, 13)])
    last_date = series.index[-1]
    future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=n_months, freq='MS')
    future_x = np.arange(len(y), len(y) + n_months)
    future_trend = trend(future_x)
    future_seasonal = np.array([seasonal[d.month - 1] for d in future_dates])
    forecast = np.maximum(future_trend + future_seasonal, 0)
    residuals = y - (trend(x) + np.array([seasonal[m-1] for m in months]))
    sigma = residuals.std() * 1.5
    lower = np.maximum(forecast - sigma, 0)
    upper = forecast + sigma
    return series, pd.Series(forecast, index=future_dates), (
        pd.Series(lower, index=future_dates),
        pd.Series(upper, index=future_dates)
    )

_dim_colors = {
    "Total":          "#4299e1",
    "Furniture":      "#48bb78",
    "Office Supplies":"#ed8936",
    "Technology":     "#9f7aea",
    "West":           "#48bb78",
    "East":           "#4299e1",
    "Central":        "#ed8936",
    "South":          "#9f7aea",
}

with _fc_col1:
    fig_fc = go.Figure()
    _fc_total_next = 0
    _fc_growth_pcts = []
    _hist = None

    for _dim_name, _dim_series in _series_dict.items():
        _color = _dim_colors.get(_dim_name, "#90cdf4")
        _hist, _fc_vals, _ci = _forecast_series(_dim_series, _fc_months)
        if _hist is None:
            continue

        fig_fc.add_trace(go.Scatter(
            x=_hist.index, y=_hist.values,
            name=f"{_dim_name} (actual)",
            line=dict(color=_color, width=2.5),
            mode="lines+markers",
            marker=dict(size=5),
            hovertemplate=f"<b>{_dim_name}</b><br>%{{x|%b %Y}}<br>Actual: $%{{y:,.0f}}<extra></extra>"
        ))

        _bridge_x = [_hist.index[-1], _fc_vals.index[0]]
        _bridge_y = [_hist.values[-1], _fc_vals.values[0]]
        fig_fc.add_trace(go.Scatter(
            x=_bridge_x, y=_bridge_y,
            line=dict(color=_color, width=2, dash='dot'),
            showlegend=False, hoverinfo='skip', mode='lines'
        ))
        fig_fc.add_trace(go.Scatter(
            x=_fc_vals.index, y=_fc_vals.values,
            name=f"{_dim_name} (forecast)",
            line=dict(color=_color, width=2.5, dash='dash'),
            mode="lines+markers",
            marker=dict(size=6, symbol='diamond'),
            hovertemplate=f"<b>{_dim_name} forecast</b><br>%{{x|%b %Y}}<br>$%{{y:,.0f}}<extra></extra>"
        ))

        _lo, _hi = _ci
        fig_fc.add_trace(go.Scatter(
            x=list(_fc_vals.index) + list(_fc_vals.index[::-1]),
            y=list(_hi.values) + list(_lo.values[::-1]),
            fill='toself',
            fillcolor=f"rgba{tuple(int(_color.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + (0.12,)}",
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False, hoverinfo='skip', name=f"{_dim_name} CI"
        ))

        _fc_total_next += _fc_vals.sum()
        _last_period_actual = _hist.tail(_fc_months).sum()
        if _last_period_actual > 0:
            _fc_growth_pcts.append((_fc_vals.sum() - _last_period_actual) / _last_period_actual * 100)

    _today_line = str(_hist.index[-1]) if _hist is not None else str(pd.Timestamp.now())
    fig_fc.add_vline(x=_today_line, line_dash="dot", line_color="rgba(255,255,255,0.3)")

    fig_fc.update_layout(
        title=dict(text=f"Sales Forecast — Next {_fc_months} Months", font=dict(size=14), x=0.5),
        xaxis=dict(title="", tickformat="%b %Y", tickangle=-30),
        yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="rgba(128,128,128,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5,
                    font=dict(size=10)),
        margin=dict(l=10, r=10, t=45, b=10),
        hovermode="x unified", height=420,
    )
    st.plotly_chart(fig_fc, use_container_width=True, key="fc_chart")

# Forecast summary cards
_avg_growth = np.mean(_fc_growth_pcts) if _fc_growth_pcts else 0
_growth_cls = "good" if _avg_growth >= 0 else "alert"
_growth_arrow = "▲" if _avg_growth >= 0 else "▼"

_fc_sum_cols = st.columns(3)
with _fc_sum_cols[0]:
    st.markdown(f"""
    <div class="insight-card good">
      <div class="icon">🔮</div>
      <div class="label">Projected Revenue (next {_fc_months}mo)</div>
      <div class="value">${_fc_total_next:,.0f}</div>
      <div class="detail">Based on linear trend + seasonal pattern from filtered data.</div>
    </div>""", unsafe_allow_html=True)

with _fc_sum_cols[1]:
    st.markdown(f"""
    <div class="insight-card {_growth_cls}">
      <div class="icon">📈</div>
      <div class="label">Projected Growth vs Prior Period</div>
      <div class="value">{_growth_arrow} {abs(_avg_growth):.1f}%</div>
      <div class="detail">Compared to the previous {_fc_months} months of actual sales.</div>
    </div>""", unsafe_allow_html=True)

with _fc_sum_cols[2]:
    _best_dim = max(_series_dict.keys(),
                    key=lambda k: _forecast_series(_series_dict[k], _fc_months)[1].sum()
                    if _forecast_series(_series_dict[k], _fc_months)[1] is not None else 0)
    st.markdown(f"""
    <div class="insight-card">
      <div class="icon">🏆</div>
      <div class="label">Highest Forecast Contributor</div>
      <div class="value">{_best_dim}</div>
      <div class="detail">Expected to lead in revenue over the forecast window.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── CITIES TABLE ──────────────────────────────────────────────────────────────
st.header("🏙️ Top Cities by Sales")

# City table uses filtered_df which already has all active filters applied
# (year, category, segment, region cards, clicked state)
_city_base = filtered_df

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
_agg = _agg[['State', 'City', 'Total Sales', 'Orders', 'Customers', 'Avg Order']]

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

st.markdown("---")
