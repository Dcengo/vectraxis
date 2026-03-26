"""Simple pipeline for agent orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectraxis.models.agent import AgentTask, PipelineRun
from vectraxis.models.common import TaskStatus

if TYPE_CHECKING:
    from vectraxis.agents.router import TaskRouter
    from vectraxis.models.agent import AgentType
    from vectraxis.validation.validators import Validator


class Pipeline:
    """Orchestrates query processing through retrieval and agent execution."""

    def __init__(
        self,
        router: TaskRouter,
        retriever: Any = None,
        validator: Validator | None = None,
    ) -> None:
        self._router = router
        self._retriever = retriever
        self._validator = validator

    def run(
        self,
        query: str,
        agent_type: AgentType,
        source_ids: list[str] | None = None,
    ) -> PipelineRun:
        """Run the full pipeline for a query."""
        run = PipelineRun(
            query=query,
            status=TaskStatus.IN_PROGRESS,
            steps=["query_understanding"],
        )

        # Step 1: Create task
        task = AgentTask(query=query, agent_type=agent_type)
        run.steps.append("task_creation")

        # Step 2: Context retrieval (optional)
        context: list[str] = []
        if self._retriever:
            results = self._retriever.retrieve(query, source_ids=source_ids)
            context = [r.chunk.content for r in results]
            run.steps.append("context_retrieval")

        # Step 3: Agent execution
        agent = self._router.route(task)
        result = agent.execute(task, context)
        run.steps.append("agent_execution")

        # Step 4: Validation (optional)
        if self._validator and result:
            self._validator.validate(result, context)
            run.steps.append("validation")

        # Step 5: Complete
        run.result = result
        run.status = TaskStatus.COMPLETED
        run.steps.append("completed")
        return run
