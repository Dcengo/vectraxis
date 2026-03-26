from enum import StrEnum

from pydantic import Field

from vectraxis.models.common import (
    Priority,
    TaskStatus,
    VectraxisModel,
    generate_id,
)


class AgentType(StrEnum):
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    RECOMMENDATION = "recommendation"


class AgentTask(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    query: str
    agent_type: AgentType
    context: list[str] = Field(default_factory=list)
    priority: Priority = Priority.MEDIUM


class AgentResult(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    task_id: str
    agent_type: AgentType
    output: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]


class PipelineRun(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    query: str
    status: TaskStatus
    steps: list[str] = Field(default_factory=list)
    result: AgentResult | None = None
