from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioRead,
    PortfolioSummary,
    PortfolioUpdate,
)
from app.services.portfolio_access import get_owned_portfolio
from app.services.portfolio_summary import build_portfolio_summary

router = APIRouter()


@router.get("", response_model=list[PortfolioRead])
def list_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Portfolio]:
    return list(db.scalars(select(Portfolio).where(Portfolio.owner_id == current_user.id)))


@router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    payload: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    portfolio = Portfolio(name=payload.name, owner_id=current_user.id)
    db.add(portfolio)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Portfolio name already exists") from exc
    db.refresh(portfolio)
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioRead)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    return get_owned_portfolio(db, portfolio_id, current_user)


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioSummary:
    portfolio = get_owned_portfolio(db, portfolio_id, current_user)
    portfolio = (
        db.query(Portfolio)
        .options(selectinload(Portfolio.holdings))
        .filter(Portfolio.id == portfolio.id)
        .one()
    )
    return build_portfolio_summary(portfolio)


@router.put("/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    portfolio_id: int,
    payload: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    portfolio = get_owned_portfolio(db, portfolio_id, current_user)
    portfolio.name = payload.name
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Portfolio name already exists") from exc
    db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    portfolio = get_owned_portfolio(db, portfolio_id, current_user)
    db.delete(portfolio)
    db.commit()
