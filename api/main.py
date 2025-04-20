from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np
from typing import Dict, Any

app = FastAPI(title="TD Checklist API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_sharpe_ratio(ticker: str) -> float:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="10y")
        returns = hist['Close'].pct_change().dropna()
        sharpe = np.sqrt(252) * (returns.mean() / returns.std())
        return round(sharpe, 2)
    except:
        return 0.0

def check_forensic_flag(ticker: str) -> bool:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        ocf = info.get('operatingCashflow', 0)
        net_income = info.get('netIncomeToCommon', 0)
        return ocf < net_income
    except:
        return False

@app.get("/")
async def root():
    return {"message": "Welcome to TD Checklist API"}

@app.get("/score")
async def get_stock_score(ticker: str) -> Dict[str, Any]:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Calculate metrics
        sharpe = calculate_sharpe_ratio(ticker)
        forensic_flag = check_forensic_flag(ticker)

        # Mock score breakdown (replace with actual calculations)
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
        raise HTTPException(status_code=400, detail=str(e)) 