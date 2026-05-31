from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TargetAllocation(Base):
    __tablename__ = "target_allocations"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "symbol", name="uq_target_portfolio_symbol"),
        CheckConstraint("target_percent >= 0 AND target_percent <= 100", name="ck_target_percent"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    target_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False)

    portfolio = relationship("Portfolio", back_populates="target_allocations")
