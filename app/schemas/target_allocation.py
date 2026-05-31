from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TargetAllocationBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    target_percent: Decimal = Field(ge=0, le=100)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.upper().strip()


class TargetAllocationCreate(TargetAllocationBase):
    pass


class TargetAllocationUpdate(BaseModel):
    target_percent: Decimal = Field(ge=0, le=100)


class TargetAllocationRead(TargetAllocationBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)

