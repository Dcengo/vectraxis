"""OpenTelemetry tracing configuration."""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TCH003

from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


class InMemorySpanExporter(SpanExporter):
    """In-memory span exporter for dev/test environments."""

    def __init__(self) -> None:
        self._spans: list[ReadableSpan] = []

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        self._spans.extend(spans)
        return SpanExportResult.SUCCESS

    def get_finished_spans(self) -> list[ReadableSpan]:
        return list(self._spans)

    def shutdown(self) -> None:
        self._spans.clear()

    def clear(self) -> None:
        self._spans.clear()


def setup_tracing(service_name: str = "vectraxis") -> TracerProvider:
    """Configure OpenTelemetry tracing with in-memory exporter for dev/test."""
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    return provider


def get_tracer(name: str = "vectraxis") -> trace.Tracer:
    """Get a tracer instance."""
    return trace.get_tracer(name)


def create_test_tracer() -> tuple[trace.Tracer, InMemorySpanExporter]:
    """Create a tracer with in-memory exporter for testing."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("vectraxis-test")
    return tracer, exporter
