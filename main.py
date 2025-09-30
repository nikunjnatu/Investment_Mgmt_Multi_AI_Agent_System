

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import requests
import threading
import time
import os

from agents.finra_advisor_agent import FinraAdvisorAgent
from agents.technical_analyst_agent import TechnicalAnalystAgent

DATABASE = 'portfolio.db'
REFRESH_INTERVAL = 5  # seconds

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Automated Market Trends and Trade Recommendations ---
class TrendsRequest(BaseModel):
    news: str
    analyst_recs: str
    technicals: str

class TrendsAndRecommendationsResponse(BaseModel):
    trends: str
    recommendations: str

@app.post('/advisor/auto_recommendations', response_model=TrendsAndRecommendationsResponse)
def get_auto_trade_recommendations(req: TrendsRequest):
    # 1. Extract market trends using technical analyst agent
    analyst = TechnicalAnalystAgent()
    trends = analyst.extract_market_trends(req.news, req.analyst_recs, req.technicals)
    # 2. Get current portfolio
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT ticker, quantity, avg_cost FROM portfolio')
    portfolio = [
        {"ticker": row[0], "quantity": row[1], "avg_cost": row[2]}
        for row in c.fetchall()
    ]
    conn.close()
    # 3. Get trade recommendations from FINRA advisor agent
    advisor = FinraAdvisorAgent()
    recommendations = advisor.get_recommendations(portfolio, trends)
    return {"trends": trends, "recommendations": recommendations}

# ...existing code...

# --- LLM-based Trade Recommendations ---
class MarketTrendsRequest(BaseModel):
    market_trends: str

@app.post('/advisor/recommendations')
def get_trade_recommendations(req: MarketTrendsRequest):
    # Get current portfolio
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT ticker, quantity, avg_cost FROM portfolio')
    portfolio = [
        {"ticker": row[0], "quantity": row[1], "avg_cost": row[2]}
        for row in c.fetchall()
    ]
    conn.close()
    # Use LLM agent
    agent = FinraAdvisorAgent()
    recommendations = agent.get_recommendations(portfolio, req.market_trends)


# --- Models ---
class PortfolioItem(BaseModel):
    ticker: str
    quantity: float
    avg_cost: float

class PortfolioItemWithPrice(PortfolioItem):
    price: float
    total_value: float

class Portfolio(BaseModel):
    items: List[PortfolioItem]

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_cost REAL NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

# --- Portfolio CRUD ---
@app.post('/portfolio', response_model=Portfolio)
def set_portfolio(portfolio: Portfolio):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM portfolio')
    for item in portfolio.items:
        c.execute('INSERT INTO portfolio (ticker, quantity, avg_cost) VALUES (?, ?, ?)',
                  (item.ticker.upper(), item.quantity, item.avg_cost))
    conn.commit()
    conn.close()
    return portfolio

@app.get('/portfolio', response_model=Portfolio)
def get_portfolio():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT ticker, quantity, avg_cost FROM portfolio')
    items = [PortfolioItem(ticker=row[0], quantity=row[1], avg_cost=row[2]) for row in c.fetchall()]
    conn.close()
    return Portfolio(items=items)

# --- Real-time Price Fetching ---
# Use Alpha Vantage API for real-time stock prices
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'O6DK31EBS5XZIN34')  # Replace 'demo' with your real key
def fetch_price(ticker):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    try:
        resp = requests.get(url)
        data = resp.json()
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            price = float(data['Global Quote']['05. price'])
            print(f"Fetched price for {ticker}: {price}")
            return price
        else:
            print(f"Alpha Vantage response for {ticker}: {data}")
            return 0.0
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0

@app.get('/portfolio/prices', response_model=List[PortfolioItemWithPrice])
def get_portfolio_with_prices():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT ticker, quantity, avg_cost FROM portfolio')
    items = []
    for row in c.fetchall():
        ticker, quantity, avg_cost = row
        price = fetch_price(ticker)
        total_value = price * quantity
        items.append(PortfolioItemWithPrice(
            ticker=ticker,
            quantity=quantity,
            avg_cost=avg_cost,
            price=price,
            total_value=total_value
        ))
    conn.close()
    return items
