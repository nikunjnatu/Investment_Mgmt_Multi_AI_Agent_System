from pydantic import BaseModel
from typing import List

class PortfolioItem(BaseModel):
    ticker: str
    quantity: float
    avg_cost: float

class Portfolio(BaseModel):
    id: int
    items: List[PortfolioItem]
