from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


OPENAPI_TAGS = [
    {
        "name": "Auth",
        "description": "Register users and issue JWT access tokens.",
    },
    {
        "name": "Portfolios",
        "description": "Create, view, update, and delete user-owned portfolios.",
    },
    {
        "name": "Holdings",
        "description": "Manage current portfolio positions and market prices.",
    },
    {
        "name": "Targets",
        "description": "Define desired allocation percentages for each symbol.",
    },
    {
        "name": "Rebalance",
        "description": "Calculate buy and sell recommendations from current vs target allocation.",
    },
    {
        "name": "Health",
        "description": "Operational readiness checks.",
    },
]


def create_app() -> FastAPI:
    """Application factory keeps startup testable and deployment friendly."""
    app = FastAPI(
        title=f"{settings.PROJECT_NAME} API",
        version=settings.VERSION,
        summary="JWT-secured portfolio rebalancing backend.",
        description=(
            "FinPilot helps users model portfolios, store holdings, define target "
            "allocations, and calculate rebalance actions."
        ),
        contact={"name": "FinPilot Engineering"},
        openapi_tags=OPENAPI_TAGS,
    )
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metadata", tags=["Health"])
    def metadata() -> dict[str, str]:
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs",
        }

    return app


app = create_app()
