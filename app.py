import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_train.csv')
    # สร้าง Mapping ชื่อรัฐเป็นตัวย่อเพื่อใช้กับแผนที่
    state_map = {
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
    df['State Code'] = df['State'].map(state_map)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

# 3. ส่วนของ Sidebar (Filter)
st.sidebar.header("🧭 ตัวกรองข้อมูล")
region = st.sidebar.multiselect("เลือกภูมิภาค", options=df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("เลือกหมวดหมู่", options=df["Category"].unique(), default=df["Category"].unique())

# กรองข้อมูลตามที่เลือก
df_selection = df[df["Region"].isin(region) & df["Category"].isin(category)]

# 4. ส่วนหัวของ Dashboard และ KPI
st.title("🗺️ ระบบวิเคราะห์ยอดขายเชิงภูมิภาค")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("ยอดขายรวม", f"${df_selection['Sales'].sum():,.0f}")
with c2:
    st.metric("จำนวนคำสั่งซื้อ", f"{df_selection['Order ID'].nunique():,}")
with c3:
    st.metric("ค่าเฉลี่ยต่อบิล", f"${df_selection['Sales'].mean():,.2f}")

st.markdown("---")

# 5. แผนที่ (US Map)
st.subheader("📍 แผนที่แสดงความหนาแน่นของยอดขาย")
state_sales = df_selection.groupby(['State', 'State Code'])['Sales'].sum().reset_index()

fig_map = px.choropleth(
    state_sales,
    locations='State Code',
    locationmode="USA-states",
    color='Sales',
    scope="usa",
    hover_name='State',
    color_continuous_scale="Viridis",
    labels={'Sales': 'ยอดขาย ($)'}
)
st.plotly_chart(fig_map, use_container_width=True)

# 6. ส่วนวิเคราะห์ Insight
st.header("💡 ข้อมูลเชิงลึก (Key Insights)")
col_left, col_right = st.columns(2)

with col_left:
    # อันดับรัฐที่ทำเงินสูงสุด
    top_state = state_sales.sort_values(by='Sales', ascending=False).head(5)
    st.subheader("🏆 5 อันดับรัฐยอดขายสูงสุด")
    st.table(top_state[['State', 'Sales']])

with col_right:
    # สัดส่วนหมวดหมู่สินค้า
    cat_sales = df_selection.groupby('Category')['Sales'].sum().reset_index()
    fig_pie = px.pie(cat_sales, values='Sales', names='Category', hole=0.4, title="สัดส่วนรายได้ตามหมวดหมู่")
    st.plotly_chart(fig_pie, use_container_width=True)

# สรุป Insight เป็นข้อความ
best_state = top_state.iloc[0]['State']
best_cat = cat_sales.sort_values(by='Sales', ascending=False).iloc[0]['Category']

st.info(f"**สรุปผล:** ปัจจุบันรัฐ **{best_state}** เป็นตลาดที่ใหญ่ที่สุดของคุณ และสินค้ากลุ่ม **{best_cat}** เป็นสินค้าที่ทำกำไรได้ดีที่สุดในพื้นที่ที่เลือก")
