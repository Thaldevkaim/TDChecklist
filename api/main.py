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
    try:
        result = score_ticker(ticker)
        return result
    except Exception as e:
        return {"error": str(e)} 