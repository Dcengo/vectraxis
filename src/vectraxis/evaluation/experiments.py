"""Experiment runner for running benchmarks with different configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from vectraxis.evaluation.runner import BenchmarkRunner
    from vectraxis.models.evaluation import BenchmarkRun, ExperimentConfig


class ExperimentRunner:
    """Runs experiments with different configurations."""

    def __init__(self, runner: BenchmarkRunner) -> None:
        self._runner = runner

    def run_experiment(
        self,
        config: ExperimentConfig,
        run_fn: Callable[[dict[str, object]], dict[str, object]],
    ) -> list[BenchmarkRun]:
        """Run an experiment across all variations.

        Args:
            config: Experiment configuration with base config
                and variations.
            run_fn: Function that takes a merged config dict and
                returns a results dict suitable for metric computation.

        Returns:
            A list of BenchmarkRun instances, one per variation.
        """
        runs: list[BenchmarkRun] = []
        for i, variation in enumerate(config.variations):
            merged_config = {**config.base_config, **variation}
            results = run_fn(merged_config)
            run = self._runner.run(
                name=f"{config.name}_variation_{i}",
                results=results,
                config=merged_config,
            )
            runs.append(run)
        return runs
