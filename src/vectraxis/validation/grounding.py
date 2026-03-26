"""Grounding checker: verifies that claims are grounded in provided evidence."""

from __future__ import annotations

from vectraxis.models.validation import ValidationResult, ValidationStatus


class GroundingChecker:
    """Checks if claims in output are grounded in provided evidence."""

    def check(self, output: str, evidence: list[str]) -> ValidationResult:
        if not evidence:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="No evidence provided",
            )

        # Simple check: at least some evidence text appears in or relates to output
        output_lower = output.lower()
        grounded_count = sum(
            1
            for e in evidence
            if any(word in output_lower for word in e.lower().split() if len(word) > 3)
        )
        ratio = grounded_count / len(evidence) if evidence else 0

        if ratio >= 0.5:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="Output is grounded in evidence",
                details={"grounding_ratio": ratio},
            )
        return ValidationResult(
            status=ValidationStatus.FAILED,
            message="Output lacks grounding",
            details={"grounding_ratio": ratio},
        )
