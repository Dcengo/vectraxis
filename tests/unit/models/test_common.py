"""TDD tests for vectraxis.models.common module.

Tests define the API contract for:
- VectraxisModel base class
- generate_id() function
- TaskStatus enum
- Priority enum
- TimestampMixin
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel

from vectraxis.models.common import (
    Priority,
    TaskStatus,
    TimestampMixin,
    VectraxisModel,
    generate_id,
)

# --- generate_id() ---


class TestGenerateId:
    """Tests for the generate_id() utility function."""

    def test_returns_string(self):
        result = generate_id()
        assert isinstance(result, str)

    def test_returns_valid_uuid(self):
        result = generate_id()
        # Should not raise
        parsed = uuid.UUID(result)
        assert str(parsed) == result

    def test_returns_unique_values(self):
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_returns_uuid4_format(self):
        result = generate_id()
        parsed = uuid.UUID(result)
        assert parsed.version == 4


# --- VectraxisModel ---


class TestVectraxisModel:
    """Tests for the VectraxisModel base class."""

    def test_is_pydantic_base_model(self):
        assert issubclass(VectraxisModel, BaseModel)

    def test_is_not_frozen(self):
        """VectraxisModel should allow field mutation (frozen=False)."""

        class MyModel(VectraxisModel):
            name: str

        instance = MyModel(name="test")
        instance.name = "changed"
        assert instance.name == "changed"

    def test_has_config_dict(self):
        """VectraxisModel should use Pydantic ConfigDict."""
        config = VectraxisModel.model_config
        assert isinstance(config, dict)

    def test_subclass_inherits_config(self):
        class ChildModel(VectraxisModel):
            value: int

        instance = ChildModel(value=42)
        assert instance.value == 42
        # Should also be mutable
        instance.value = 99
        assert instance.value == 99

    def test_serialization(self):
        class SampleModel(VectraxisModel):
            name: str
            count: int

        instance = SampleModel(name="test", count=5)
        data = instance.model_dump()
        assert data == {"name": "test", "count": 5}

    def test_deserialization(self):
        class SampleModel(VectraxisModel):
            name: str
            count: int

        instance = SampleModel.model_validate({"name": "hello", "count": 10})
        assert instance.name == "hello"
        assert instance.count == 10


# --- TaskStatus ---


class TestTaskStatus:
    """Tests for the TaskStatus enum."""

    def test_has_pending(self):
        assert TaskStatus.PENDING is not None

    def test_has_in_progress(self):
        assert TaskStatus.IN_PROGRESS is not None

    def test_has_completed(self):
        assert TaskStatus.COMPLETED is not None

    def test_has_failed(self):
        assert TaskStatus.FAILED is not None

    def test_has_cancelled(self):
        assert TaskStatus.CANCELLED is not None

    def test_has_exactly_five_values(self):
        assert len(TaskStatus) == 5

    def test_values_are_strings(self):
        for status in TaskStatus:
            assert isinstance(status.value, str)

    def test_value_names(self):
        expected = {"PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"}
        assert {s.name for s in TaskStatus} == expected


# --- Priority ---


class TestPriority:
    """Tests for the Priority enum."""

    def test_has_low(self):
        assert Priority.LOW is not None

    def test_has_medium(self):
        assert Priority.MEDIUM is not None

    def test_has_high(self):
        assert Priority.HIGH is not None

    def test_has_critical(self):
        assert Priority.CRITICAL is not None

    def test_has_exactly_four_values(self):
        assert len(Priority) == 4

    def test_values_are_strings(self):
        for p in Priority:
            assert isinstance(p.value, str)


# --- TimestampMixin ---


class TestTimestampMixin:
    """Tests for the TimestampMixin model."""

    def test_created_at_is_datetime(self):
        instance = TimestampMixin()
        assert isinstance(instance.created_at, datetime)

    def test_created_at_defaults_to_now(self):
        before = datetime.now(UTC)
        instance = TimestampMixin()
        after = datetime.now(UTC)
        assert before <= instance.created_at <= after

    def test_updated_at_is_optional(self):
        instance = TimestampMixin()
        assert instance.updated_at is None

    def test_updated_at_can_be_set(self):
        now = datetime.now(UTC)
        instance = TimestampMixin(updated_at=now)
        assert instance.updated_at == now

    def test_created_at_can_be_overridden(self):
        custom_time = datetime(2024, 1, 1, tzinfo=UTC)
        instance = TimestampMixin(created_at=custom_time)
        assert instance.created_at == custom_time

    def test_is_pydantic_model(self):
        assert issubclass(TimestampMixin, BaseModel)

    def test_serialization_includes_timestamps(self):
        instance = TimestampMixin()
        data = instance.model_dump()
        assert "created_at" in data
        assert "updated_at" in data
