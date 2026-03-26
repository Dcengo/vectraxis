"""Benchmark runner for evaluating pipeline results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectraxis.models.evaluation import BenchmarkRun

if TYPE_CHECKING:
    from vectraxis.evaluation.metrics import Metric


class BenchmarkRunner:
    """Runs a set of metrics on pipeline results and returns a BenchmarkRun."""

    def __init__(self, metrics: list[Metric]) -> None:
        self._metrics = metrics

    def run(
        self,
        name: str,
        results: dict[str, object],
        config: dict[str, object] | None = None,
    ) -> BenchmarkRun:
        metric_results = []
        for metric in self._metrics:
            try:
                result = metric.compute(**results)
                metric_results.append(result)
            except TypeError:
                # Metric doesn't accept these kwargs, skip
                pass
        return BenchmarkRun(
            name=name,
            metrics=metric_results,
            config=config or {},
        )
