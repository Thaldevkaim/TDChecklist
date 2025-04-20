import streamlit as st
import yfinance as yf
import requests
import ssl
import json
from bs4 import BeautifulSoup
import urllib3
import os
import time
import plotly.express as px
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="TD Investment Screener",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 TD Investment Screener")
st.markdown("""
This tool screens Indian stocks based on principles from legendary investors:
- Charlie Munger (Business Quality)
- Benjamin Graham (Value)
- Aswath Damodaran (Valuation)
- Mohnish Pabrai (Risk)
- Jim Simons (Quant)
- Saurabh Mukherjea (Quality)
""")

# Import the screening logic
from td_screener import get_all_indian_stocks, fetch_data, td_checklist

def main():
    # Sidebar controls
    st.sidebar.header("Screening Parameters")
    min_score = st.sidebar.slider("Minimum TD Score (%)", 0, 100, 90, 5)
    
    if st.sidebar.button("Start Screening"):
        with st.spinner("Fetching stock list..."):
            stocks = get_all_indian_stocks()
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()
        
        results = []
        total_stocks = len(stocks)
        
        for i, ticker in enumerate(stocks):
            # Update progress
            progress = int((i + 1) / total_stocks * 100)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing {ticker}... ({i+1}/{total_stocks})")
            
            # Analyze stock
            hist, info, error = fetch_data(ticker)
            if error:
                continue
                
            report = td_checklist(info, hist)
            if report and report['Score %'] >= min_score:
                results.append(report)
            
            # Display current results
            if results:
                # Create a simple table display
                table_data = []
                for r in results:
                    table_data.append({
                        "Ticker": r['Ticker'],
                        "Name": r['Stock Name'],
                        "Sector": r['Sector'],
                        "Score": f"{r['Score %']:.1f}%",
                        "ROE": f"{r['ROE']*100:.1f}%" if r['ROE'] else "N/A",
                        "D/E": f"{r['Debt/Equity']:.2f}" if r['Debt/Equity'] else "N/A",
                        "Sharpe": f"{r['Sharpe (10Y)']:.2f}"
                    })
                st.table(table_data)
            
            time.sleep(0.5)  # Prevent rate limiting
        
        # Final results
        status_text.text("Screening completed!")
        st.success(f"Found {len(results)} stocks matching your criteria!")
        
        if results:
            # Detailed results
            st.header("Detailed Analysis")
            for result in results:
                with st.expander(f"{result['Stock Name']} ({result['Ticker']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Basic Information")
                        st.write(f"Sector: {result['Sector']}")
                        st.write(f"Market Cap: ₹{result['Market Cap']/1e9:.1f}B")
                        st.write(f"Current Price: ₹{result['Current Price']:.2f}")
                    
                    with col2:
                        st.subheader("Score Breakdown")
                        for category, score in result['Breakdown'].items():
                            st.write(f"{category}: {score}")
                    
                    st.subheader("Key Metrics")
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    
                    with metrics_col1:
                        st.metric("TD Score", f"{result['Score %']:.1f}%")
                    with metrics_col2:
                        st.metric("ROE", f"{result['ROE']*100:.1f}%" if result['ROE'] else "N/A")
                    with metrics_col3:
                        st.metric("Debt/Equity", f"{result['Debt/Equity']:.2f}" if result['Debt/Equity'] else "N/A")
                    with metrics_col4:
                        st.metric("Sharpe Ratio", f"{result['Sharpe (10Y)']:.2f}")

def plot_score_breakdown(breakdown):
    df = pd.DataFrame(list(breakdown.items()), columns=['Category', 'Score'])
    fig = px.bar(df, x='Category', y='Score',
                 title='Score Breakdown',
                 labels={'Score': 'Points (out of 10)'},
                 color='Score',
                 color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename="td_screener_results.xlsx"):
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Excel file</a>'

if __name__ == "__main__":
    main() 