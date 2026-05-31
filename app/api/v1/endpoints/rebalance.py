from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.rebalance import RebalanceResponse
from app.services.portfolio_access import get_owned_portfolio
from app.services.rebalance import calculate_rebalance

router = APIRouter()


@router.get("/{portfolio_id}/rebalance", response_model=RebalanceResponse)
def get_rebalance(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RebalanceResponse:
    portfolio = get_owned_portfolio(db, portfolio_id, current_user)
    # Eager load collections before the service layer so its inputs are complete.
    portfolio = (
        db.query(Portfolio)
        .options(selectinload(Portfolio.holdings), selectinload(Portfolio.target_allocations))
        .filter(Portfolio.id == portfolio.id)
        .one()
    )
    return calculate_rebalance(portfolio)
