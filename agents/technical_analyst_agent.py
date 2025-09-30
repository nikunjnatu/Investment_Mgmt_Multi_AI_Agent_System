
from transformers import pipeline

class TechnicalAnalystAgent:
    def __init__(self):
        # Uses a free Hugging Face model (local or will download on first use)
        self.llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    def extract_market_trends(self, news: str, analyst_recs: str, technicals: str) -> str:
        prompt = f"""
You are a US stock market technical analyst and researcher. Given the latest news, analyst recommendations, and technical analysis, extract and summarize the most important current US market trends. Be concise and actionable. Example output: 'S&P 500 uptrend, tech stocks volatile, energy sector strong, Fed rate hike expected.'

Latest News:
{news}

Analyst Recommendations:
{analyst_recs}

Technical Analysis:
{technicals}
"""
        result = self.llm(prompt, max_new_tokens=200)
        return result[0]['generated_text']