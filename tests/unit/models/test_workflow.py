"""Tests for Workflow models."""

from vectraxis.models.workflow import (
    NodeExecutionResult,
    NodeType,
    Workflow,
    WorkflowCreate,
    WorkflowEdge,
    WorkflowNode,
    WorkflowRunResult,
    WorkflowUpdate,
)


class TestNodeType:
    def test_values(self):
        assert NodeType.PROMPT == "prompt"
        assert NodeType.CONDITION == "condition"
        assert NodeType.DATA_SOURCE == "data_source"
        assert NodeType.VALIDATOR == "validator"
        assert NodeType.MERGER == "merger"
        assert NodeType.OUTPUT == "output"

    def test_all_types_count(self):
        assert len(NodeType) == 6


class TestWorkflowNode:
    def test_defaults(self):
        n = WorkflowNode(type=NodeType.PROMPT)
        assert n.id
        assert n.label == ""
        assert n.position == {"x": 0, "y": 0}
        assert n.config == {}

    def test_custom(self):
        n = WorkflowNode(
            id="n1",
            type=NodeType.CONDITION,
            label="Check score",
            config={"field": "score", "operator": ">", "value": 0.8},
        )
        assert n.type == NodeType.CONDITION
        assert n.config["field"] == "score"


class TestWorkflowEdge:
    def test_defaults(self):
        e = WorkflowEdge(source="n1", target="n2")
        assert e.id
        assert e.source_handle is None
        assert e.label == ""

    def test_with_handle(self):
        e = WorkflowEdge(source="n1", target="n2", source_handle="true")
        assert e.source_handle == "true"


class TestWorkflow:
    def test_defaults(self):
        wf = Workflow(name="test")
        assert wf.id
        assert wf.nodes == []
        assert wf.edges == []
        assert wf.version == 1

    def test_with_nodes_and_edges(self):
        wf = Workflow(
            name="pipeline",
            nodes=[WorkflowNode(id="n1", type=NodeType.OUTPUT)],
            edges=[WorkflowEdge(id="e1", source="n1", target="n2")],
        )
        assert len(wf.nodes) == 1
        assert len(wf.edges) == 1


class TestWorkflowCreate:
    def test_minimal(self):
        wc = WorkflowCreate(name="test")
        assert wc.name == "test"
        assert wc.nodes == []


class TestWorkflowUpdate:
    def test_all_none(self):
        wu = WorkflowUpdate()
        assert wu.name is None
        assert wu.nodes is None

    def test_partial(self):
        wu = WorkflowUpdate(name="renamed")
        data = wu.model_dump(exclude_none=True)
        assert data == {"name": "renamed"}


class TestNodeExecutionResult:
    def test_defaults(self):
        ner = NodeExecutionResult(node_id="n1", node_type=NodeType.PROMPT)
        assert ner.status == "completed"
        assert ner.output == ""
        assert ner.error is None


class TestWorkflowRunResult:
    def test_defaults(self):
        wrr = WorkflowRunResult(workflow_id="wf-1")
        assert wrr.status == "completed"
        assert wrr.node_results == []
        assert wrr.final_output == ""
