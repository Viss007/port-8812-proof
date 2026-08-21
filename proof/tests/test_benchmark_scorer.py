"""Benchmark scorer correctness — not a target accuracy."""

from __future__ import annotations

from pathlib import Path

from dimensional_agent.product.benchmark_data import queries, records
from dimensional_agent.product.benchmark_run import run


def test_benchmark_dataset_size() -> None:
    assert len(records()) >= 50
    assert len(queries()) >= 200
    ids = [q["id"] for q in queries()]
    assert len(ids) == len(set(ids))


def test_benchmark_scorer_runs(tmp_path: Path) -> None:
    result = run(tmp_path / "bench", repeats=3)
    s = result["summary"]
    assert s["n_queries"] >= 200
    assert s["llm_judge"] is False
    assert s["echo_query_ok"] is True
    assert s["determinism_fail_50x_first40"] == 0
    assert "top1_accuracy" in s
    assert "negative_fp_rate" in s
