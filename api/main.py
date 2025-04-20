from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.td_logic import score_ticker

app = FastAPI()

# Enable CORS so the Streamlit app can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to TD Checklist API"}

@app.get("/score")
def score(ticker: str):
    """
    Calculate TD Score for a given stock ticker.
    Returns comprehensive analysis including:
    - Total TD Score (out of 80)
    - Score percentage
    - 10-year Sharpe ratio
    - Forensic red flags
    - Detailed breakdown by category
    """
    try:
        result = score_ticker(ticker)
        return result
    except Exception as e:
        return {"error": str(e)} 