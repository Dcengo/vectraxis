"""Pipelines router for listing available pipelines."""

from fastapi import APIRouter
from pydantic import BaseModel

from vectraxis.models.agent import AgentType

router = APIRouter()


class PipelineInfo(BaseModel):
    """Information about an available pipeline."""

    name: str
    description: str
    agent_types: list[AgentType]


@router.get(
    "/",
    response_model=list[PipelineInfo],
    summary="List pipelines",
    description=(
        "Returns all available agentic pipelines with their supported agent types."
    ),
)
async def list_pipelines() -> list[PipelineInfo]:
    """List all available pipelines."""
    return [
        PipelineInfo(
            name="analysis",
            description="Analyze workflow data",
            agent_types=[AgentType.ANALYSIS],
        ),
        PipelineInfo(
            name="summarization",
            description="Summarize workflow data",
            agent_types=[AgentType.SUMMARIZATION],
        ),
        PipelineInfo(
            name="recommendation",
            description="Generate recommendations",
            agent_types=[AgentType.RECOMMENDATION],
        ),
    ]
