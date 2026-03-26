"""Tests for ingestion loaders - written BEFORE implementation (TDD)."""

from pathlib import Path

import pytest

from vectraxis.ingestion.loaders import (
    CSVLoader,
    JSONLoader,
    Loader,
    TextDocumentLoader,
)
from vectraxis.models.ingestion import RawRecord

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


# ─── CSVLoader Tests ────────────────────────────────────────────────────────


class TestCSVLoader:
    def test_csv_loader_implements_loader_protocol(self):
        assert isinstance(CSVLoader(), Loader)

    def test_csv_loader_loads_records(self):
        loader = CSVLoader()
        records = loader.load(FIXTURES_DIR / "sample.csv", source_id="src-1")
        assert isinstance(records, list)
        assert len(records) == 3
        assert all(isinstance(r, RawRecord) for r in records)

    def test_csv_loader_record_data_contains_columns(self):
        loader = CSVLoader()
        records = loader.load(FIXTURES_DIR / "sample.csv", source_id="src-1")
        expected_keys = {
            "task_id",
            "assignee",
            "status",
            "duration_hours",
            "description",
        }
        for record in records:
            assert expected_keys.issubset(record.data.keys())

    def test_csv_loader_record_indices_are_sequential(self):
        loader = CSVLoader()
        records = loader.load(FIXTURES_DIR / "sample.csv", source_id="src-1")
        indices = [r.record_index for r in records]
        assert indices == [0, 1, 2]

    def test_csv_loader_sets_source_id(self):
        loader = CSVLoader()
        records = loader.load(FIXTURES_DIR / "sample.csv", source_id="my-source")
        assert all(r.source_id == "my-source" for r in records)

    def test_csv_loader_file_not_found_raises(self):
        loader = CSVLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(Path("/nonexistent/file.csv"), source_id="src-1")

    def test_csv_loader_empty_file_returns_empty(self, tmp_path: Path):
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("col_a,col_b\n")
        loader = CSVLoader()
        records = loader.load(empty_csv, source_id="src-1")
        assert records == []


# ─── JSONLoader Tests ───────────────────────────────────────────────────────


class TestJSONLoader:
    def test_json_loader_implements_loader_protocol(self):
        assert isinstance(JSONLoader(), Loader)

    def test_json_loader_loads_records(self):
        loader = JSONLoader()
        records = loader.load(FIXTURES_DIR / "sample.json", source_id="src-1")
        assert isinstance(records, list)
        assert len(records) == 2
        assert all(isinstance(r, RawRecord) for r in records)

    def test_json_loader_record_data_matches(self):
        loader = JSONLoader()
        records = loader.load(FIXTURES_DIR / "sample.json", source_id="src-1")
        assert records[0].data["task_id"] == "TASK-001"
        assert records[0].data["assignee"] == "Alice"
        assert records[0].data["duration_hours"] == 4.5
        assert records[1].data["task_id"] == "TASK-002"
        assert records[1].data["assignee"] == "Bob"

    def test_json_loader_record_indices_are_sequential(self):
        loader = JSONLoader()
        records = loader.load(FIXTURES_DIR / "sample.json", source_id="src-1")
        indices = [r.record_index for r in records]
        assert indices == [0, 1]

    def test_json_loader_sets_source_id(self):
        loader = JSONLoader()
        records = loader.load(FIXTURES_DIR / "sample.json", source_id="json-src")
        assert all(r.source_id == "json-src" for r in records)

    def test_json_loader_file_not_found_raises(self):
        loader = JSONLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(Path("/nonexistent/file.json"), source_id="src-1")

    def test_json_loader_invalid_json_raises(self, tmp_path: Path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{not valid json!!!")
        loader = JSONLoader()
        with pytest.raises(ValueError):
            loader.load(bad_json, source_id="src-1")


# ─── TextDocumentLoader Tests ──────────────────────────────────────────────


class TestTextDocumentLoader:
    def test_text_loader_implements_loader_protocol(self):
        assert isinstance(TextDocumentLoader(), Loader)

    def test_text_loader_loads_single_record(self):
        loader = TextDocumentLoader()
        records = loader.load(FIXTURES_DIR / "sample.txt", source_id="src-1")
        assert isinstance(records, list)
        assert len(records) == 1
        assert isinstance(records[0], RawRecord)

    def test_text_loader_record_data_has_content_key(self):
        loader = TextDocumentLoader()
        records = loader.load(FIXTURES_DIR / "sample.txt", source_id="src-1")
        assert "content" in records[0].data
        assert "Weekly Team Report" in records[0].data["content"]
        assert "API rate limiting" in records[0].data["content"]

    def test_text_loader_sets_source_id(self):
        loader = TextDocumentLoader()
        records = loader.load(FIXTURES_DIR / "sample.txt", source_id="txt-src")
        assert records[0].source_id == "txt-src"

    def test_text_loader_file_not_found_raises(self):
        loader = TextDocumentLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(Path("/nonexistent/file.txt"), source_id="src-1")
