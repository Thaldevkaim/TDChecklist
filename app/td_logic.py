import yfinance as yf
import numpy as np
from typing import Dict, Any

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

def score_ticker(ticker: str) -> Dict[str, Any]:
    """Calculate comprehensive TD score for a given stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Calculate metrics
        sharpe = calculate_sharpe_ratio(ticker)
        forensic_flag = check_forensic_flag(ticker)

        # Score breakdown (replace with actual calculations)
        breakdown = {
            "Growth": 8,
            "Profitability": 7,
            "Financial Health": 9,
            "Valuation": 6,
            "Management Quality": 8,
            "Market Position": 7,
            "Risk Factors": 8,
            "Future Outlook": 7
        }

        # Calculate total score
        total_score = sum(breakdown.values())
        score_percentage = round((total_score / 80) * 100, 1)

        return {
            "TD Score": total_score,
            "Score %": score_percentage,
            "Sharpe (10Y)": sharpe,
            "Forensic Red Flag": forensic_flag,
            "Breakdown": breakdown
        }

    except Exception as e:
        raise Exception(f"Error analyzing {ticker}: {str(e)}") 