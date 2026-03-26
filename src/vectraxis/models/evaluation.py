from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel, generate_id


class MetricType(StrEnum):
    RETRIEVAL_RELEVANCE = "retrieval_relevance"
    ANSWER_FAITHFULNESS = "answer_faithfulness"
    RESPONSE_COMPLETENESS = "response_completeness"
    LATENCY = "latency"
    TOKEN_COST = "token_cost"


class MetricResult(VectraxisModel):
    metric_type: MetricType
    value: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkRun(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    name: str
    metrics: list[MetricResult] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class ExperimentConfig(VectraxisModel):
    name: str
    variations: list[dict[str, Any]]
    base_config: dict[str, Any] = Field(default_factory=dict)
