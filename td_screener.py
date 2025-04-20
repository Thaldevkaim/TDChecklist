# TD Investment Screener v1.0 – Automated with Yahoo Finance
# Evaluates stocks based on Munger, Graham, Damodaran, Pabrai, Simons & Mukherjea principles

import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import requests
import ssl
import json
from bs4 import BeautifulSoup

def get_all_indian_stocks():
    """Return a list of all BSE and NSE stocks"""
    try:
        # BSE stocks (with .BO suffix)
        bse_url = "https://www.bseindia.com/corporates/List_Scrips.aspx"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        stocks = []
        
        # Default list of major stocks (as backup)
        default_stocks = [
            # Large Cap BSE
            "RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "INFY.BO", "ICICIBANK.BO",
            "HINDUNILVR.BO", "BHARTIARTL.BO", "ITC.BO", "KOTAKBANK.BO", "LT.BO",
            
            # Mid Cap BSE
            "NAUKRI.BO", "MPHASIS.BO", "TATACOMM.BO", "PERSISTENT.BO", "LTIM.BO",
            "TRENT.BO", "ABBOTINDIA.BO", "SUPREMEIND.BO", "ASTRAL.BO",
            
            # NSE stocks
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
            
            # Additional Popular Stocks
            "TATAMOTORS.BO", "ZEEL.BO", "PNB.BO", "TVSMOTOR.BO", "M&M.BO",
            "BAJFINANCE.BO", "DMART.BO", "PIDILITIND.BO", "TITAN.BO", "ASIANPAINT.BO"
        ]
        
        try:
            # Try to fetch BSE equity list
            bse_response = requests.get("https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w", headers=headers)
            if bse_response.status_code == 200:
                bse_data = bse_response.json()
                for scrip in bse_data:
                    if scrip['Status'] == 'Active':
                        stocks.append(f"{scrip['SCRIP_CD']}.BO")
            
            # Try to fetch NSE equity list
            nse_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
            nse_response = requests.get(nse_url, headers=headers)
            if nse_response.status_code == 200:
                nse_data = nse_response.json()
                for stock in nse_data['data']:
                    stocks.append(f"{stock['symbol']}.NS")
                    
        except Exception as e:
            print(f"Error fetching stock lists: {e}")
            print("Using default stock list...")
            return default_stocks
            
        if not stocks:
            return default_stocks
            
        return list(set(stocks))  # Remove duplicates
        
    except Exception as e:
        print(f"Error in get_all_indian_stocks: {e}")
        return default_stocks

def fetch_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="10y")
        info = stock.info
        if hist.empty or not info:
            return None, None, f"No data available for {ticker}"
        return hist, info, None
    except Exception as e:
        return None, None, str(e)

def td_checklist(info, hist):
    if hist is None or info is None:
        return None
        
    score = 0
    max_score = 80
    breakdown = {}

    # 1. Business Quality & Moat (10 pts)
    moat_score = 0
    if info.get('longBusinessSummary'): moat_score += 6
    if info.get('sector') not in ['Financial Services', 'Cyclicals']: moat_score += 4
    score += moat_score
    breakdown['Business Quality & Moat'] = moat_score

    # 2. Management Quality (10 pts)
    mgmt_score = 0
    if info.get('heldPercentInsiders', 0) > 0.1: mgmt_score += 5
    if info.get('returnOnEquity', 0) > 0.15: mgmt_score += 5
    score += mgmt_score
    breakdown['Management Quality'] = mgmt_score

    # 3. Financial Strength (10 pts)
    fin_score = 0
    if info.get('debtToEquity', 100) < 1: fin_score += 5
    if info.get('freeCashflow', 0) > 0: fin_score += 5
    score += fin_score
    breakdown['Financial Strength'] = fin_score

    # 4. Forensic Accounting (10 pts)
    forensic_score = 0
    ocf_net_ratio = info.get('operatingCashflow', 1) / max(info.get('netIncome', 1), 1)
    if ocf_net_ratio > 1: forensic_score += 6
    if info.get('totalCash', 0) > info.get('totalDebt', 0): forensic_score += 4
    score += forensic_score
    breakdown['Forensic Accounting'] = forensic_score

    # 5. Valuation (10 pts)
    val_score = 0
    if info.get('trailingPE', 50) < 30: val_score += 5
    if info.get('priceToBook', 10) < 5: val_score += 5
    score += val_score
    breakdown['Valuation'] = val_score

    # 6. Risk Profile (10 pts)
    risk_score = 0
    if info.get('beta', 1.2) < 1.2: risk_score += 5
    if info.get('trailingEps', 0) > 0: risk_score += 5
    score += risk_score
    breakdown['Risk Profile'] = risk_score

    # 7. Conviction & Psychology (10 pts)
    conviction_score = 5  # Manual override area
    score += conviction_score
    breakdown['Conviction & Temperament'] = conviction_score

    # 8. Quant Edge (10 pts)
    try:
        returns = hist['Close'].pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5)
        quant_score = 0
        if sharpe > 1: quant_score += 4
        score += quant_score
        breakdown['Quant Edge'] = quant_score
    except:
        sharpe = 0
        breakdown['Quant Edge'] = 0

    summary = {
        "Ticker": info.get("symbol", ""),
        "Stock Name": info.get("shortName", ""),
        "Sector": info.get("sector", ""),
        "Market Cap": info.get("marketCap", 0),
        "Current Price": info.get("currentPrice", 0),
        "TD Score": score,
        "Score %": round(score / max_score * 100, 2),
        "Breakdown": breakdown,
        "OCF < Net Profit (Forensic Red Flag)": ocf_net_ratio < 1,
        "Sharpe (10Y)": round(sharpe, 2),
        "ROE": info.get("returnOnEquity", 0),
        "Debt/Equity": info.get("debtToEquity", 0),
        "Exchange": "BSE" if ".BO" in info.get("symbol", "") else "NSE"
    }

    return summary

def analyze_stocks(min_score_percent=90):
    results = []
    stocks = get_all_indian_stocks()
    total_stocks = len(stocks)
    
    print(f"\n🔍 Analyzing {total_stocks} Indian Stocks...\n")
    print(f"Looking for stocks with TD Score >= {min_score_percent}%\n")
    
    for i, ticker in enumerate(stocks, 1):
        print(f"Progress: {i}/{total_stocks} - Analyzing {ticker}...")
        hist, info, error = fetch_data(ticker)
        
        if error:
            print(f"Error analyzing {ticker}: {error}")
            continue
            
        report = td_checklist(info, hist)
        if report and report['Score %'] >= min_score_percent:
            results.append(report)
            print(f"✨ High Score Found! {ticker}: {report['Score %']}%")
        elif report:
            print(f"Score: {report['Score %']}%")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    # Sort results by TD Score
    results.sort(key=lambda x: x['TD Score'], reverse=True)
    
    # Print results
    print(f"\n📊 Indian Stocks with TD Score >= {min_score_percent}%")
    print("=" * 140)
    print(f"{'Rank':<5} {'Ticker':<12} {'Stock Name':<30} {'Sector':<20} {'Market Cap':<15} {'Price':<10} {'TD Score':<10} {'Score %':<10} {'ROE %':<8} {'D/E':<8} {'Sharpe':<10}")
    print("-" * 140)
    
    for i, result in enumerate(results, 1):
        market_cap = f"₹{result['Market Cap']/1e9:.1f}B" if result['Market Cap'] else "N/A"
        price = f"₹{result['Current Price']:.1f}" if result['Current Price'] else "N/A"
        roe = f"{result['ROE']*100:.1f}" if result['ROE'] else "N/A"
        de = f"{result['Debt/Equity']:.1f}" if result['Debt/Equity'] else "N/A"
        
        print(f"{i:<5} {result['Ticker']:<12} {result['Stock Name'][:30]:<30} {result['Sector'][:20]:<20} "
              f"{market_cap:<15} {price:<10} {result['TD Score']:<10} {result['Score %']:<10.2f} "
              f"{roe:<8} {de:<8} {result['Sharpe (10Y)']:<10.2f}")
    
    return results

# Run the analysis
if __name__ == "__main__":
    analyze_stocks(min_score_percent=90) 