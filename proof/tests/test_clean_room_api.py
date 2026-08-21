"""Clean-room API acceptance: empty bank, supersede via API, determinism."""

from __future__ import annotations

from pathlib import Path

from dimensional_agent.product.clean_room_bank import CleanRoomBank
from dimensional_agent.product.guidance_api import (
    guidance_commit,
    guidance_deactivate,
    guidance_health,
    guidance_recall,
)


def test_empty_bank_recall(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    out = guidance_recall(bank, query="anything")
    assert out["recall_status"] == "empty_bank"
    assert out["suggestion"] == "calibration_needed"
    assert out["hits"] == []


def test_commit_supersede_deactivate_cycle(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    c1 = guidance_commit(
        bank,
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval.",
        receipt="Never deploy without asking me first.",
    )
    id1 = c1["record"]["record_id"]
    c2 = guidance_commit(
        bank,
        key="deployment.production-approval",
        content="Deploy only after written ticket approval.",
        receipt="Replace: approval must be in the ticket.",
    )
    id2 = c2["record"]["record_id"]
    out = guidance_recall(bank, query="deploy production approval")
    assert out["recall_status"] == "ok"
    assert out["hits"][0]["record_id"] == id2
    assert id1 not in [h["record_id"] for h in out["hits"]]

    guidance_deactivate(bank, id2)
    out2 = guidance_recall(bank, query="deploy production approval")
    assert out2["recall_status"] == "empty_bank"


def test_determinism_repeat(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    guidance_commit(
        bank,
        key="style.short",
        content="Keep answers short and plain.",
        kind="taste",
    )
    guidance_commit(
        bank,
        key="risk.approval",
        content="Never deploy without approval.",
        kind="lock",
    )
    q = "deploy approval short answers"
    first = None
    for _ in range(50):
        out = guidance_recall(bank, query=q)
        ids = [h["record_id"] for h in out["hits"]]
        if first is None:
            first = ids
        assert ids == first


def test_health_surface(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    h = guidance_health(bank)
    assert h["status"] == "ok"
    assert h["llm_judgment"] is False
    assert h["surface"] == "8811.guidance.v1"
