"""Custom metrics for pipeline observability."""

import time
from dataclasses import dataclass, field


@dataclass
class PipelineMetrics:
    """Collects metrics for a pipeline run."""

    start_time: float = 0.0
    end_time: float = 0.0
    step_durations: dict[str, float] = field(default_factory=dict)
    token_counts: dict[str, int] = field(default_factory=dict)
    error_count: int = 0

    def start(self) -> None:
        self.start_time = time.monotonic()

    def stop(self) -> None:
        self.end_time = time.monotonic()

    @property
    def total_duration(self) -> float:
        if self.end_time <= 0 or self.start_time <= 0:
            return 0.0
        return self.end_time - self.start_time

    def record_step(self, step_name: str, duration: float) -> None:
        self.step_durations[step_name] = duration

    def record_tokens(self, step_name: str, count: int) -> None:
        self.token_counts[step_name] = count

    def record_error(self) -> None:
        self.error_count += 1

    def to_dict(self) -> dict[str, object]:
        return {
            "total_duration": self.total_duration,
            "step_durations": self.step_durations,
            "token_counts": self.token_counts,
            "error_count": self.error_count,
        }


class MetricsCollector:
    """Collects and aggregates pipeline metrics."""

    def __init__(self) -> None:
        self._runs: list[PipelineMetrics] = []

    def create_run(self) -> PipelineMetrics:
        metrics = PipelineMetrics()
        self._runs.append(metrics)
        return metrics

    @property
    def runs(self) -> list[PipelineMetrics]:
        return self._runs

    def summary(self) -> dict[str, object]:
        if not self._runs:
            return {"total_runs": 0, "avg_duration": 0.0, "total_errors": 0}
        total_duration = sum(r.total_duration for r in self._runs)
        return {
            "total_runs": len(self._runs),
            "avg_duration": total_duration / len(self._runs),
            "total_errors": sum(r.error_count for r in self._runs),
        }
