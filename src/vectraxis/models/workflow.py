"""Workflow models for the visual workflow builder."""

from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from enum import StrEnum
from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel, generate_id


class NodeType(StrEnum):
    PROMPT = "prompt"
    CONDITION = "condition"
    DATA_SOURCE = "data_source"
    VALIDATOR = "validator"
    MERGER = "merger"
    OUTPUT = "output"


class WorkflowNode(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    type: NodeType
    label: str = ""
    position: dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    source: str
    target: str
    source_handle: str | None = None
    label: str = ""


class Workflow(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    name: str
    description: str = ""
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WorkflowCreate(VectraxisModel):
    name: str
    description: str = ""
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class WorkflowUpdate(VectraxisModel):
    name: str | None = None
    description: str | None = None
    nodes: list[WorkflowNode] | None = None
    edges: list[WorkflowEdge] | None = None
    tags: list[str] | None = None


class NodeExecutionResult(VectraxisModel):
    node_id: str
    node_type: NodeType
    status: str = "completed"
    output: str = ""
    error: str | None = None
    duration_ms: float = 0.0


class WorkflowRunResult(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    workflow_id: str
    status: str = "completed"
    node_results: list[NodeExecutionResult] = Field(default_factory=list)
    final_output: str = ""
    error: str | None = None
    duration_ms: float = 0.0
