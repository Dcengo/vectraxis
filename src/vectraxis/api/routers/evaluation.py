"""Evaluation router for benchmark status."""

from fastapi import APIRouter
from pydantic import BaseModel

from vectraxis.models.evaluation import MetricType

router = APIRouter()


class EvaluationStatus(BaseModel):
    """Status of the evaluation subsystem."""

    available_metrics: list[str]
    status: str


@router.get(
    "/status",
    response_model=EvaluationStatus,
    summary="Evaluation status",
    description=(
        "Returns the status of the evaluation subsystem "
        "and lists all available benchmark metrics."
    ),
)
async def evaluation_status() -> EvaluationStatus:
    """Return evaluation subsystem status."""
    return EvaluationStatus(
        available_metrics=[m.value for m in MetricType],
        status="ready",
    )
