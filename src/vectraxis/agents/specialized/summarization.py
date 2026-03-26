"""Summarization agent implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectraxis.agents.base import LLMProvider

from vectraxis.models.agent import AgentResult, AgentTask, AgentType


class SummarizationAgent:
    """Agent specialized in summarization tasks."""

    agent_type = AgentType.SUMMARIZATION

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    def execute(self, task: AgentTask, context: list[str] | None = None) -> AgentResult:
        prompt = f"Summarize the following query: {task.query}"
        if context:
            prompt += "\n\nContext:\n" + "\n".join(context)
        output = self._llm.generate(prompt, context)
        return AgentResult(
            task_id=task.id,
            agent_type=self.agent_type,
            output=output,
            confidence=0.85,
            evidence=context or [],
        )
