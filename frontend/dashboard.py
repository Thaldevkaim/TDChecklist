import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="TD Checklist",
    page_icon="📊",
    layout="wide"
)

st.title("TD Checklist Dashboard")
st.markdown("### Stock Screening and Analysis Tool")

def main():
    # Add sidebar for filters
    st.sidebar.title("Filters")
    
    # Main content area
    st.write("Welcome to TD Checklist! Select options from the sidebar to begin analysis.")
    
    # Placeholder for future functionality
    st.info("More features coming soon!")

if __name__ == "__main__":
    main() 