"""TDD tests for vectraxis.models.validation module.

Tests define the API contract for:
- ValidationStatus enum
- ValidationResult model
- ConfidenceScore model
"""

import pytest
from pydantic import ValidationError

from vectraxis.models.common import VectraxisModel
from vectraxis.models.validation import (
    ConfidenceScore,
    ValidationResult,
    ValidationStatus,
)

# --- ValidationStatus ---


class TestValidationStatus:
    """Tests for the ValidationStatus enum."""

    def test_has_passed(self):
        assert ValidationStatus.PASSED is not None

    def test_has_failed(self):
        assert ValidationStatus.FAILED is not None

    def test_has_warning(self):
        assert ValidationStatus.WARNING is not None

    def test_has_exactly_three_values(self):
        assert len(ValidationStatus) == 3

    def test_values_are_strings(self):
        for s in ValidationStatus:
            assert isinstance(s.value, str)


# --- ValidationResult ---


class TestValidationResult:
    """Tests for the ValidationResult model."""

    def test_create_with_required_fields(self):
        vr = ValidationResult(
            status=ValidationStatus.PASSED,
            message="All checks passed",
        )
        assert vr.status == ValidationStatus.PASSED
        assert vr.message == "All checks passed"

    def test_details_defaults_to_empty_dict(self):
        vr = ValidationResult(
            status=ValidationStatus.PASSED,
            message="ok",
        )
        assert vr.details == {}

    def test_details_can_be_set(self):
        details = {"field": "name", "constraint": "not_null"}
        vr = ValidationResult(
            status=ValidationStatus.FAILED,
            message="Validation failed",
            details=details,
        )
        assert vr.details == details

    def test_requires_status(self):
        with pytest.raises(ValidationError):
            ValidationResult(message="msg")

    def test_requires_message(self):
        with pytest.raises(ValidationError):
            ValidationResult(status=ValidationStatus.PASSED)

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            ValidationResult(status="INVALID", message="msg")

    def test_all_statuses_accepted(self):
        for status in ValidationStatus:
            vr = ValidationResult(status=status, message="test")
            assert vr.status == status

    def test_serialization(self):
        vr = ValidationResult(
            status=ValidationStatus.WARNING,
            message="check this",
            details={"hint": "review"},
        )
        data = vr.model_dump()
        assert data["message"] == "check this"
        assert data["details"] == {"hint": "review"}

    def test_is_vectraxis_model(self):
        assert issubclass(ValidationResult, VectraxisModel)


# --- ConfidenceScore ---


class TestConfidenceScore:
    """Tests for the ConfidenceScore model."""

    def test_create_with_required_fields(self):
        cs = ConfidenceScore(
            score=0.85,
            factors={"source_quality": 0.9, "coverage": 0.8},
            explanation="High confidence based on quality sources",
        )
        assert cs.score == 0.85
        assert cs.factors == {"source_quality": 0.9, "coverage": 0.8}

    def test_score_at_zero(self):
        cs = ConfidenceScore(score=0.0, factors={}, explanation="No confidence")
        assert cs.score == 0.0

    def test_score_at_one(self):
        cs = ConfidenceScore(score=1.0, factors={}, explanation="Full confidence")
        assert cs.score == 1.0

    def test_score_below_zero_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=-0.01, factors={}, explanation="invalid")

    def test_score_above_one_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=1.01, factors={}, explanation="invalid")

    def test_score_well_below_zero_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=-5.0, factors={}, explanation="invalid")

    def test_score_well_above_one_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=100.0, factors={}, explanation="invalid")

    def test_requires_score(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(factors={}, explanation="missing score")

    def test_requires_factors(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=0.5, explanation="missing factors")

    def test_requires_explanation(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(score=0.5, factors={})

    def test_factors_is_dict(self):
        cs = ConfidenceScore(
            score=0.5,
            factors={"key": "value", "num": 42},
            explanation="test",
        )
        assert isinstance(cs.factors, dict)

    def test_serialization(self):
        cs = ConfidenceScore(
            score=0.75,
            factors={"f1": 0.8},
            explanation="good",
        )
        data = cs.model_dump()
        assert data["score"] == 0.75
        assert data["factors"] == {"f1": 0.8}
        assert data["explanation"] == "good"

    def test_is_vectraxis_model(self):
        assert issubclass(ConfidenceScore, VectraxisModel)
