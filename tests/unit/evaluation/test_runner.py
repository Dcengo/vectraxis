"""Tests for BenchmarkRunner (Phase 6)."""

from vectraxis.evaluation.metrics import (
    LatencyMetric,
    RetrievalRelevance,
)
from vectraxis.evaluation.runner import BenchmarkRunner
from vectraxis.models.evaluation import MetricType
from vectraxis.models.retrieval import Chunk, SearchResult


def make_search_result(
    content: str = "test content",
    score: float = 0.9,
) -> SearchResult:
    chunk = Chunk(document_id="doc-1", content=content, index=0)
    return SearchResult(chunk=chunk, score=score)


class TestBenchmarkRunner:
    def test_benchmark_runner_creates_run(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        run = runner.run(name="test-run", results={"duration_seconds": 1.0})
        assert run is not None
        assert run.name == "test-run"

    def test_benchmark_runner_includes_metrics(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        run = runner.run(name="test-run", results={"duration_seconds": 1.0})
        assert len(run.metrics) == 1
        assert run.metrics[0].metric_type == MetricType.LATENCY

    def test_benchmark_runner_sets_name(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        run = runner.run(
            name="my-benchmark",
            results={"duration_seconds": 0.5},
        )
        assert run.name == "my-benchmark"

    def test_benchmark_runner_sets_config(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        run = runner.run(
            name="test-run",
            results={"duration_seconds": 1.0},
            config={"model": "gpt-4"},
        )
        assert run.config == {"model": "gpt-4"}

    def test_benchmark_runner_skips_incompatible_metrics(self):
        """RetrievalRelevance needs query+results.

        Passing only duration_seconds should skip it.
        """
        runner = BenchmarkRunner(metrics=[RetrievalRelevance(), LatencyMetric()])
        run = runner.run(name="test-run", results={"duration_seconds": 1.0})
        # Only LatencyMetric should produce a result
        assert len(run.metrics) == 1
        assert run.metrics[0].metric_type == MetricType.LATENCY
