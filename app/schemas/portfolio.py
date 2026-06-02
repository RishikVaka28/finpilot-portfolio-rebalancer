from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class PortfolioUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class PortfolioRead(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PortfolioAllocation(BaseModel):
    symbol: str
    market_value: Decimal
    current_percent: Decimal


class PortfolioSummary(BaseModel):
    portfolio_id: int
    portfolio_name: str
    total_value: Decimal
    holdings_count: int
    allocations: list[PortfolioAllocation]
