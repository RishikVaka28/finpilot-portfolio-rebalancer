from decimal import Decimal

from pydantic import BaseModel


class RebalanceRecommendation(BaseModel):
    symbol: str
    current_value: Decimal
    current_percent: Decimal
    target_percent: Decimal
    target_value: Decimal
    difference_value: Decimal
    action: str


class RebalanceResponse(BaseModel):
    portfolio_id: int
    total_value: Decimal
    recommendations: list[RebalanceRecommendation]

