# lotto_app.py
import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta
import plotly.express as px
from apscheduler.schedulers.background import BackgroundScheduler

# โหลดข้อมูลจาก data.go.th
@st.cache_data
def load_data():
    url = "https://data.go.th/dataset/7a01d7f6-173d-48e2-9f71-2f1c50d9a99a/resource/1e8e37aa-bcf3-4f81-9b42-78d1e7c1c0f2/download/lottery_result.csv"
    r = requests.get(url); r.encoding = 'utf-8'
    df = pd.read_csv(StringIO(r.text), parse_dates=['DRAW_DATE'])
    df['LAST2'] = df['PRIZE_1'].astype(str).str[-2:]
    return df

df = load_data()

# UI
st.title("📊 ระบบวิเคราะห์ข้อมูลสลากกินแบ่งรัฐบาล")
st.markdown("**ข้อมูลจาก data.go.th** — วิเคราะห์เลขท้าย 2 ตัว + แจ้งเตือน + พยากรณ์")

col1, col2 = st.columns(2)
with col1:
    start = st.date_input("📅 เริ่มวันที่", value=datetime.now().date()-timedelta(days=180))
with col2:
    end = st.date_input("📅 ถึงวันที่", value=datetime.now().date())

filtered = df[(df['DRAW_DATE'].dt.date >= start) & (df['DRAW_DATE'].dt.date <= end)]
freq = filtered['LAST2'].value_counts().reset_index()
freq.columns = ['Number', 'Count']

# Bar Chart
st.subheader("🔢 เลขท้าย 2 ตัวที่ออกบ่อย")
fig = px.bar(freq.head(20), x='Number', y='Count', title="Top 20 เลขท้าย 2 ตัว")
st.plotly_chart(fig, use_container_width=True)

# Never Output
all_nums = {f"{i:02}" for i in range(100)}
never = sorted(list(all_nums - set(freq['Number'])))
st.subheader("❌ เลขที่ไม่เคยออก")
st.write(", ".join(never))

# พยากรณ์จากความน่าจะเป็น
st.subheader("🔮 พยากรณ์เบื้องต้น")
prob = freq.copy()
prob['Prob'] = prob['Count'] / prob['Count'].sum()
st.dataframe(prob.sort_values('Prob', ascending=False).head(5))

st.caption("จัดทำโดย AI Assistant สำหรับนำเสนอ Demo เท่านั้น")
