import streamlit as st
import pandas as pd
from td_screener import fetch_data, td_checklist, get_nse_stocks

# Set page config
st.set_page_config(
    page_title="TD Investment Screener",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 TD Investment Screener")
st.markdown("""
This tool evaluates stocks based on principles from legendary investors:
- Charlie Munger
- Benjamin Graham
- Aswath Damodaran
- Mohnish Pabrai
- Jim Simons
- Saurabh Mukherjea
""")

# Sidebar
st.sidebar.header("Settings")
analysis_type = st.sidebar.radio(
    "Choose Analysis Type",
    ["Single Stock", "Multiple Stocks"]
)

if analysis_type == "Single Stock":
    # Single stock analysis
    ticker = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
    
    if st.button("Analyze Stock"):
        with st.spinner("Analyzing stock..."):
            hist, info, error = fetch_data(ticker)
            
            if error:
                st.error(f"Error analyzing {ticker}: {error}")
            else:
                report = td_checklist(info, hist)
                if report:
                    # Display basic info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("TD Score", f"{report['Score %']}%")
                    with col2:
                        st.metric("Sector", report['Sector'])
                    with col3:
                        st.metric("Sharpe Ratio", f"{report['Sharpe (10Y)']:.2f}")
                    
                    # Display breakdown
                    st.subheader("Score Breakdown")
                    breakdown_df = pd.DataFrame(list(report['Breakdown'].items()), columns=['Category', 'Score'])
                    breakdown_df['Score'] = breakdown_df['Score'].astype(str) + '/10'
                    st.table(breakdown_df)
                    
                    # Display additional metrics
                    st.subheader("Additional Metrics")
                    metrics_df = pd.DataFrame({
                        'Metric': ['Market Cap', 'Current Price', 'ROE', 'Debt/Equity'],
                        'Value': [
                            f"₹{report['Market Cap']/1e9:.1f}B" if report['Market Cap'] else "N/A",
                            f"₹{report['Current Price']:.1f}" if report['Current Price'] else "N/A",
                            f"{report['ROE']*100:.1f}%" if report['ROE'] else "N/A",
                            f"{report['Debt/Equity']:.2f}" if report['Debt/Equity'] else "N/A"
                        ]
                    })
                    st.table(metrics_df)
                    
                    # Warning for forensic red flags
                    if report['OCF < Net Profit (Forensic Red Flag)']:
                        st.warning("⚠️ Forensic Red Flag: Operating Cash Flow is less than Net Profit")
                else:
                    st.error("Could not generate report for this stock")

else:
    # Multiple stocks analysis
    min_score = st.sidebar.slider("Minimum TD Score %", 0, 100, 50)
    
    if st.button("Analyze All Stocks"):
        stocks = get_nse_stocks()
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(stocks):
            status_text.text(f"Analyzing {ticker}... ({i+1}/{len(stocks)})")
            hist, info, error = fetch_data(ticker)
            
            if not error:
                report = td_checklist(info, hist)
                if report and report['Score %'] >= min_score:
                    results.append(report)
            
            progress_bar.progress((i + 1) / len(stocks))
        
        if results:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            df['Market Cap'] = df['Market Cap'].apply(lambda x: f"₹{x/1e9:.1f}B" if x else "N/A")
            df['Current Price'] = df['Current Price'].apply(lambda x: f"₹{x:.1f}" if x else "N/A")
            df['ROE'] = df['ROE'].apply(lambda x: f"{x*100:.1f}%" if x else "N/A")
            df['Debt/Equity'] = df['Debt/Equity'].apply(lambda x: f"{x:.2f}" if x else "N/A")
            
            # Display results
            st.subheader(f"Stocks with TD Score ≥ {min_score}%")
            st.dataframe(df.sort_values('Score %', ascending=False))
        else:
            st.warning("No stocks found matching the criteria") 