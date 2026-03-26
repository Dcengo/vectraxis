"""Health check router."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current service status and API version.",
)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="healthy", version="0.1.0")
