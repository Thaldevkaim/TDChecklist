#!/usr/bin/env python3

import yfinance as yf
import requests
import ssl
import json
from bs4 import BeautifulSoup
import urllib3
import time
from td_screener import get_all_indian_stocks, fetch_data, td_checklist

def main():
    print("\n📊 TD Investment Screener")
    print("=" * 80)
    print("Screening Indian stocks based on principles from legendary investors:")
    print("- Charlie Munger (Business Quality)")
    print("- Benjamin Graham (Value)")
    print("- Aswath Damodaran (Valuation)")
    print("- Mohnish Pabrai (Risk)")
    print("- Jim Simons (Quant)")
    print("- Saurabh Mukherjea (Quality)")
    print("=" * 80)
    
    min_score = float(input("\nEnter minimum TD Score % (0-100): "))
    
    print("\n🔍 Fetching stock list...")
    stocks = get_all_indian_stocks()
    total_stocks = len(stocks)
    
    print(f"\nAnalyzing {total_stocks} stocks...")
    results = []
    
    for i, ticker in enumerate(stocks, 1):
        print(f"\rProgress: {i}/{total_stocks} - Analyzing {ticker}...", end="", flush=True)
        
        hist, info, error = fetch_data(ticker)
        if error:
            continue
            
        report = td_checklist(info, hist)
        if report and report['Score %'] >= min_score:
            results.append(report)
            print(f"\n✨ High Score Found! {ticker}: {report['Score %']}%")
        
        time.sleep(0.5)  # Prevent rate limiting
    
    # Sort results by TD Score
    results.sort(key=lambda x: x['Score %'], reverse=True)
    
    # Print results
    print(f"\n\n📊 Indian Stocks with TD Score >= {min_score}%")
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
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main() 