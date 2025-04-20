# TD Investment Screener

A comprehensive stock screening tool that evaluates companies based on principles from legendary investors like Charlie Munger, Benjamin Graham, Aswath Damodaran, Mohnish Pabrai, Jim Simons, and Saurabh Mukherjea.

## Features

- Business Quality & Moat Analysis
- Management Quality Assessment
- Financial Strength Evaluation
- Forensic Accounting Checks
- Valuation Metrics
- Risk Profile Analysis
- Conviction & Psychology Factors
- Quantitative Edge Analysis

## Installation

1. Clone this repository
```bash
git clone https://github.com/Thaldevkaim/TDChecklist.git
cd TDChecklist
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)
Run the Streamlit app:
```bash
streamlit run app.py
```
This will open a web interface where you can:
- Analyze individual stocks
- Screen multiple stocks with custom criteria
- View detailed breakdowns and metrics
- Get real-time analysis results

### Command Line Interface
You can also run the script directly:
```bash
python td_screener.py
```

## Scoring System

The screener evaluates stocks across 8 categories, each worth 10 points:
1. Business Quality & Moat
2. Management Quality
3. Financial Strength
4. Forensic Accounting
5. Valuation
6. Risk Profile
7. Conviction & Psychology
8. Quant Edge

## Features

### Single Stock Analysis
- Detailed breakdown of scores across all categories
- Key financial metrics and ratios
- Forensic accounting red flags
- Risk metrics including Sharpe ratio

### Multiple Stocks Screening
- Analyze entire sets of stocks
- Filter by minimum TD Score
- Sort and compare across different metrics
- Export results for further analysis

## Notes

- The screener uses Yahoo Finance API for data
- Some metrics may not be available for all stocks
- The Conviction & Psychology score is set to 5 by default and can be manually adjusted
- The screener is designed for educational purposes and should not be used as the sole basis for investment decisions 