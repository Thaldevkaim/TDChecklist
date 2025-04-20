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
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Open `td_screener.py`
2. Modify the `ticker` variable with the stock symbol you want to analyze
3. Run the script:
```bash
python td_screener.py
```

The screener will output a detailed report including:
- Overall TD Score (out of 80)
- Score breakdown by category
- Key metrics and red flags
- 10-year Sharpe ratio

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

## Notes

- The screener uses Yahoo Finance API for data
- Some metrics may not be available for all stocks
- The Conviction & Psychology score is set to 5 by default and can be manually adjusted
- The screener is designed for educational purposes and should not be used as the sole basis for investment decisions 