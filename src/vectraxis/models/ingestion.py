from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel, generate_id


class DataSourceType(StrEnum):
    CSV = "csv"
    JSON = "json"
    TEXT_DOCUMENT = "text_document"


class DataSource(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    name: str
    source_type: DataSourceType
    file_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    record_count: int = 0


class RawRecord(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    source_id: str
    data: dict[str, Any]
    record_index: int


class NormalizedRecord(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    source_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    record_type: str
