"""Tests for the GroundingChecker."""

from vectraxis.models.validation import ValidationStatus
from vectraxis.validation.grounding import GroundingChecker


class TestGroundingChecker:
    def test_grounding_passes_with_evidence(self) -> None:
        checker = GroundingChecker()
        output = "The workflow data shows significant improvement in processing speed"
        evidence = [
            "workflow data shows improvement",
            "processing speed increased by 20%",
        ]
        result = checker.check(output, evidence)
        assert result.status == ValidationStatus.PASSED

    def test_grounding_fails_without_matching_evidence(self) -> None:
        checker = GroundingChecker()
        output = "completely unrelated text about something else entirely"
        evidence = [
            "xylophone quantum zebra mechanics",
            "phosphorescent kaleidoscope entropy",
        ]
        result = checker.check(output, evidence)
        assert result.status == ValidationStatus.FAILED

    def test_grounding_warns_no_evidence(self) -> None:
        checker = GroundingChecker()
        result = checker.check("some output text", [])
        assert result.status == ValidationStatus.WARNING

    def test_grounding_details_have_ratio(self) -> None:
        checker = GroundingChecker()
        output = "The workflow data shows improvement"
        evidence = ["workflow data shows improvement"]
        result = checker.check(output, evidence)
        assert "grounding_ratio" in result.details
