"""TDD tests for vectraxis.models.evaluation module.

Tests define the API contract for:
- MetricType enum
- MetricResult model
- BenchmarkRun model
- ExperimentConfig model
"""

import pytest
from pydantic import ValidationError

from vectraxis.models.common import VectraxisModel, generate_id
from vectraxis.models.evaluation import (
    BenchmarkRun,
    ExperimentConfig,
    MetricResult,
    MetricType,
)

# --- MetricType ---


class TestMetricType:
    """Tests for the MetricType enum."""

    def test_has_retrieval_relevance(self):
        assert MetricType.RETRIEVAL_RELEVANCE is not None

    def test_has_answer_faithfulness(self):
        assert MetricType.ANSWER_FAITHFULNESS is not None

    def test_has_response_completeness(self):
        assert MetricType.RESPONSE_COMPLETENESS is not None

    def test_has_latency(self):
        assert MetricType.LATENCY is not None

    def test_has_token_cost(self):
        assert MetricType.TOKEN_COST is not None

    def test_has_exactly_five_values(self):
        assert len(MetricType) == 5

    def test_values_are_strings(self):
        for m in MetricType:
            assert isinstance(m.value, str)


# --- MetricResult ---


class TestMetricResult:
    """Tests for the MetricResult model."""

    def test_create_with_required_fields(self):
        mr = MetricResult(
            metric_type=MetricType.RETRIEVAL_RELEVANCE,
            value=0.92,
        )
        assert mr.metric_type == MetricType.RETRIEVAL_RELEVANCE
        assert mr.value == 0.92

    def test_metadata_defaults_to_empty_dict(self):
        mr = MetricResult(
            metric_type=MetricType.LATENCY,
            value=150.0,
        )
        assert mr.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"unit": "ms", "percentile": "p99"}
        mr = MetricResult(
            metric_type=MetricType.LATENCY,
            value=200.0,
            metadata=meta,
        )
        assert mr.metadata == meta

    def test_value_is_float(self):
        mr = MetricResult(
            metric_type=MetricType.TOKEN_COST,
            value=0.003,
        )
        assert isinstance(mr.value, float)

    def test_value_can_be_negative(self):
        """Some metrics (like deltas) could be negative."""
        mr = MetricResult(
            metric_type=MetricType.LATENCY,
            value=-10.0,
        )
        assert mr.value == -10.0

    def test_value_can_be_zero(self):
        mr = MetricResult(
            metric_type=MetricType.TOKEN_COST,
            value=0.0,
        )
        assert mr.value == 0.0

    def test_requires_metric_type(self):
        with pytest.raises(ValidationError):
            MetricResult(value=0.5)

    def test_requires_value(self):
        with pytest.raises(ValidationError):
            MetricResult(metric_type=MetricType.RETRIEVAL_RELEVANCE)

    def test_invalid_metric_type_raises(self):
        with pytest.raises(ValidationError):
            MetricResult(metric_type="INVALID", value=0.5)

    def test_all_metric_types_accepted(self):
        for mt in MetricType:
            mr = MetricResult(metric_type=mt, value=1.0)
            assert mr.metric_type == mt

    def test_serialization(self):
        mr = MetricResult(
            metric_type=MetricType.ANSWER_FAITHFULNESS,
            value=0.88,
            metadata={"model": "gpt-4"},
        )
        data = mr.model_dump()
        assert data["value"] == 0.88
        assert data["metadata"] == {"model": "gpt-4"}

    def test_is_vectraxis_model(self):
        assert issubclass(MetricResult, VectraxisModel)


# --- BenchmarkRun ---


class TestBenchmarkRun:
    """Tests for the BenchmarkRun model."""

    def test_create_with_required_fields(self):
        br = BenchmarkRun(
            id=generate_id(),
            name="retrieval_benchmark_v1",
        )
        assert br.name == "retrieval_benchmark_v1"

    def test_metrics_defaults_to_empty_list(self):
        br = BenchmarkRun(id=generate_id(), name="bench")
        assert br.metrics == []

    def test_metrics_can_be_set(self):
        metrics = [
            MetricResult(metric_type=MetricType.RETRIEVAL_RELEVANCE, value=0.9),
            MetricResult(metric_type=MetricType.LATENCY, value=120.0),
        ]
        br = BenchmarkRun(id=generate_id(), name="bench", metrics=metrics)
        assert len(br.metrics) == 2
        assert br.metrics[0].value == 0.9

    def test_config_defaults_to_empty_dict(self):
        br = BenchmarkRun(id=generate_id(), name="bench")
        assert br.config == {}

    def test_config_can_be_set(self):
        config = {"top_k": 10, "threshold": 0.7}
        br = BenchmarkRun(id=generate_id(), name="bench", config=config)
        assert br.config == config

    def test_requires_name(self):
        with pytest.raises(ValidationError):
            BenchmarkRun(id=generate_id())

    def test_serialization(self):
        mr = MetricResult(metric_type=MetricType.TOKEN_COST, value=0.005)
        br = BenchmarkRun(
            id="br-1",
            name="cost_bench",
            metrics=[mr],
            config={"budget": 1.0},
        )
        data = br.model_dump()
        assert data["name"] == "cost_bench"
        assert len(data["metrics"]) == 1
        assert data["config"] == {"budget": 1.0}

    def test_is_vectraxis_model(self):
        assert issubclass(BenchmarkRun, VectraxisModel)


# --- ExperimentConfig ---


class TestExperimentConfig:
    """Tests for the ExperimentConfig model."""

    def test_create_with_required_fields(self):
        ec = ExperimentConfig(
            name="chunk_size_experiment",
            variations=[
                {"chunk_size": 256},
                {"chunk_size": 512},
                {"chunk_size": 1024},
            ],
        )
        assert ec.name == "chunk_size_experiment"
        assert len(ec.variations) == 3

    def test_base_config_defaults_to_empty_dict(self):
        ec = ExperimentConfig(name="exp", variations=[{"a": 1}])
        assert ec.base_config == {}

    def test_base_config_can_be_set(self):
        base = {"model": "gpt-4", "temperature": 0.7}
        ec = ExperimentConfig(
            name="exp",
            variations=[{"temp": 0.5}],
            base_config=base,
        )
        assert ec.base_config == base

    def test_variations_is_list_of_dicts(self):
        ec = ExperimentConfig(
            name="exp",
            variations=[{"k": "v1"}, {"k": "v2"}],
        )
        assert isinstance(ec.variations, list)
        assert all(isinstance(v, dict) for v in ec.variations)

    def test_requires_name(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(variations=[{"a": 1}])

    def test_requires_variations(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(name="exp")

    def test_serialization(self):
        ec = ExperimentConfig(
            name="test_exp",
            variations=[{"x": 1}, {"x": 2}],
            base_config={"base": True},
        )
        data = ec.model_dump()
        assert data["name"] == "test_exp"
        assert len(data["variations"]) == 2
        assert data["base_config"] == {"base": True}

    def test_is_vectraxis_model(self):
        assert issubclass(ExperimentConfig, VectraxisModel)
