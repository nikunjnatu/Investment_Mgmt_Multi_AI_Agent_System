
from transformers import pipeline
from typing import List, Dict

class FinraAdvisorAgent:
    def __init__(self):
        # Uses a free Hugging Face model (local or will download on first use)
        self.llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    def get_recommendations(self, portfolio: List[Dict], market_trends: str) -> str:
        prompt = f"""
You are a FINRA certified financial advisor specializing in short-term, intraday trading strategies. Analyze the following US stock portfolio and current market trends. Recommend specific intraday trades (buy/sell/hold) for each security to maximize quick profit within the same trading day. For each recommendation, include a brief rationale based on technicals, news, or momentum. Format your response as:

Intraday Trade Recommendations:
- [Buy/Sell/Hold] [Ticker]: [Rationale for quick profit]

Analytics Table:
| Ticker | Suggested Action | Rationale |
|--------|------------------|-----------|
... (one row per security)

Portfolio:
{portfolio}

Market Trends:
{market_trends}
"""
        result = self.llm(prompt, max_new_tokens=600)
        return result[0]['generated_text']