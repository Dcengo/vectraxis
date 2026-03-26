"""Tests for OpenTelemetry tracing configuration (Phase 8 - Red phase first)."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from vectraxis.observability.tracing import (
    InMemorySpanExporter,
    create_test_tracer,
    get_tracer,
    setup_tracing,
)


class TestSetupTracing:
    def test_setup_tracing_returns_provider(self):
        provider = setup_tracing("vectraxis-test")
        assert isinstance(provider, TracerProvider)

    def test_get_tracer_returns_tracer(self):
        setup_tracing("vectraxis-test")
        tracer = get_tracer("vectraxis-test")
        assert tracer is not None
        assert isinstance(tracer, trace.Tracer)


class TestCreateTestTracer:
    def test_create_test_tracer_returns_tuple(self):
        tracer, exporter = create_test_tracer()
        assert isinstance(tracer, trace.Tracer)
        assert isinstance(exporter, InMemorySpanExporter)

    def test_test_tracer_records_spans(self):
        tracer, exporter = create_test_tracer()
        with tracer.start_as_current_span("test-span"):
            pass
        spans = exporter.get_finished_spans()
        assert len(spans) == 1

    def test_span_has_name(self):
        tracer, exporter = create_test_tracer()
        with tracer.start_as_current_span("my-operation"):
            pass
        spans = exporter.get_finished_spans()
        assert spans[0].name == "my-operation"
