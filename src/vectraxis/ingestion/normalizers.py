"""Normalizers that convert RawRecords into NormalizedRecords."""

from vectraxis.models.ingestion import NormalizedRecord, RawRecord


class WorkflowNormalizer:
    """Normalizes raw records into a standard format.

    - Records with a "content" key are treated as documents.
    - All other records are treated as workflow tasks and formatted as text.
    """

    def normalize(self, record: RawRecord) -> NormalizedRecord:
        if "content" in record.data and len(record.data) == 1:
            return self._normalize_document(record)
        return self._normalize_workflow_task(record)

    def _normalize_document(self, record: RawRecord) -> NormalizedRecord:
        return NormalizedRecord(
            source_id=record.source_id,
            content=record.data["content"],
            metadata={},
            record_type="document",
        )

    def _normalize_workflow_task(self, record: RawRecord) -> NormalizedRecord:
        parts: list[str] = []
        for key, value in record.data.items():
            parts.append(f"{key}: {value}")
        content = " | ".join(parts)

        return NormalizedRecord(
            source_id=record.source_id,
            content=content,
            metadata=dict(record.data),
            record_type="workflow_task",
        )
