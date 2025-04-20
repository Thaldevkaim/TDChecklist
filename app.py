import streamlit as st
import pandas as pd
import plotly.express as px
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
min_score = st.sidebar.slider("Minimum TD Score %", 0, 100, 50)
selected_sectors = st.sidebar.multiselect(
    "Filter by Sectors",
    ["All", "Technology", "Healthcare", "Financial Services", "Consumer Defensive", "Consumer Cyclical", 
     "Industrials", "Basic Materials", "Energy", "Utilities", "Communication Services"],
    default=["All"]
)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Stock Analysis")
    if st.button("Analyze Stocks"):
        stocks = get_nse_stocks()
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(stocks):
            status_text.text(f"Analyzing {ticker}...")
            hist, info, error = fetch_data(ticker)
            
            if error:
                st.warning(f"Error analyzing {ticker}: {error}")
                continue
                
            report = td_checklist(info, hist)
            if report:
                results.append(report)
            
            # Update progress
            progress_bar.progress((i + 1) / len(stocks))
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if results:
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Filter by score and sector
            df = df[df['Score %'] >= min_score]
            if "All" not in selected_sectors:
                df = df[df['Sector'].isin(selected_sectors)]
            
            # Sort by TD Score
            df = df.sort_values('TD Score', ascending=False)
            
            # Display results
            st.dataframe(
                df[[
                    'Ticker', 'Stock Name', 'Sector', 'TD Score', 'Score %',
                    'Market Cap', 'Current Price', 'Sharpe (10Y)'
                ]],
                hide_index=True
            )
            
            # Save to session state for visualization
            st.session_state['results'] = df

with col2:
    st.subheader("Visualizations")
    if 'results' in st.session_state:
        df = st.session_state['results']
        
        # Sector Distribution
        fig1 = px.pie(df, names='Sector', title='Sector Distribution')
        st.plotly_chart(fig1)
        
        # Score Distribution
        fig2 = px.histogram(df, x='Score %', title='Score Distribution')
        st.plotly_chart(fig2)
        
        # Top 10 Stocks by Score
        fig3 = px.bar(
            df.head(10),
            x='Ticker',
            y='Score %',
            title='Top 10 Stocks by TD Score'
        )
        st.plotly_chart(fig3)

# Footer
st.markdown("---")
st.markdown("*Disclaimer: This tool is for educational purposes only. Always do your own research before making investment decisions.*") 