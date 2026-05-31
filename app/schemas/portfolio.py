from datetime import datetime

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

