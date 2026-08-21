"""Recall quality: negatives, query echo, inactive leak."""

from __future__ import annotations

from pathlib import Path

from dimensional_agent.product.clean_room_bank import CleanRoomBank
from dimensional_agent.product.guidance_api import guidance_commit, guidance_recall
from dimensional_agent.product.guidance_record import GuidanceRecord, GuidanceSource


def test_exact_query_preserved(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    guidance_commit(bank, key="style.short", content="Keep answers short and plain.")
    q = "Keep answers short and plain. Extra?"
    out = guidance_recall(bank, query=q)
    assert out["query"] == q


def test_negative_trivia_no_hits(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    guidance_commit(
        bank,
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval.",
    )
    out = guidance_recall(bank, query="What is 2+2?")
    assert out["hits"] == []
    assert out["recall_status"] in {"no_relevant_active_guidance", "empty_bank"}


def test_test_and_plan_meta_do_not_leak(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    probe = GuidanceRecord(
        key="k.test",
        content="Smoke probe smoke-abc must not rank",
        kind="lock",
        status="test",
        source=GuidanceSource(receipt="probe"),
    )
    meta = GuidanceRecord(
        key="k.plan",
        content="THIS WAKE leftover foo",
        kind="plan_meta",
        source=GuidanceSource(receipt="plan"),
    )
    real = GuidanceRecord(
        key="k.lock",
        content="Real lock about leftover foo ranking",
        kind="lock",
        source=GuidanceSource(receipt="real"),
    )
    bank.replace_all([probe, meta, real])
    out = guidance_recall(bank, query="leftover foo ranking")
    ids = [h["record_id"] for h in out["hits"]]
    assert real.record_id in ids
    assert probe.record_id not in ids
    assert meta.record_id not in ids


def test_mcp_four_tools_only() -> None:
    from dimensional_agent.product.mcp_server import _tools

    names = sorted(t["name"] for t in _tools())
    assert names == [
        "guidance_commit",
        "guidance_deactivate",
        "guidance_recall",
        "health",
    ]


def test_server_down_when_port_closed(monkeypatch) -> None:
    monkeypatch.setenv("VISS_PRODUCT_MCP_URL", "http://127.0.0.1:1/api/dimensional")
    from dimensional_agent.product.mcp_server import _http

    out = _http("health", {})
    assert out.get("error") == "server_down"
