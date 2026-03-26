"""Tests for pipeline metrics (Phase 8 - Red phase first)."""

import time

from vectraxis.observability.metrics import MetricsCollector, PipelineMetrics


class TestPipelineMetrics:
    def test_pipeline_metrics_initial_duration_zero(self):
        m = PipelineMetrics()
        assert m.total_duration == 0.0

    def test_pipeline_metrics_start_stop(self):
        m = PipelineMetrics()
        m.start()
        assert m.start_time > 0
        time.sleep(0.01)
        m.stop()
        assert m.end_time > m.start_time

    def test_pipeline_metrics_total_duration(self):
        m = PipelineMetrics()
        m.start()
        time.sleep(0.01)
        m.stop()
        assert m.total_duration > 0.0

    def test_pipeline_metrics_record_step(self):
        m = PipelineMetrics()
        m.record_step("retrieval", 0.5)
        assert m.step_durations["retrieval"] == 0.5

    def test_pipeline_metrics_record_tokens(self):
        m = PipelineMetrics()
        m.record_tokens("generation", 150)
        assert m.token_counts["generation"] == 150

    def test_pipeline_metrics_record_error(self):
        m = PipelineMetrics()
        assert m.error_count == 0
        m.record_error()
        assert m.error_count == 1
        m.record_error()
        assert m.error_count == 2

    def test_pipeline_metrics_to_dict(self):
        m = PipelineMetrics()
        m.record_step("ingestion", 0.3)
        m.record_tokens("ingestion", 100)
        m.record_error()
        result = m.to_dict()
        assert result["total_duration"] == 0.0
        assert result["step_durations"] == {"ingestion": 0.3}
        assert result["token_counts"] == {"ingestion": 100}
        assert result["error_count"] == 1


class TestMetricsCollector:
    def test_metrics_collector_create_run(self):
        collector = MetricsCollector()
        run = collector.create_run()
        assert isinstance(run, PipelineMetrics)

    def test_metrics_collector_runs_list(self):
        collector = MetricsCollector()
        r1 = collector.create_run()
        r2 = collector.create_run()
        assert len(collector.runs) == 2
        assert collector.runs[0] is r1
        assert collector.runs[1] is r2

    def test_metrics_collector_summary_empty(self):
        collector = MetricsCollector()
        summary = collector.summary()
        assert summary == {"total_runs": 0, "avg_duration": 0.0, "total_errors": 0}

    def test_metrics_collector_summary_with_runs(self):
        collector = MetricsCollector()
        r1 = collector.create_run()
        r1.start()
        time.sleep(0.01)
        r1.stop()
        r1.record_error()

        r2 = collector.create_run()
        r2.start()
        time.sleep(0.01)
        r2.stop()

        summary = collector.summary()
        assert summary["total_runs"] == 2
        assert summary["avg_duration"] > 0.0
        assert summary["total_errors"] == 1
