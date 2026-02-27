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

# ── CSS (ปรับปรุงเพื่อแก้ปัญหาการบังกัน) ──────────────────────────────────────────
st.markdown("""
<style>
/* สร้างช่องว่างคงที่เพื่อไม่ให้ Filter บังเนื้อหา */
#filter-spacer { 
    height: 180px !important; 
    display: block; 
}

.filter-bar {
    background: linear-gradient(135deg, #3a6f8f 0%, #4a85a8 50%, #5a9abf 100%);
    border: 1px solid #7ab3d0;
    border-radius: 0 0 14px 14px;
    padding: 12px 20px 10px 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    position: relative; 
    overflow: hidden;
}

/* ปรับสีตัวอักษรใน Filter */
.filter-bar label { color: #ffffff !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.filter-bar [data-baseweb="select"] input { color: #ffffff !important; }

/* Active pills */
.active-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; margin-bottom:2px; }
.pill {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(30,58,95,0.9); border:1px solid #2d5a8a;
    border-radius:16px; padding:3px 10px; font-size:0.73rem; color:#90cdf4;
}

.state-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:linear-gradient(90deg,#1e3a5f,#2d5a8a);
    border:1px solid #4299e1; border-radius:20px;
    padding:5px 14px; font-size:0.8rem; color:#90cdf4; margin-bottom:10px;
}

.insight-card {
    background:linear-gradient(135deg,#0d1b2a 0%,#1b2a3b 100%);
    border-left:4px solid #4299e1; border-radius:8px;
    padding:14px 18px; margin-bottom:10px; color:#f0f0f0;
}
.insight-card.good { border-left-color:#48bb78; }
.insight-card.warn { border-left-color:#ed8936; }
</style>
""", unsafe_allow_html=True)

# ── Sentinel + JavaScript (Fixed Filter Logic) ──────────────────────────────
st.markdown('<span id="filter-sentinel"></span>', unsafe_allow_html=True)

import streamlit.components.v1 as _stc
_stc.html("""
<script>
(function () {
  function fixFilter() {
    var sentinel = document.getElementById('filter-sentinel');
    if (!sentinel) return;
    var block = sentinel.closest('[data-testid="stVerticalBlock"]');
    if (!block || block.getAttribute('data-filter-fixed') === '1') return;
    
    block.setAttribute('data-filter-fixed', '1');
    var spacer = document.createElement('div');
    spacer.id = 'filter-spacer';
    block.parentNode.insertBefore(spacer, block);

    function applyFixed() {
      var parentRect = block.parentElement.getBoundingClientRect();
      block.style.cssText = `
        position: fixed; top: 0; left: ${parentRect.left}px;
        width: ${parentRect.width}px; z-index: 9999;
        background: rgba(8, 15, 26, 0.98); backdrop-filter: blur(10px);
      `;
    }
    applyFixed();
    window.addEventListener('resize', applyFixed);
  }
  fixFilter();
  new MutationObserver(fixFilter).observe(document.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

# ── Data Loading & Mapping ────────────────────────────────────────────────────
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
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ── Session State ─────────────────────────────────────────────────────────────
if 'clicked_state' not in st.session_state: st.session_state.clicked_state = None

# ── STICKY FILTER BAR ─────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar"><div style="font-size:0.7rem; color:#63b3ed; font-weight:700; letter-spacing:0.1em; margin-bottom:8px;">🧭 DASHBOARD FILTERS</div>', unsafe_allow_html=True)

fc1, fc2, fc3, fc4 = st.columns(4)
with fc1: sel_region = st.multiselect("Region", sorted(df['Region'].unique()), placeholder="All")
with fc2: sel_category = st.multiselect("Category", sorted(df['Category'].unique()), placeholder="All")
with fc3: sel_segment = st.multiselect("Segment", sorted(df['Segment'].unique()), placeholder="All")
with fc4: sel_year = st.multiselect("Year", sorted(df['Year'].unique()), placeholder="All")

# Pills display
pills_html = '<div class="active-pills">'
for v in sel_region + sel_category + sel_segment + [str(y) for y in sel_year]:
    pills_html += f'<div class="pill">● {v}</div>'
if st.session_state.clicked_state:
    pills_html += f'<div class="pill" style="border-color:#e94560; color:#feb2b2;">📍 {st.session_state.clicked_state}</div>'
pills_html += '</div>'
st.markdown(pills_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Filtering Logic ───────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df))
if sel_region: mask &= df['Region'].isin(sel_region)
if sel_category: mask &= df['Category'].isin(sel_category)
if sel_segment: mask &= df['Segment'].isin(sel_segment)
if sel_year: mask &= df['Year'].isin(sel_year)
if st.session_state.clicked_state: mask &= df['State'] == st.session_state.clicked_state

filtered_df = df[mask]

# ── Main Content ─────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")

if st.session_state.clicked_state:
    c_badge, c_clear = st.columns([5, 1])
    c_badge.markdown(f'<div class="state-badge">📍 Map filter active: <strong>{st.session_state.clicked_state}</strong></div>', unsafe_allow_html=True)
    if c_clear.button("✕ Clear Map", use_container_width=True):
        st.session_state.clicked_state = None
        st.rerun()

# KPIs
k1, k2, k3, k4 = st.columns(4)
total_sales = filtered_df['Sales'].sum()
k1.metric("💰 Total Sales", f"${total_sales:,.0f}")
k2.metric("📦 Total Orders", f"{filtered_df['Order ID'].nunique():,}")
k3.metric("🧾 Avg Order Value", f"${(total_sales/filtered_df['Order ID'].nunique() if total_sales else 0):,.0f}")
k4.metric("🏆 Top Category", filtered_df.groupby('Category')['Sales'].sum().idxmax() if not filtered_df.empty else "N/A")

st.markdown("---")

# Map
st.subheader("📍 Sales Distribution")
all_state_sales = df.groupby(['State','State Code'])['Sales'].sum().reset_index()
fig_map = px.choropleth(
    all_state_sales, locations='State Code', locationmode="USA-states",
    color='Sales', scope="usa", color_continuous_scale="Blues"
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, geo_bgcolor='rgba(0,0,0,0)')
map_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", key="main_map")

if map_event and map_event.selection and map_event.selection.get("points"):
    clicked_code = map_event.selection["points"][0].get("location")
    st.session_state.clicked_state = abbrev_to_state.get(clicked_code)
    st.rerun()

st.markdown("---")

# City Table (ตรงที่คุณต้องการให้แก้)
st.header("🏙️ Performance by City")
city_stats = filtered_df.groupby('City')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).reset_index(drop=True)
city_stats.index += 1
city_stats.insert(0, 'Rank', city_stats.index)

st.dataframe(
    city_stats,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", width="small"),
        "City": st.column_config.TextColumn("City Name"),
        "Sales": st.column_config.NumberColumn("Total Sales", format="$%,.2f")
    }
)

st.markdown("---")

# Region vs Segment
st.header("🌎 Region vs. Segment Matrix")
region_seg = filtered_df.groupby(['Region','Segment'])['Sales'].sum().reset_index()
fig_rs = px.bar(region_seg, x='Region', y='Sales', color='Segment', barmode='group')
st.plotly_chart(fig_rs, use_container_width=True)
