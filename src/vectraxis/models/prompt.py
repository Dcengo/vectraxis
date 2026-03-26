"""Prompt management models."""

from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel, generate_id


class Prompt(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    name: str
    description: str = ""
    system_prompt: str = ""
    user_prompt_template: str
    model: str = ""
    agent_type: str = "analysis"
    output_json_schema: dict[str, Any] | None = None
    temperature: float = 0.7
    max_tokens: int = 1024
    variables: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PromptCreate(VectraxisModel):
    name: str
    description: str = ""
    system_prompt: str = ""
    user_prompt_template: str
    model: str = ""
    agent_type: str = "analysis"
    output_json_schema: dict[str, Any] | None = None
    temperature: float = 0.7
    max_tokens: int = 1024
    variables: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PromptUpdate(VectraxisModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    user_prompt_template: str | None = None
    model: str | None = None
    agent_type: str | None = None
    output_json_schema: dict[str, Any] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    variables: list[str] | None = None
    tags: list[str] | None = None
