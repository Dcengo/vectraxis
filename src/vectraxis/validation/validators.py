"""Validation layer: validators and confidence scoring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from vectraxis.models.validation import (
    ConfidenceScore,
    ValidationResult,
    ValidationStatus,
)

if TYPE_CHECKING:
    from vectraxis.models.agent import AgentResult


@runtime_checkable
class Validator(Protocol):
    def validate(
        self, result: AgentResult, context: list[str] | None = None
    ) -> ValidationResult: ...


class StructureValidator:
    """Validates agent output structure (non-empty, reasonable length)."""

    def __init__(self, min_length: int = 10, max_length: int = 10000) -> None:
        self._min_length = min_length
        self._max_length = max_length

    def validate(
        self, result: AgentResult, context: list[str] | None = None
    ) -> ValidationResult:
        if len(result.output) < self._min_length:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Output too short",
                details={"length": len(result.output), "min_length": self._min_length},
            )
        if len(result.output) > self._max_length:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Output exceeds maximum length",
                details={"length": len(result.output), "max_length": self._max_length},
            )
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="Structure validation passed",
        )


class FaithfulnessValidator:
    """Validates output references provided context via keyword overlap."""

    def __init__(self, min_overlap_ratio: float = 0.1) -> None:
        self._min_overlap_ratio = min_overlap_ratio

    def validate(
        self, result: AgentResult, context: list[str] | None = None
    ) -> ValidationResult:
        if not context:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="No context provided for faithfulness check",
            )

        # Simple word overlap check between output and context
        output_words = set(result.output.lower().split())
        context_text = " ".join(context).lower()
        context_words = set(context_text.split())

        if not context_words:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Empty context",
            )

        overlap = output_words & context_words
        ratio = len(overlap) / len(context_words) if context_words else 0

        if ratio >= self._min_overlap_ratio:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="Faithfulness check passed",
                details={"overlap_ratio": ratio},
            )
        return ValidationResult(
            status=ValidationStatus.FAILED,
            message="Low faithfulness score",
            details={"overlap_ratio": ratio, "min_required": self._min_overlap_ratio},
        )


class ConfidenceScorer:
    """Computes confidence score based on multiple factors."""

    def score(
        self, result: AgentResult, validation_results: list[ValidationResult]
    ) -> ConfidenceScore:
        factors: dict[str, float] = {}

        # Factor 1: Agent's own confidence
        factors["agent_confidence"] = result.confidence

        # Factor 2: Validation pass rate
        if validation_results:
            passed = sum(
                1 for v in validation_results if v.status == ValidationStatus.PASSED
            )
            factors["validation_pass_rate"] = passed / len(validation_results)
        else:
            factors["validation_pass_rate"] = 0.5

        # Factor 3: Evidence availability
        factors["has_evidence"] = 1.0 if result.evidence else 0.0

        # Weighted average
        weights = {
            "agent_confidence": 0.4,
            "validation_pass_rate": 0.4,
            "has_evidence": 0.2,
        }
        score = sum(factors[k] * weights[k] for k in weights)

        agent_conf = factors["agent_confidence"]
        pass_rate = factors["validation_pass_rate"]
        evidence_str = "present" if result.evidence else "absent"
        explanation = (
            f"Score {score:.2f} based on agent confidence"
            f" ({agent_conf:.2f}), validation pass rate"
            f" ({pass_rate:.2f}), evidence ({evidence_str})"
        )

        return ConfidenceScore(score=score, factors=factors, explanation=explanation)
