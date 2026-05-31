from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.target_allocation import TargetAllocation
from app.models.user import User
from app.schemas.target_allocation import (
    TargetAllocationCreate,
    TargetAllocationRead,
    TargetAllocationUpdate,
)
from app.services.portfolio_access import get_owned_portfolio

router = APIRouter()


@router.get("/{portfolio_id}/targets", response_model=list[TargetAllocationRead])
def list_targets(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TargetAllocation]:
    get_owned_portfolio(db, portfolio_id, current_user)
    return list(
        db.scalars(select(TargetAllocation).where(TargetAllocation.portfolio_id == portfolio_id))
    )


@router.post(
    "/{portfolio_id}/targets",
    response_model=TargetAllocationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    portfolio_id: int,
    payload: TargetAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TargetAllocation:
    get_owned_portfolio(db, portfolio_id, current_user)
    target = TargetAllocation(portfolio_id=portfolio_id, **payload.model_dump())
    db.add(target)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Target allocation already exists") from exc
    db.refresh(target)
    return target


@router.put("/{portfolio_id}/targets/{target_id}", response_model=TargetAllocationRead)
def update_target(
    portfolio_id: int,
    target_id: int,
    payload: TargetAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TargetAllocation:
    get_owned_portfolio(db, portfolio_id, current_user)
    target = db.get(TargetAllocation, target_id)
    if target is None or target.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Target allocation not found")
    target.target_percent = payload.target_percent
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{portfolio_id}/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(
    portfolio_id: int,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    get_owned_portfolio(db, portfolio_id, current_user)
    target = db.get(TargetAllocation, target_id)
    if target is None or target.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Target allocation not found")
    db.delete(target)
    db.commit()

