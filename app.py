import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Geographic Sales Intelligence",
    page_icon="🗺️",
    layout="wide"
)

# ── CSS (Consistent with your theme) ─────────────────────────────────────────
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
.filter-title { font-size: 0.68rem; font-weight: 700; color: #63b3ed; text-transform: uppercase; letter-spacing: 0.13em; margin-bottom: 8px; }
.active-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; }
.pill { display:inline-flex; align-items:center; gap:5px; background:rgba(30,58,95,0.9); border:1px solid #2d5a8a; border-radius:16px; padding:3px 10px; font-size:0.73rem; color:#90cdf4; }
.insight-card { background:linear-gradient(135deg,#0d1b2a 0%,#1b2a3b 100%); border-left:4px solid #4299e1; border-radius:8px; padding:14px 18px; margin-bottom:10px; color:#f0f0f0; }
.insight-card.warn  { border-left-color:#ed8936; }
.insight-card.good  { border-left-color:#48bb78; }
.insight-card .label { font-size:0.7rem; color:#a0aec0; text-transform:uppercase; margin-bottom:3px; }
.insight-card .value { font-size:1.35rem; font-weight:700; color:#fff; }
</style>
""", unsafe_allow_html=True)

# ── State Mapping & Data Load ────────────────────────────────────────────────
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

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    df['State Code'] = df['State'].map(us_state_to_abbrev)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    return df

df = load_data()

# ── TITLE ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Regional Sales Intelligence")

# ── FILTERS ───────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar"><div class="filter-title">🧭 &nbsp;Dashboard Filters</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: sel_region = st.multiselect("Region", sorted(df['Region'].unique()))
with c2: sel_category = st.multiselect("Category", sorted(df['Category'].unique()))
with c3: sel_segment = st.multiselect("Segment", sorted(df['Segment'].unique()))

mask = pd.Series([True] * len(df), index=df.index)
if sel_region: mask &= df['Region'].isin(sel_region)
if sel_category: mask &= df['Category'].isin(sel_category)
if sel_segment: mask &= df['Segment'].isin(sel_segment)
filtered_df = df[mask]
st.markdown('</div>', unsafe_allow_html=True)

# ── CITY TABLE (Optimized) ────────────────────────────────────────────────────
st.header("🏙️ Cities by Revenue")

# Group data
city_table = filtered_df.groupby('City')['Sales'].sum().reset_index()
city_table = city_table.sort_values('Sales', ascending=False).reset_index(drop=True)
city_table.index += 1
city_table.insert(0, 'Rank', city_table.index)
city_table['Share %'] = (city_table['Sales'] / city_table['Sales'].sum() * 100)

# Calculating Z-Score for Sales
# Formula: (x - mean) / std
mean_sales = city_table['Sales'].mean()
std_sales = city_table['Sales'].std()
city_table['Z-Score'] = (city_table['Sales'] - mean_sales) / std_sales

# Displaying the Table
st.dataframe(
    city_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", width="small", help="Global rank in current selection"),
        "City": st.column_config.TextColumn("City Name"),
        "Sales": st.column_config.NumberColumn("Total Sales", format="$%,d"), # Fixed: Added comma
        "Share %": st.column_config.NumberColumn("Share %", format="%.1f%%"),
        "Z-Score": st.column_config.NumberColumn("Z-Score", format="%.2f", help="Distance from mean sales in standard deviations")
    }
)

st.markdown("---")

# ── Z-SCORE ANALYSIS SECTION ──────────────────────────────────────────────────
st.header("📉 Statistical Outlier Detection (Z-Score)")
st.caption("A Z-score tells you how many standard deviations a city is from the average. Values > 2.0 indicate exceptionally high-performing hubs.")

col_z1, col_z2 = st.columns([2, 1])

with col_z1:
    # Filter to show interesting Z-Scores (Top 15)
    z_plot_df = city_table.head(15)
    fig_z = px.bar(
        z_plot_df, x='City', y='Z-Score',
        color='Z-Score', color_continuous_scale='RdBu',
        range_color=[-3, 3],
        template="plotly_dark",
        title="Market Performance Significance (Top 15 Cities)"
    )
    fig_z.add_hline(y=2, line_dash="dash", line_color="#48bb78", annotation_text="High Outlier (>2.0)")
    fig_z.add_hline(y=0, line_color="white", opacity=0.3)
    fig_z.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_z, use_container_width=True)

with col_z2:
    outliers_count = len(city_table[city_table['Z-Score'] > 2])
    top_outlier = city_table.iloc[0]
    
    st.markdown(f"""
    <div class="insight-card good">
      <div class="label">Statistical Health</div>
      <div class="value">{outliers_count} Extreme Outliers</div>
      <div style="font-size:0.85rem; color:#90cdf4; margin-top:5px;">
        Detected <strong>{outliers_count}</strong> cities performing significantly above the statistical norm.
      </div>
    </div>
    
    <div class="insight-card">
      <div class="label">Top Market Anomaly</div>
      <div class="value">{top_outlier['City']}</div>
      <div style="font-size:0.85rem; color:#90cdf4; margin-top:5px;">
        Z-Score of <strong>{top_outlier['Z-Score']:.2f}</strong>. This city is not just leading; 
        it is performing <strong>{top_outlier['Z-Score']:.1f}x</strong> more standard deviations than the average city.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── TRENDS (Brief) ───────────────────────────────────────────────────────────
st.header("📈 Sales Trend")
monthly_sales = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M').astype(str))['Sales'].sum().reset_index()
fig_line = px.line(monthly_sales, x='Order Date', y='Sales', template="plotly_dark")
fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig_line.update_traces(line_color='#4299e1')
st.plotly_chart(fig_line, use_container_width=True)
