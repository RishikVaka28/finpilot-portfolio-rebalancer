from decimal import Decimal, ROUND_HALF_UP

from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioAllocation, PortfolioSummary


TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _percent(value: Decimal) -> Decimal:
    return value.quantize(FOURPLACES, rounding=ROUND_HALF_UP)


def build_portfolio_summary(portfolio: Portfolio) -> PortfolioSummary:
    """Build a read-only snapshot of portfolio value and current allocation."""
    values_by_symbol: dict[str, Decimal] = {}
    for holding in portfolio.holdings:
        values_by_symbol[holding.symbol] = (
            values_by_symbol.get(holding.symbol, Decimal("0"))
            + Decimal(holding.quantity) * Decimal(holding.price)
        )

    total_value = sum(values_by_symbol.values(), Decimal("0"))
    allocations = []
    for symbol, market_value in sorted(values_by_symbol.items()):
        current_percent = (
            market_value / total_value * Decimal("100")
            if total_value > 0
            else Decimal("0")
        )
        allocations.append(
            PortfolioAllocation(
                symbol=symbol,
                market_value=_money(market_value),
                current_percent=_percent(current_percent),
            )
        )

    return PortfolioSummary(
        portfolio_id=portfolio.id,
        portfolio_name=portfolio.name,
        total_value=_money(total_value),
        holdings_count=len(portfolio.holdings),
        allocations=allocations,
    )
