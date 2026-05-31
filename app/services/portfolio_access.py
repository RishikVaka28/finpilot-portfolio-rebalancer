from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.user import User


def get_owned_portfolio(db: Session, portfolio_id: int, user: User) -> Portfolio:
    portfolio = db.get(Portfolio, portfolio_id)
    if portfolio is None or portfolio.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio

