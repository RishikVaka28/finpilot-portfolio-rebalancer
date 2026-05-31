from fastapi import APIRouter

from app.api.v1.endpoints import auth, holdings, portfolios, rebalance, targets

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
api_router.include_router(holdings.router, prefix="/portfolios", tags=["Holdings"])
api_router.include_router(targets.router, prefix="/portfolios", tags=["Targets"])
api_router.include_router(rebalance.router, prefix="/portfolios", tags=["Rebalance"])
