from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HoldingBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(ge=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.upper().strip()


class HoldingCreate(HoldingBase):
    pass


class HoldingUpdate(BaseModel):
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(ge=0)


class HoldingRead(HoldingBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)

