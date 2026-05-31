from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status

from app.models.portfolio import Portfolio
from app.schemas.rebalance import RebalanceRecommendation, RebalanceResponse


TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _percent(value: Decimal) -> Decimal:
    return value.quantize(FOURPLACES, rounding=ROUND_HALF_UP)


def calculate_rebalance(portfolio: Portfolio) -> RebalanceResponse:
    """Compute buy/sell deltas needed to match target allocations.

    The engine includes symbols present only in targets so users can see which
    positions need to be opened, and symbols present only in holdings so users
    can see which assets should be reduced to zero.
    """
    holdings_by_symbol = {holding.symbol: holding for holding in portfolio.holdings}
    targets_by_symbol = {
        target.symbol: Decimal(target.target_percent)
        for target in portfolio.target_allocations
    }

    target_total = sum(targets_by_symbol.values(), Decimal("0"))
    if target_total != Decimal("100"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Target allocations must sum to 100 percent",
        )

    total_value = sum(
        Decimal(holding.quantity) * Decimal(holding.price)
        for holding in portfolio.holdings
    )
    if total_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Portfolio must have positive market value",
        )

    recommendations: list[RebalanceRecommendation] = []
    for symbol in sorted(set(holdings_by_symbol) | set(targets_by_symbol)):
        holding = holdings_by_symbol.get(symbol)
        current_value = (
            Decimal(holding.quantity) * Decimal(holding.price) if holding else Decimal("0")
        )
        target_percent = targets_by_symbol.get(symbol, Decimal("0"))
        current_percent = current_value / total_value * Decimal("100")
        target_value = total_value * target_percent / Decimal("100")
        difference_value = target_value - current_value

        if difference_value > Decimal("0.005"):
            action = "BUY"
        elif difference_value < Decimal("-0.005"):
            action = "SELL"
        else:
            action = "HOLD"

        recommendations.append(
            RebalanceRecommendation(
                symbol=symbol,
                current_value=_money(current_value),
                current_percent=_percent(current_percent),
                target_percent=_percent(target_percent),
                target_value=_money(target_value),
                difference_value=_money(difference_value),
                action=action,
            )
        )

    return RebalanceResponse(
        portfolio_id=portfolio.id,
        total_value=_money(total_value),
        recommendations=recommendations,
    )
