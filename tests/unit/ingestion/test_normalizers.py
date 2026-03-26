"""Tests for ingestion normalizers - written BEFORE implementation (TDD)."""

from vectraxis.ingestion.normalizers import WorkflowNormalizer
from vectraxis.models.ingestion import NormalizedRecord, RawRecord


class TestWorkflowNormalizer:
    def test_normalize_csv_record(self):
        raw = RawRecord(
            source_id="src-1",
            data={
                "task_id": "TASK-001",
                "assignee": "Alice",
                "status": "completed",
                "duration_hours": "4.5",
                "description": "Implement login page",
            },
            record_index=0,
        )
        normalizer = WorkflowNormalizer()
        result = normalizer.normalize(raw)

        assert isinstance(result, NormalizedRecord)
        assert result.record_type == "workflow_task"
        assert "TASK-001" in result.content
        assert "Alice" in result.content
        assert "completed" in result.content

    def test_normalize_preserves_source_id(self):
        raw = RawRecord(
            source_id="my-source-42",
            data={"task_id": "T1", "assignee": "X", "status": "done"},
            record_index=0,
        )
        normalizer = WorkflowNormalizer()
        result = normalizer.normalize(raw)
        assert result.source_id == "my-source-42"

    def test_normalize_includes_metadata(self):
        raw = RawRecord(
            source_id="src-1",
            data={
                "task_id": "TASK-005",
                "assignee": "Charlie",
                "status": "in_progress",
                "duration_hours": "2.0",
            },
            record_index=3,
        )
        normalizer = WorkflowNormalizer()
        result = normalizer.normalize(raw)

        assert "task_id" in result.metadata
        assert result.metadata["task_id"] == "TASK-005"
        assert "assignee" in result.metadata
        assert result.metadata["assignee"] == "Charlie"

    def test_normalize_text_record(self):
        raw = RawRecord(
            source_id="src-1",
            data={"content": "Some document text here."},
            record_index=0,
        )
        normalizer = WorkflowNormalizer()
        result = normalizer.normalize(raw)

        assert isinstance(result, NormalizedRecord)
        assert result.record_type == "document"
        assert result.content == "Some document text here."

    def test_normalize_generates_unique_id(self):
        raw1 = RawRecord(source_id="s", data={"content": "a"}, record_index=0)
        raw2 = RawRecord(source_id="s", data={"content": "b"}, record_index=1)
        normalizer = WorkflowNormalizer()
        r1 = normalizer.normalize(raw1)
        r2 = normalizer.normalize(raw2)
        assert r1.id != r2.id
