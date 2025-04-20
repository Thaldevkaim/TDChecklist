import streamlit as st
import requests

st.set_page_config(page_title="TD Checklist Dashboard")

st.title("TD Checklist Dashboard")
st.subheader("Stock Screening and Analysis Tool")
st.caption("Enter a stock ticker below (e.g., ASIANPAINT.NS or RELIANCE.BO)")

ticker = st.text_input("📈 Enter Stock Ticker")

if st.button("🔍 Analyze"):
    url = f"https://td-api-9qrg.onrender.com/score?ticker={ticker}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if "error" in data:
            st.error(f"❌ API Error: {data['error']}")
        else:
            st.success(f"TD Score: {data['TD Score']} / 80 ({data['Score %']}%)")
            st.metric("Sharpe Ratio (5Y)", data['Sharpe (5Y)'])

            if data['Forensic Red Flag']:
                st.warning("⚠️ Forensic Red Flag: OCF < Net Profit")
            else:
                st.success("✅ No Forensic Accounting Issues Detected")

            st.subheader("🧠 Score Breakdown")
            for category, pts in data['Breakdown'].items():
                st.write(f"• **{category}**: {pts}/10")
    else:
        st.error("❌ Unable to fetch score. Please check the ticker or try again.") 