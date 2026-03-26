"""Chat router for conversational queries with data source references."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vectraxis.api.dependencies import (
    get_data_source_repo,
    get_pipeline,
    get_settings,
)
from vectraxis.models.agent import AgentType

router = APIRouter()


class DataSourceRef(BaseModel):
    """A reference to a data source in a chat message."""

    data_source_id: str
    data_source_name: str


class ChatRequest(BaseModel):
    """Request model for chat."""

    message: str
    data_sources: list[DataSourceRef] = []
    model: str | None = None
    agent_type: AgentType = AgentType.ANALYSIS


class DataSourceUsed(BaseModel):
    """A data source that was used in the response."""

    id: str
    name: str


class ChatResponse(BaseModel):
    """Response model for chat."""

    message: str
    response: str
    confidence: float
    data_sources_used: list[DataSourceUsed]
    steps: list[str]
    model: str


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat with data sources",
    description=(
        "Send a chat message with optional @data_source references. "
        "Referenced data sources are used to filter context retrieval."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message with optional data source filtering."""
    repo = get_data_source_repo()
    source_ids: list[str] | None = None
    sources_used: list[DataSourceUsed] = []

    if request.data_sources:
        source_ids = []
        for ref in request.data_sources:
            ds = await repo.get(ref.data_source_id)
            if ds is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Data source not found: {ref.data_source_id}",
                )
            source_ids.append(ref.data_source_id)
            sources_used.append(
                DataSourceUsed(
                    id=ref.data_source_id,
                    name=ref.data_source_name,
                )
            )

    settings = get_settings()
    model_name = request.model or settings.default_model

    # Try to create a real LLM provider; fall back to fake
    llm = None
    try:
        from vectraxis.agents.provider_registry import (
            get_provider_for_model,
        )

        llm = get_provider_for_model(model_name, settings)
    except (ValueError, ImportError):
        pass

    pipeline = get_pipeline(llm=llm)
    run = pipeline.run(
        query=request.message,
        agent_type=request.agent_type,
        source_ids=source_ids,
    )

    used_model = model_name if llm is not None else "fake"
    return ChatResponse(
        message=request.message,
        response=run.result.output if run.result else "",
        confidence=run.result.confidence if run.result else 0.0,
        data_sources_used=sources_used,
        steps=run.steps,
        model=used_model,
    )
