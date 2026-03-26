"""Tests for ExperimentRunner (Phase 6)."""

from vectraxis.evaluation.experiments import ExperimentRunner
from vectraxis.evaluation.metrics import LatencyMetric
from vectraxis.evaluation.runner import BenchmarkRunner
from vectraxis.models.evaluation import ExperimentConfig


class TestExperimentRunner:
    def test_experiment_runner_runs_variations(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        experiment_runner = ExperimentRunner(runner)
        config = ExperimentConfig(
            name="latency-test",
            variations=[{"speed": "fast"}, {"speed": "slow"}],
            base_config={"model": "gpt-4"},
        )

        def run_fn(cfg: dict) -> dict:
            duration = 0.5 if cfg["speed"] == "fast" else 2.0
            return {"duration_seconds": duration}

        runs = experiment_runner.run_experiment(config, run_fn)
        assert len(runs) == 2

    def test_experiment_runner_names_variations(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        experiment_runner = ExperimentRunner(runner)
        config = ExperimentConfig(
            name="exp",
            variations=[{"a": 1}, {"a": 2}],
        )

        def run_fn(cfg: dict) -> dict:
            return {"duration_seconds": 1.0}

        runs = experiment_runner.run_experiment(config, run_fn)
        assert runs[0].name == "exp_variation_0"
        assert runs[1].name == "exp_variation_1"

    def test_experiment_runner_merges_config(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        experiment_runner = ExperimentRunner(runner)
        config = ExperimentConfig(
            name="merge-test",
            variations=[{"override": "yes"}],
            base_config={
                "base_key": "base_val",
                "override": "no",
            },
        )

        captured_configs: list[dict] = []

        def run_fn(cfg: dict) -> dict:
            captured_configs.append(cfg)
            return {"duration_seconds": 1.0}

        experiment_runner.run_experiment(config, run_fn)
        # Variation should override base_config
        assert captured_configs[0]["override"] == "yes"
        assert captured_configs[0]["base_key"] == "base_val"

    def test_experiment_runner_returns_list_of_runs(self):
        runner = BenchmarkRunner(metrics=[LatencyMetric()])
        experiment_runner = ExperimentRunner(runner)
        config = ExperimentConfig(
            name="list-test",
            variations=[{"x": 1}, {"x": 2}, {"x": 3}],
        )

        def run_fn(cfg: dict) -> dict:
            return {"duration_seconds": 0.1}

        runs = experiment_runner.run_experiment(config, run_fn)
        assert isinstance(runs, list)
        assert len(runs) == 3
        for run in runs:
            assert len(run.metrics) == 1
