"""Tests for evaluation metrics (Phase 6 - Red phase first)."""

import pytest

from vectraxis.evaluation.metrics import (
    AnswerFaithfulness,
    LatencyMetric,
    Metric,
    ResponseCompleteness,
    RetrievalRelevance,
    TokenCostMetric,
)
from vectraxis.models.evaluation import MetricType
from vectraxis.models.retrieval import Chunk, SearchResult


def make_search_result(
    content: str = "test content",
    score: float = 0.9,
) -> SearchResult:
    chunk = Chunk(document_id="doc-1", content=content, index=0)
    return SearchResult(chunk=chunk, score=score)


# === RetrievalRelevance ===


class TestRetrievalRelevance:
    def test_retrieval_relevance_implements_protocol(self):
        metric = RetrievalRelevance()
        assert isinstance(metric, Metric)

    def test_retrieval_relevance_metric_type(self):
        metric = RetrievalRelevance()
        assert metric.metric_type == MetricType.RETRIEVAL_RELEVANCE

    def test_retrieval_relevance_computes_avg_score(self):
        metric = RetrievalRelevance()
        results = [
            make_search_result(score=0.8),
            make_search_result(score=0.6),
            make_search_result(score=1.0),
        ]
        result = metric.compute(query="test query", results=results)
        assert result.value == pytest.approx(0.8)

    def test_retrieval_relevance_empty_results(self):
        metric = RetrievalRelevance()
        result = metric.compute(query="test query", results=[])
        assert result.value == 0.0

    def test_retrieval_relevance_metadata_has_num_results(self):
        metric = RetrievalRelevance()
        results = [
            make_search_result(score=0.9),
            make_search_result(score=0.7),
        ]
        result = metric.compute(query="test query", results=results)
        assert result.metadata["num_results"] == 2


# === AnswerFaithfulness ===


class TestAnswerFaithfulness:
    def test_answer_faithfulness_implements_protocol(self):
        metric = AnswerFaithfulness()
        assert isinstance(metric, Metric)

    def test_answer_faithfulness_metric_type(self):
        metric = AnswerFaithfulness()
        assert metric.metric_type == MetricType.ANSWER_FAITHFULNESS

    def test_answer_faithfulness_high_overlap(self):
        metric = AnswerFaithfulness()
        answer = "the cat sat on the mat"
        context = ["the cat sat on the mat in the room"]
        result = metric.compute(answer=answer, context=context)
        assert result.value == pytest.approx(1.0)

    def test_answer_faithfulness_no_context(self):
        metric = AnswerFaithfulness()
        result = metric.compute(answer="some answer", context=[])
        assert result.value == 0.0

    def test_answer_faithfulness_no_overlap(self):
        metric = AnswerFaithfulness()
        answer = "alpha beta gamma"
        context = ["completely different words here"]
        result = metric.compute(answer=answer, context=context)
        assert result.value == pytest.approx(0.0)


# === ResponseCompleteness ===


class TestResponseCompleteness:
    def test_response_completeness_implements_protocol(self):
        metric = ResponseCompleteness()
        assert isinstance(metric, Metric)

    def test_response_completeness_all_topics_found(self):
        metric = ResponseCompleteness()
        response = "This covers machine learning and deep learning topics."
        expected_topics = ["machine learning", "deep learning"]
        result = metric.compute(response=response, expected_topics=expected_topics)
        assert result.value == pytest.approx(1.0)

    def test_response_completeness_partial_topics(self):
        metric = ResponseCompleteness()
        response = "This covers machine learning only."
        expected_topics = ["machine learning", "deep learning"]
        result = metric.compute(response=response, expected_topics=expected_topics)
        assert result.value == pytest.approx(0.5)

    def test_response_completeness_no_topics_expected(self):
        metric = ResponseCompleteness()
        result = metric.compute(response="anything", expected_topics=[])
        assert result.value == pytest.approx(1.0)

    def test_response_completeness_metadata(self):
        metric = ResponseCompleteness()
        response = "This covers machine learning only."
        expected_topics = ["machine learning", "deep learning"]
        result = metric.compute(response=response, expected_topics=expected_topics)
        assert result.metadata["found"] == 1
        assert result.metadata["total"] == 2


# === LatencyMetric ===


class TestLatencyMetric:
    def test_latency_metric_type(self):
        metric = LatencyMetric()
        assert metric.metric_type == MetricType.LATENCY

    def test_latency_compute(self):
        metric = LatencyMetric()
        result = metric.compute(duration_seconds=1.5)
        assert result.value == pytest.approx(1.5)

    def test_latency_metadata_has_unit(self):
        metric = LatencyMetric()
        result = metric.compute(duration_seconds=2.0)
        assert result.metadata["unit"] == "seconds"


# === TokenCostMetric ===


class TestTokenCostMetric:
    def test_token_cost_metric_type(self):
        metric = TokenCostMetric()
        assert metric.metric_type == MetricType.TOKEN_COST

    def test_token_cost_compute(self):
        metric = TokenCostMetric()
        result = metric.compute(input_tokens=1000, output_tokens=500)
        # (1000/1000)*0.001 + (500/1000)*0.002 = 0.002
        assert result.value == pytest.approx(0.002)
        assert result.metadata["input_tokens"] == 1000
        assert result.metadata["output_tokens"] == 500

    def test_token_cost_with_custom_rates(self):
        metric = TokenCostMetric()
        result = metric.compute(
            input_tokens=2000,
            output_tokens=1000,
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.03,
        )
        # (2000/1000)*0.01 + (1000/1000)*0.03 = 0.05
        assert result.value == pytest.approx(0.05)
