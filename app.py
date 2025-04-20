import streamlit as st
import pandas as pd
import plotly.express as px
from td_screener import fetch_data, td_checklist, get_all_indian_stocks
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
This tool evaluates Indian stocks (BSE & NSE) based on principles from legendary investors:
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

if analysis_type == "Single Stock":
    # Single stock analysis
    col1, col2 = st.columns(2)
    with col1:
        exchange = st.selectbox("Select Exchange", ["BSE", "NSE"])
    with col2:
        ticker_input = st.text_input("Enter Stock Symbol (e.g., RELIANCE):")
    
    if ticker_input:
        ticker = f"{ticker_input}.{'BO' if exchange == 'BSE' else 'NS'}"
        
        if st.button("Analyze Stock"):
            with st.spinner("Analyzing stock..."):
                hist, info, error = fetch_data(ticker)
                
                if error:
                    st.error(f"Error analyzing {ticker}: {error}")
                else:
                    report = td_checklist(info, hist)
                    if report:
                        # Create tabs for different sections
                        tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Analysis", "Historical Data"])
                        
                        with tab1:
                            # Display basic info
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("TD Score", f"{report['Score %']}%")
                            with col2:
                                st.metric("Sector", report['Sector'])
                            with col3:
                                st.metric("Market Cap", f"₹{report['Market Cap']/1e9:.1f}B" if report['Market Cap'] else "N/A")
                            with col4:
                                st.metric("Current Price", f"₹{report['Current Price']:.1f}" if report['Current Price'] else "N/A")
                            
                            # Plot score breakdown
                            st.plotly_chart(plot_score_breakdown(report['Breakdown']), use_container_width=True)
                        
                        with tab2:
                            # Display breakdown
                            st.subheader("Score Breakdown")
                            breakdown_df = pd.DataFrame(list(report['Breakdown'].items()), columns=['Category', 'Score'])
                            breakdown_df['Score'] = breakdown_df['Score'].astype(str) + '/10'
                            st.table(breakdown_df)
                            
                            # Display additional metrics
                            st.subheader("Additional Metrics")
                            metrics_df = pd.DataFrame({
                                'Metric': ['Market Cap', 'Current Price', 'ROE', 'Debt/Equity', 'Sharpe Ratio'],
                                'Value': [
                                    f"₹{report['Market Cap']/1e9:.1f}B" if report['Market Cap'] else "N/A",
                                    f"₹{report['Current Price']:.1f}" if report['Current Price'] else "N/A",
                                    f"{report['ROE']*100:.1f}%" if report['ROE'] else "N/A",
                                    f"{report['Debt/Equity']:.2f}" if report['Debt/Equity'] else "N/A",
                                    f"{report['Sharpe (10Y)']:.2f}"
                                ]
                            })
                            st.table(metrics_df)
                            
                            # Warning for forensic red flags
                            if report['OCF < Net Profit (Forensic Red Flag)']:
                                st.warning("⚠️ Forensic Red Flag: Operating Cash Flow is less than Net Profit")
                        
                        with tab3:
                            # Display historical data
                            st.subheader("Historical Price Data")
                            st.line_chart(hist['Close'])
                            
                            # Display returns statistics
                            returns = hist['Close'].pct_change()
                            stats_df = pd.DataFrame({
                                'Metric': ['Annual Return', 'Annual Volatility', 'Sharpe Ratio'],
                                'Value': [
                                    f"{returns.mean() * 252 * 100:.1f}%",
                                    f"{returns.std() * (252 ** 0.5) * 100:.1f}%",
                                    f"{report['Sharpe (10Y)']:.2f}"
                                ]
                            })
                            st.table(stats_df)
                    else:
                        st.error("Could not generate report for this stock")

else:
    # Multiple stocks analysis
    col1, col2, col3 = st.columns(3)
    with col1:
        min_score = st.slider("Minimum TD Score %", 0, 100, 50)
    with col2:
        min_mcap = st.number_input("Minimum Market Cap (₹ Cr)", 0, 1000000, 0)
    with col3:
        sectors = ["All", "Technology", "Financial Services", "Consumer Defensive", "Healthcare", 
                  "Industrials", "Basic Materials", "Consumer Cyclical", "Energy", "Utilities"]
        selected_sector = st.selectbox("Select Sector", sectors)
    
    if st.button("Analyze Stocks"):
        stocks = get_all_indian_stocks()
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(stocks):
            status_text.text(f"Analyzing {ticker}... ({i+1}/{len(stocks)})")
            hist, info, error = fetch_data(ticker)
            
            if not error:
                report = td_checklist(info, hist)
                if report:
                    # Apply filters
                    meets_criteria = (
                        report['Score %'] >= min_score and
                        (report['Market Cap'] / 1e7 >= min_mcap if report['Market Cap'] else False) and
                        (selected_sector == "All" or report['Sector'] == selected_sector)
                    )
                    if meets_criteria:
                        results.append(report)
            
            progress_bar.progress((i + 1) / len(stocks))
        
        if results:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Format columns
            display_df = df.copy()
            display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"₹{x/1e9:.1f}B" if x else "N/A")
            display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"₹{x:.1f}" if x else "N/A")
            display_df['ROE'] = display_df['ROE'].apply(lambda x: f"{x*100:.1f}%" if x else "N/A")
            display_df['Debt/Equity'] = display_df['Debt/Equity'].apply(lambda x: f"{x:.2f}" if x else "N/A")
            
            # Display results
            st.subheader(f"Stocks Meeting Criteria (Total: {len(results)})")
            st.dataframe(display_df.sort_values('Score %', ascending=False))
            
            # Download link
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)
            
            # Analytics
            st.subheader("Analytics")
            col1, col2 = st.columns(2)
            
            with col1:
                # Sector distribution
                sector_dist = df['Sector'].value_counts()
                fig_sector = px.pie(values=sector_dist.values, names=sector_dist.index, 
                                  title='Sector Distribution')
                st.plotly_chart(fig_sector)
            
            with col2:
                # Score distribution
                fig_score = px.histogram(df, x='Score %', nbins=20,
                                       title='Score Distribution')
                st.plotly_chart(fig_score)
        else:
            st.warning("No stocks found matching the criteria") 