"""Query router for running pipeline queries."""

from fastapi import APIRouter
from pydantic import BaseModel

from vectraxis.api.dependencies import get_pipeline, get_settings
from vectraxis.models.agent import AgentType

router = APIRouter()


class QueryRequest(BaseModel):
    """Request model for pipeline queries."""

    query: str
    agent_type: AgentType = AgentType.ANALYSIS
    model: str | None = None


class QueryResponse(BaseModel):
    """Response model for pipeline queries."""

    query: str
    output: str
    confidence: float
    agent_type: AgentType
    steps: list[str]
    model: str


@router.post(
    "/",
    response_model=QueryResponse,
    summary="Run a query",
    description="Execute a natural language query through the agentic pipeline. "
    "Choose an agent type to control the kind of analysis performed. "
    "Optionally specify a model to use for LLM calls.",
)
async def run_query(request: QueryRequest) -> QueryResponse:
    """Run a query through the pipeline."""
    settings = get_settings()
    model_name = request.model or settings.default_model

    # Try to create a real LLM provider; fall back to fake
    llm = None
    try:
        from vectraxis.agents.provider_registry import get_provider_for_model

        llm = get_provider_for_model(model_name, settings)
    except (ValueError, ImportError):
        pass

    pipeline = get_pipeline(llm=llm)
    run = pipeline.run(query=request.query, agent_type=request.agent_type)

    used_model = model_name if llm is not None else "fake"
    return QueryResponse(
        query=run.query,
        output=run.result.output if run.result else "",
        confidence=run.result.confidence if run.result else 0.0,
        agent_type=request.agent_type,
        steps=run.steps,
        model=used_model,
    )
