"""Ingestion router for file uploads."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from vectraxis.api.dependencies import get_data_source_repo, get_retriever
from vectraxis.ingestion.normalizers import WorkflowNormalizer
from vectraxis.ingestion.registry import create_default_registry
from vectraxis.models.common import generate_id
from vectraxis.models.ingestion import DataSource, DataSourceType
from vectraxis.models.retrieval import Document

router = APIRouter()

EXTENSION_MAP: dict[str, DataSourceType] = {
    ".csv": DataSourceType.CSV,
    ".json": DataSourceType.JSON,
    ".txt": DataSourceType.TEXT_DOCUMENT,
    ".text": DataSourceType.TEXT_DOCUMENT,
    ".docx": DataSourceType.TEXT_DOCUMENT,
}


class IngestResponse(BaseModel):
    """Response model for data ingestion."""

    source_id: str
    records_count: int
    message: str


@router.post(
    "/upload",
    response_model=IngestResponse,
    summary="Upload data file",
    description=(
        "Upload a CSV, JSON, or text file for ingestion into the pipeline. "
        "The file will be processed and normalized for downstream retrieval "
        "and analysis."
    ),
)
async def upload_data(file: UploadFile) -> IngestResponse:
    """Upload a data file for ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    source_id = generate_id()
    ext = Path(file.filename).suffix.lower()

    source_type = EXTENSION_MAP.get(ext)
    if source_type is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {ext}. Supported: {list(EXTENSION_MAP.keys())}"
            ),
        )

    # Write uploaded file to temp location
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Load records
        loader_registry = create_default_registry()
        loader = loader_registry.get(source_type)
        raw_records = loader.load(tmp_path, source_id)

        # Normalize
        normalizer = WorkflowNormalizer()
        normalized = [normalizer.normalize(r) for r in raw_records]

        # Convert to Documents and index in RAG
        documents = [
            Document(
                content=nr.content,
                metadata=nr.metadata,
                source_id=source_id,
            )
            for nr in normalized
        ]
        retriever = get_retriever()
        retriever.index(documents)

        # Persist the data source
        repo = get_data_source_repo()
        ds = DataSource(
            id=source_id,
            name=file.filename,
            source_type=source_type,
            file_path=str(tmp_path),
            metadata={"record_count": len(raw_records)},
            record_count=len(raw_records),
        )
        await repo.create(ds)
    finally:
        tmp_path.unlink(missing_ok=True)

    return IngestResponse(
        source_id=source_id,
        records_count=len(raw_records),
        message=(
            f"File '{file.filename}' processed: {len(raw_records)} records ingested"
        ),
    )
