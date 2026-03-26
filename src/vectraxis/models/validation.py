from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel


class ValidationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class ValidationResult(VectraxisModel):
    status: ValidationStatus
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ConfidenceScore(VectraxisModel):
    score: float = Field(ge=0, le=1)
    factors: dict[str, Any]
    explanation: str
