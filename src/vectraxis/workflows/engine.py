"""Workflow execution engine — runs a DAG of workflow nodes."""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from typing import TYPE_CHECKING, Any

from vectraxis.models.workflow import (
    NodeExecutionResult,
    NodeType,
    Workflow,
    WorkflowRunResult,
)

if TYPE_CHECKING:
    from vectraxis.config import Settings
    from vectraxis.db.repositories.data_source import DataSourceRepository
    from vectraxis.db.repositories.prompt import PromptRepository
    from vectraxis.retrieval.rag import RAGRetriever


class WorkflowEngine:
    """Executes a workflow by traversing nodes in topological order."""

    def __init__(
        self,
        prompt_repo: PromptRepository,
        data_source_repo: DataSourceRepository,
        retriever: RAGRetriever,
        settings: Settings,
    ) -> None:
        self._prompt_repo = prompt_repo
        self._ds_repo = data_source_repo
        self._retriever = retriever
        self._settings = settings

    async def run(self, workflow: Workflow) -> WorkflowRunResult:
        start = time.perf_counter()
        node_map = {n.id: n for n in workflow.nodes}

        # Build adjacency and in-degree for topological sort
        adj: dict[str, list[str]] = defaultdict(list)
        in_degree: dict[str, int] = {n.id: 0 for n in workflow.nodes}
        edge_map: dict[tuple[str, str | None], str] = {}  # (source, handle) -> target

        for edge in workflow.edges:
            adj[edge.source].append(edge.target)
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1
            edge_map[(edge.source, edge.source_handle)] = edge.target

        # Topological sort (Kahn's algorithm)
        try:
            order = _topological_sort(list(node_map.keys()), adj, in_degree)
        except ValueError as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return WorkflowRunResult(
                workflow_id=workflow.id,
                status="failed",
                error=str(exc),
                duration_ms=elapsed,
            )

        # Execute nodes in order
        node_outputs: dict[str, str] = {}
        node_results: list[NodeExecutionResult] = []
        skipped: set[str] = set()
        final_output = ""

        for nid in order:
            if nid in skipped:
                node_results.append(
                    NodeExecutionResult(
                        node_id=nid,
                        node_type=node_map[nid].type,
                        status="skipped",
                    )
                )
                continue

            node = node_map[nid]
            # Gather upstream inputs
            upstream_inputs = _gather_inputs(nid, workflow, node_outputs)

            t0 = time.perf_counter()
            try:
                output = await self._execute_node(
                    node.type, node.config, upstream_inputs
                )
                dur = (time.perf_counter() - t0) * 1000

                node_outputs[nid] = output
                node_results.append(
                    NodeExecutionResult(
                        node_id=nid,
                        node_type=node.type,
                        status="completed",
                        output=output,
                        duration_ms=dur,
                    )
                )

                # Handle condition branching
                if node.type == NodeType.CONDITION:
                    branch = output  # "true" or "false"
                    for edge in workflow.edges:
                        if edge.source == nid and edge.source_handle != branch:
                            _mark_descendants_skipped(
                                edge.target, adj, skipped, node_map, workflow
                            )

                if node.type == NodeType.OUTPUT:
                    final_output = output

            except Exception as exc:
                dur = (time.perf_counter() - t0) * 1000
                node_results.append(
                    NodeExecutionResult(
                        node_id=nid,
                        node_type=node.type,
                        status="failed",
                        error=str(exc),
                        duration_ms=dur,
                    )
                )
                elapsed = (time.perf_counter() - start) * 1000
                return WorkflowRunResult(
                    workflow_id=workflow.id,
                    status="failed",
                    node_results=node_results,
                    error=str(exc),
                    duration_ms=elapsed,
                )

        elapsed = (time.perf_counter() - start) * 1000
        return WorkflowRunResult(
            workflow_id=workflow.id,
            status="completed",
            node_results=node_results,
            final_output=final_output,
            duration_ms=elapsed,
        )

    async def _execute_node(
        self, node_type: NodeType, config: dict[str, Any], inputs: str
    ) -> str:
        if node_type == NodeType.PROMPT:
            return await self._exec_prompt(config, inputs)
        if node_type == NodeType.CONDITION:
            return self._exec_condition(config, inputs)
        if node_type == NodeType.DATA_SOURCE:
            return await self._exec_data_source(config)
        if node_type == NodeType.VALIDATOR:
            return self._exec_validator(config, inputs)
        if node_type == NodeType.MERGER:
            return inputs  # inputs already merged
        if node_type == NodeType.OUTPUT:
            fmt = config.get("format", "text")
            if fmt == "json":
                return json.dumps({"result": inputs})
            return inputs
        return inputs

    async def _exec_prompt(self, config: dict[str, Any], inputs: str) -> str:
        prompt_id = config.get("prompt_id")
        if not prompt_id:
            raise ValueError("Prompt node missing prompt_id in config")
        prompt = await self._prompt_repo.get(prompt_id)
        if prompt is None:
            raise ValueError(f"Prompt not found: {prompt_id}")

        # Render template — replace {{input}} with upstream data
        rendered = prompt.user_prompt_template.replace("{{input}}", inputs)
        # Replace other variable placeholders
        for var in prompt.variables:
            rendered = rendered.replace(f"{{{{{var}}}}}", inputs)

        # Build system prompt with optional JSON schema instruction
        system = prompt.system_prompt
        if prompt.output_json_schema:
            schema_str = json.dumps(prompt.output_json_schema)
            system += f"\nRespond with valid JSON matching this schema: {schema_str}"

        # Call LLM
        from vectraxis.agents.base import FakeLLMProvider, LLMProvider

        llm: LLMProvider
        try:
            from vectraxis.agents.provider_registry import get_provider_for_model

            model = prompt.model or self._settings.default_model
            llm = get_provider_for_model(model, self._settings)
        except (ValueError, ImportError):
            llm = FakeLLMProvider()

        full_prompt = f"{system}\n\n{rendered}" if system else rendered
        return llm.generate(full_prompt, context=[inputs] if inputs else None)

    def _exec_condition(self, config: dict[str, Any], inputs: str) -> str:
        field = config.get("field", "")
        operator = config.get("operator", "==")
        value = config.get("value", "")

        # Try to extract field value from inputs
        test_value = inputs
        if field:
            # Try JSON parsing
            try:
                data = json.loads(inputs)
                if isinstance(data, dict):
                    test_value = str(data.get(field, inputs))
            except (json.JSONDecodeError, TypeError):
                test_value = inputs

        # Evaluate condition
        try:
            if operator == ">":
                result = float(test_value) > float(value)
            elif operator == "<":
                result = float(test_value) < float(value)
            elif operator == ">=":
                result = float(test_value) >= float(value)
            elif operator == "<=":
                result = float(test_value) <= float(value)
            elif operator == "!=":
                result = str(test_value) != str(value)
            elif operator == "contains":
                result = str(value) in str(test_value)
            else:  # ==
                result = str(test_value) == str(value)
        except (ValueError, TypeError):
            result = False

        return "true" if result else "false"

    async def _exec_data_source(self, config: dict[str, Any]) -> str:
        ds_id = config.get("data_source_id")
        if not ds_id:
            raise ValueError("DataSource node missing data_source_id in config")
        ds = await self._ds_repo.get(ds_id)
        if ds is None:
            raise ValueError(f"Data source not found: {ds_id}")
        results = self._retriever.retrieve("*", top_k=10, source_ids=[ds_id])
        return "\n".join(r.chunk.content for r in results) if results else ""

    def _exec_validator(self, config: dict[str, Any], inputs: str) -> str:
        from vectraxis.models.agent import AgentResult, AgentType

        validator_type = config.get("validator_type", "structure")
        result_obj = AgentResult(
            output=inputs,
            confidence=0.5,
            agent_type=AgentType.ANALYSIS,
            task_id="validator",
            evidence=[],
        )
        if validator_type == "faithfulness":
            from vectraxis.validation.validators import FaithfulnessValidator

            f_validator = FaithfulnessValidator()
            vr = f_validator.validate(result_obj, context=[inputs])
        else:
            from vectraxis.validation.validators import StructureValidator

            min_length = config.get("min_length", 10)
            s_validator = StructureValidator(min_length=min_length)
            vr = s_validator.validate(result_obj)

        return f"{vr.status.value}: {vr.message}"


def _topological_sort(
    nodes: list[str],
    adj: dict[str, list[str]],
    in_degree: dict[str, int],
) -> list[str]:
    """Kahn's algorithm. Raises ValueError on cycles."""
    queue = deque(n for n in nodes if in_degree.get(n, 0) == 0)
    order: list[str] = []
    in_deg = dict(in_degree)

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adj.get(node, []):
            in_deg[neighbor] -= 1
            if in_deg[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(nodes):
        raise ValueError("Workflow contains a cycle")

    return order


def _gather_inputs(
    node_id: str, workflow: Workflow, node_outputs: dict[str, str]
) -> str:
    """Gather outputs from all upstream nodes connected to this node."""
    parts = []
    for edge in workflow.edges:
        if edge.target == node_id and edge.source in node_outputs:
            parts.append(node_outputs[edge.source])
    return "\n".join(parts) if parts else ""


def _mark_descendants_skipped(
    node_id: str,
    adj: dict[str, list[str]],
    skipped: set[str],
    node_map: dict[str, Any],
    workflow: Workflow,
) -> None:
    """Mark a node and all its descendants as skipped."""
    if node_id in skipped:
        return
    skipped.add(node_id)
    for neighbor in adj.get(node_id, []):
        _mark_descendants_skipped(neighbor, adj, skipped, node_map, workflow)
