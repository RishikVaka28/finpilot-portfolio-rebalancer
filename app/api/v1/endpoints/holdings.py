from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.holding import Holding
from app.models.user import User
from app.schemas.holding import HoldingCreate, HoldingRead, HoldingUpdate
from app.services.portfolio_access import get_owned_portfolio

router = APIRouter()


@router.get("/{portfolio_id}/holdings", response_model=list[HoldingRead])
def list_holdings(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Holding]:
    get_owned_portfolio(db, portfolio_id, current_user)
    return list(db.scalars(select(Holding).where(Holding.portfolio_id == portfolio_id)))


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    portfolio_id: int,
    payload: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Holding:
    get_owned_portfolio(db, portfolio_id, current_user)
    holding = Holding(portfolio_id=portfolio_id, **payload.model_dump())
    db.add(holding)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Holding already exists") from exc
    db.refresh(holding)
    return holding


@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingRead)
def update_holding(
    portfolio_id: int,
    holding_id: int,
    payload: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Holding:
    get_owned_portfolio(db, portfolio_id, current_user)
    holding = db.get(Holding, holding_id)
    if holding is None or holding.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Holding not found")
    holding.quantity = payload.quantity
    holding.price = payload.price
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    get_owned_portfolio(db, portfolio_id, current_user)
    holding = db.get(Holding, holding_id)
    if holding is None or holding.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Holding not found")
    db.delete(holding)
    db.commit()

