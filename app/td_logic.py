import yfinance as yf
import numpy as np
from typing import Dict, Any
import time

def calculate_sharpe_ratio(ticker: str) -> float:
    """Calculate 10-year Sharpe ratio for a given stock"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="10y")
        returns = hist['Close'].pct_change().dropna()
        sharpe = np.sqrt(252) * (returns.mean() / returns.std())
        return round(sharpe, 2)
    except:
        return 0.0

def check_forensic_flag(ticker: str) -> bool:
    """Check if operating cash flow is less than net income"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        ocf = info.get('operatingCashflow', 0)
        net_income = info.get('netIncomeToCommon', 0)
        return ocf < net_income
    except:
        return False

def score_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Get 5y data
        hist = stock.history(period="5y")
        if hist.empty:
            # Retry once if first attempt fails
            time.sleep(2)
            hist = stock.history(period="5y")

        if hist.empty:
            raise ValueError("No historical data found.")

        info = stock.info

        if not info or "shortName" not in info:
            raise ValueError("Failed to load financial info.")

        score = 0
        breakdown = {}

        # 1. Business Quality & Moat
        moat = 0
        if info.get('longBusinessSummary'): moat += 6
        if info.get('sector') not in ['Financial Services', 'Cyclicals']: moat += 4
        breakdown['Business Quality & Moat'] = moat
        score += moat

        # 2. Management Quality
        mgmt = 0
        if info.get('heldPercentInsiders', 0) > 0.1: mgmt += 5
        if info.get('returnOnEquity', 0) > 0.15: mgmt += 5
        breakdown['Management Quality'] = mgmt
        score += mgmt

        # 3. Financial Strength
        fin = 0
        if info.get('debtToEquity', 100) < 1: fin += 5
        if info.get('freeCashflow', 0) > 0: fin += 5
        breakdown['Financial Strength'] = fin
        score += fin

        # 4. Forensic Accounting
        forensic = 0
        ocf_net = info.get('operatingCashflow', 1) / max(info.get('netIncome', 1), 1)
        if ocf_net > 1: forensic += 6
        if info.get('totalCash', 0) > info.get('totalDebt', 0): forensic += 4
        breakdown['Forensic Accounting'] = forensic
        score += forensic

        # 5. Valuation
        val = 0
        if info.get('trailingPE', 50) < 30: val += 5
        if info.get('priceToBook', 10) < 5: val += 5
        breakdown['Valuation'] = val
        score += val

        # 6. Risk Profile
        risk = 0
        if info.get('beta', 1.2) < 1.2: risk += 5
        if info.get('trailingEps', 0) > 0: risk += 5
        breakdown['Risk Profile'] = risk
        score += risk

        # 7. Conviction
        conviction = 5
        breakdown['Conviction'] = conviction
        score += conviction

        # 8. Quant Edge
        returns = hist['Close'].pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5)
        quant = 4 if sharpe > 1 else 0
        breakdown['Quant Edge'] = quant
        score += quant

        return {
            "TD Score": score,
            "Score %": round(score / 80 * 100, 2),
            "Sharpe (5Y)": round(sharpe, 2),
            "Breakdown": breakdown,
            "Forensic Red Flag": ocf_net < 1
        }

    except Exception as e:
        return {"error": f"Error analyzing {ticker}: {str(e)}"} 