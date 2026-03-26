"""Task router for directing tasks to appropriate agents."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectraxis.agents.base import Agent
    from vectraxis.models.agent import AgentTask, AgentType


class TaskRouter:
    """Routes tasks to the appropriate agent based on agent type."""

    def __init__(self, agents: dict[AgentType, Agent]) -> None:
        self._agents = agents

    def route(self, task: AgentTask) -> Agent:
        """Route a task to the correct agent.

        Raises:
            ValueError: If no agent is registered for the task's agent type.
        """
        agent = self._agents.get(task.agent_type)
        if agent is None:
            msg = f"No agent registered for type: {task.agent_type}"
            raise ValueError(msg)
        return agent
