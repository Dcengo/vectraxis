"""TDD tests for vectraxis.models.ingestion module.

Tests define the API contract for:
- DataSourceType enum
- DataSource model
- RawRecord model
- NormalizedRecord model
"""

import pytest
from pydantic import ValidationError

from vectraxis.models.common import VectraxisModel, generate_id
from vectraxis.models.ingestion import (
    DataSource,
    DataSourceType,
    NormalizedRecord,
    RawRecord,
)

# --- DataSourceType ---


class TestDataSourceType:
    """Tests for the DataSourceType enum."""

    def test_has_csv(self):
        assert DataSourceType.CSV is not None

    def test_has_json(self):
        assert DataSourceType.JSON is not None

    def test_has_text_document(self):
        assert DataSourceType.TEXT_DOCUMENT is not None

    def test_has_exactly_three_values(self):
        assert len(DataSourceType) == 3

    def test_values_are_strings(self):
        for t in DataSourceType:
            assert isinstance(t.value, str)


# --- DataSource ---


class TestDataSource:
    """Tests for the DataSource model."""

    def test_create_with_required_fields(self):
        ds = DataSource(
            id=generate_id(),
            name="test_source",
            source_type=DataSourceType.CSV,
            file_path="/data/test.csv",
        )
        assert ds.name == "test_source"
        assert ds.source_type == DataSourceType.CSV
        assert ds.file_path == "/data/test.csv"

    def test_id_is_string(self):
        ds = DataSource(
            id="abc-123",
            name="src",
            source_type=DataSourceType.JSON,
            file_path="/data/test.json",
        )
        assert isinstance(ds.id, str)

    def test_metadata_defaults_to_empty_dict(self):
        ds = DataSource(
            id=generate_id(),
            name="src",
            source_type=DataSourceType.CSV,
            file_path="/data/test.csv",
        )
        assert ds.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"encoding": "utf-8", "delimiter": ","}
        ds = DataSource(
            id=generate_id(),
            name="src",
            source_type=DataSourceType.CSV,
            file_path="/data/test.csv",
            metadata=meta,
        )
        assert ds.metadata == meta

    def test_requires_name(self):
        with pytest.raises(ValidationError):
            DataSource(
                id=generate_id(),
                source_type=DataSourceType.CSV,
                file_path="/data/test.csv",
            )

    def test_requires_source_type(self):
        with pytest.raises(ValidationError):
            DataSource(
                id=generate_id(),
                name="src",
                file_path="/data/test.csv",
            )

    def test_requires_file_path(self):
        with pytest.raises(ValidationError):
            DataSource(
                id=generate_id(),
                name="src",
                source_type=DataSourceType.CSV,
            )

    def test_invalid_source_type_raises(self):
        with pytest.raises(ValidationError):
            DataSource(
                id=generate_id(),
                name="src",
                source_type="INVALID",
                file_path="/data/test.csv",
            )

    def test_serialization(self):
        ds = DataSource(
            id="test-id",
            name="src",
            source_type=DataSourceType.JSON,
            file_path="/data/test.json",
            metadata={"key": "value"},
        )
        data = ds.model_dump()
        assert data["id"] == "test-id"
        assert data["name"] == "src"
        assert data["file_path"] == "/data/test.json"
        assert data["metadata"] == {"key": "value"}

    def test_is_vectraxis_model(self):
        assert issubclass(DataSource, VectraxisModel)


# --- RawRecord ---


class TestRawRecord:
    """Tests for the RawRecord model."""

    def test_create_with_required_fields(self):
        rr = RawRecord(
            id=generate_id(),
            source_id="source-1",
            data={"col1": "val1", "col2": "val2"},
            record_index=0,
        )
        assert rr.source_id == "source-1"
        assert rr.data == {"col1": "val1", "col2": "val2"}
        assert rr.record_index == 0

    def test_data_is_dict(self):
        rr = RawRecord(
            id=generate_id(),
            source_id="s1",
            data={"key": "value"},
            record_index=1,
        )
        assert isinstance(rr.data, dict)

    def test_record_index_is_int(self):
        rr = RawRecord(
            id=generate_id(),
            source_id="s1",
            data={},
            record_index=42,
        )
        assert isinstance(rr.record_index, int)
        assert rr.record_index == 42

    def test_requires_source_id(self):
        with pytest.raises(ValidationError):
            RawRecord(id=generate_id(), data={}, record_index=0)

    def test_requires_data(self):
        with pytest.raises(ValidationError):
            RawRecord(id=generate_id(), source_id="s1", record_index=0)

    def test_requires_record_index(self):
        with pytest.raises(ValidationError):
            RawRecord(id=generate_id(), source_id="s1", data={})

    def test_serialization(self):
        rr = RawRecord(id="rec-1", source_id="s1", data={"a": 1}, record_index=5)
        data = rr.model_dump()
        assert data["source_id"] == "s1"
        assert data["data"] == {"a": 1}
        assert data["record_index"] == 5

    def test_is_vectraxis_model(self):
        assert issubclass(RawRecord, VectraxisModel)


# --- NormalizedRecord ---


class TestNormalizedRecord:
    """Tests for the NormalizedRecord model."""

    def test_create_with_required_fields(self):
        nr = NormalizedRecord(
            id=generate_id(),
            source_id="source-1",
            content="This is normalized content",
            record_type="text",
        )
        assert nr.content == "This is normalized content"
        assert nr.record_type == "text"

    def test_metadata_defaults_to_empty_dict(self):
        nr = NormalizedRecord(
            id=generate_id(),
            source_id="s1",
            content="content",
            record_type="text",
        )
        assert nr.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"language": "en", "tokens": 150}
        nr = NormalizedRecord(
            id=generate_id(),
            source_id="s1",
            content="content",
            metadata=meta,
            record_type="text",
        )
        assert nr.metadata == meta

    def test_requires_content(self):
        with pytest.raises(ValidationError):
            NormalizedRecord(
                id=generate_id(),
                source_id="s1",
                record_type="text",
            )

    def test_requires_source_id(self):
        with pytest.raises(ValidationError):
            NormalizedRecord(
                id=generate_id(),
                content="content",
                record_type="text",
            )

    def test_requires_record_type(self):
        with pytest.raises(ValidationError):
            NormalizedRecord(
                id=generate_id(),
                source_id="s1",
                content="content",
            )

    def test_serialization(self):
        nr = NormalizedRecord(
            id="nr-1",
            source_id="s1",
            content="normalized",
            metadata={"key": "val"},
            record_type="csv_row",
        )
        data = nr.model_dump()
        assert data["content"] == "normalized"
        assert data["record_type"] == "csv_row"
        assert data["metadata"] == {"key": "val"}

    def test_is_vectraxis_model(self):
        assert issubclass(NormalizedRecord, VectraxisModel)
