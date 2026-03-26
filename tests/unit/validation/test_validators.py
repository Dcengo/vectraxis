"""Tests for StructureValidator, FaithfulnessValidator, ConfidenceScorer."""

from vectraxis.models.agent import AgentResult, AgentType
from vectraxis.models.validation import (
    ConfidenceScore,
    ValidationResult,
    ValidationStatus,
)
from vectraxis.validation.validators import (
    ConfidenceScorer,
    FaithfulnessValidator,
    StructureValidator,
    Validator,
)


def make_result(
    output: str = "This is a test analysis of workflow data",
    confidence: float = 0.85,
    evidence: list[str] | None = None,
) -> AgentResult:
    return AgentResult(
        task_id="test-task-id",
        agent_type=AgentType.ANALYSIS,
        output=output,
        confidence=confidence,
        evidence=(
            evidence if evidence is not None else ["workflow data shows improvement"]
        ),
    )


# ---------------------------------------------------------------------------
# StructureValidator
# ---------------------------------------------------------------------------


class TestStructureValidator:
    def test_structure_validator_implements_protocol(self) -> None:
        assert isinstance(StructureValidator(), Validator)

    def test_structure_validator_passes_valid_output(self) -> None:
        validator = StructureValidator()
        result = validator.validate(make_result())
        assert result.status == ValidationStatus.PASSED
        assert "passed" in result.message.lower()

    def test_structure_validator_fails_too_short(self) -> None:
        validator = StructureValidator()
        result = validator.validate(make_result(output="short"))
        assert result.status == ValidationStatus.FAILED
        assert result.details["length"] == 5
        assert result.details["min_length"] == 10

    def test_structure_validator_warns_too_long(self) -> None:
        validator = StructureValidator(max_length=50)
        long_output = "a" * 100
        result = validator.validate(make_result(output=long_output))
        assert result.status == ValidationStatus.WARNING
        assert result.details["length"] == 100
        assert result.details["max_length"] == 50

    def test_structure_validator_custom_limits(self) -> None:
        validator = StructureValidator(min_length=5, max_length=20)
        result = validator.validate(make_result(output="hello world"))
        assert result.status == ValidationStatus.PASSED

    def test_structure_validator_at_boundary(self) -> None:
        validator = StructureValidator(min_length=10)
        result = validator.validate(make_result(output="a" * 10))
        assert result.status == ValidationStatus.PASSED


# ---------------------------------------------------------------------------
# FaithfulnessValidator
# ---------------------------------------------------------------------------


class TestFaithfulnessValidator:
    def test_faithfulness_validator_implements_protocol(self) -> None:
        assert isinstance(FaithfulnessValidator(), Validator)

    def test_faithfulness_passes_with_overlap(self) -> None:
        validator = FaithfulnessValidator()
        context = ["workflow data shows improvement in analysis"]
        result = validator.validate(make_result(), context=context)
        assert result.status == ValidationStatus.PASSED
        assert "overlap_ratio" in result.details

    def test_faithfulness_fails_with_no_overlap(self) -> None:
        validator = FaithfulnessValidator()
        context = ["xylophone zebra quantum"]
        unrelated = "completely unrelated output here enough length"
        result = validator.validate(
            make_result(output=unrelated),
            context=context,
        )
        assert result.status == ValidationStatus.FAILED
        assert result.details["overlap_ratio"] < validator._min_overlap_ratio

    def test_faithfulness_warns_no_context(self) -> None:
        validator = FaithfulnessValidator()
        result = validator.validate(make_result(), context=None)
        assert result.status == ValidationStatus.WARNING

    def test_faithfulness_warns_empty_context(self) -> None:
        validator = FaithfulnessValidator()
        result = validator.validate(make_result(), context=[])
        assert result.status == ValidationStatus.WARNING

    def test_faithfulness_custom_threshold(self) -> None:
        validator = FaithfulnessValidator(min_overlap_ratio=0.01)
        context = ["workflow data and many other unique words for testing"]
        result = validator.validate(make_result(), context=context)
        assert result.status == ValidationStatus.PASSED


# ---------------------------------------------------------------------------
# ConfidenceScorer
# ---------------------------------------------------------------------------


class TestConfidenceScorer:
    def test_confidence_scorer_basic_score(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result(confidence=0.8)
        validations = [
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
        ]
        score = scorer.score(agent_result, validations)
        assert isinstance(score, ConfidenceScore)
        assert 0.0 <= score.score <= 1.0

    def test_confidence_scorer_all_passed(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result(confidence=0.9)
        validations = [
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
        ]
        score = scorer.score(agent_result, validations)
        # All passed + high confidence + evidence -> high score
        assert score.score > 0.7

    def test_confidence_scorer_all_failed(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result(confidence=0.3)
        validations = [
            ValidationResult(status=ValidationStatus.FAILED, message="bad"),
            ValidationResult(status=ValidationStatus.FAILED, message="bad"),
        ]
        score = scorer.score(agent_result, validations)
        assert score.score < 0.5

    def test_confidence_scorer_no_evidence(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result(confidence=0.5, evidence=[])
        validations = [
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
        ]
        score = scorer.score(agent_result, validations)
        # No evidence -> lower than with evidence
        scorer2 = ConfidenceScorer()
        agent_result2 = make_result(confidence=0.5, evidence=["some evidence"])
        score2 = scorer2.score(agent_result2, validations)
        assert score.score < score2.score

    def test_confidence_scorer_score_in_range(self) -> None:
        scorer = ConfidenceScorer()
        for conf in [0.0, 0.5, 1.0]:
            for evidence in [[], ["e"]]:
                agent_result = make_result(confidence=conf, evidence=evidence)
                validations = [
                    ValidationResult(status=ValidationStatus.PASSED, message="ok"),
                ]
                s = scorer.score(agent_result, validations)
                assert 0.0 <= s.score <= 1.0

    def test_confidence_scorer_has_factors(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result()
        validations = [
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
        ]
        score = scorer.score(agent_result, validations)
        assert "agent_confidence" in score.factors
        assert "validation_pass_rate" in score.factors
        assert "has_evidence" in score.factors

    def test_confidence_scorer_has_explanation(self) -> None:
        scorer = ConfidenceScorer()
        agent_result = make_result()
        validations = [
            ValidationResult(status=ValidationStatus.PASSED, message="ok"),
        ]
        score = scorer.score(agent_result, validations)
        assert len(score.explanation) > 0
        assert "Score" in score.explanation
