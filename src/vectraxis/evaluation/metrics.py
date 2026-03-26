"""Evaluation metrics for the Vectraxis pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from vectraxis.models.evaluation import MetricResult, MetricType

if TYPE_CHECKING:
    from vectraxis.models.retrieval import SearchResult


@runtime_checkable
class Metric(Protocol):
    @property
    def metric_type(self) -> MetricType: ...

    def compute(self, **kwargs: object) -> MetricResult: ...


class RetrievalRelevance:
    """Measures how relevant retrieved chunks are to the query."""

    metric_type = MetricType.RETRIEVAL_RELEVANCE

    def compute(
        self, query: str, results: list[SearchResult], **kwargs: object
    ) -> MetricResult:
        if not results:
            return MetricResult(metric_type=self.metric_type, value=0.0)
        avg_score = sum(r.score for r in results) / len(results)
        return MetricResult(
            metric_type=self.metric_type,
            value=avg_score,
            metadata={"num_results": len(results)},
        )


class AnswerFaithfulness:
    """Measures faithfulness of answer to context via word overlap."""

    metric_type = MetricType.ANSWER_FAITHFULNESS

    def compute(
        self, answer: str, context: list[str], **kwargs: object
    ) -> MetricResult:
        if not context:
            return MetricResult(metric_type=self.metric_type, value=0.0)
        answer_words = set(answer.lower().split())
        context_words = set(" ".join(context).lower().split())
        if not answer_words:
            return MetricResult(metric_type=self.metric_type, value=0.0)
        overlap = answer_words & context_words
        ratio = len(overlap) / len(answer_words)
        return MetricResult(
            metric_type=self.metric_type,
            value=ratio,
            metadata={"overlap_count": len(overlap)},
        )


class ResponseCompleteness:
    """Measures completeness of response based on expected keywords/topics."""

    metric_type = MetricType.RESPONSE_COMPLETENESS

    def compute(
        self, response: str, expected_topics: list[str], **kwargs: object
    ) -> MetricResult:
        if not expected_topics:
            return MetricResult(metric_type=self.metric_type, value=1.0)
        response_lower = response.lower()
        found = sum(1 for topic in expected_topics if topic.lower() in response_lower)
        ratio = found / len(expected_topics)
        return MetricResult(
            metric_type=self.metric_type,
            value=ratio,
            metadata={"found": found, "total": len(expected_topics)},
        )


class LatencyMetric:
    """Records pipeline latency."""

    metric_type = MetricType.LATENCY

    def compute(self, duration_seconds: float, **kwargs: object) -> MetricResult:
        return MetricResult(
            metric_type=self.metric_type,
            value=duration_seconds,
            metadata={"unit": "seconds"},
        )


class TokenCostMetric:
    """Records token cost."""

    metric_type = MetricType.TOKEN_COST

    def compute(
        self,
        input_tokens: int,
        output_tokens: int,
        cost_per_1k_input: float = 0.001,
        cost_per_1k_output: float = 0.002,
        **kwargs: object,
    ) -> MetricResult:
        total_cost = (input_tokens / 1000) * cost_per_1k_input + (
            output_tokens / 1000
        ) * cost_per_1k_output
        return MetricResult(
            metric_type=self.metric_type,
            value=total_cost,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )
