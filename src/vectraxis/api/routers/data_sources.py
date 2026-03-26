"""Data sources router for listing uploaded data sources."""

from fastapi import APIRouter
from pydantic import BaseModel

from vectraxis.api.dependencies import get_data_source_repo
from vectraxis.models.ingestion import DataSourceType

router = APIRouter()


class DataSourceInfo(BaseModel):
    """Response model for a data source."""

    id: str
    name: str
    source_type: DataSourceType
    record_count: int


@router.get(
    "/",
    response_model=list[DataSourceInfo],
    summary="List data sources",
    description="Return all uploaded data sources with their metadata.",
)
async def list_data_sources() -> list[DataSourceInfo]:
    """List all registered data sources."""
    repo = get_data_source_repo()
    sources = await repo.list_all()
    return [
        DataSourceInfo(
            id=ds.id,
            name=ds.name,
            source_type=ds.source_type,
            record_count=ds.metadata.get("record_count", 0),
        )
        for ds in sources
    ]
