"""Durable past vs newer unrelated (Test D) + plan-meta via API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from dimensional_agent.product.clean_room_bank import CleanRoomBank
from dimensional_agent.product.guidance_api import guidance_commit, guidance_recall
from dimensional_agent.product.guidance_record import GuidanceRecord, GuidanceSource


def test_durable_past_beats_unrelated_recent(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    old = (datetime.now(timezone.utc) - timedelta(days=90)).replace(microsecond=0)
    old_iso = old.isoformat().replace("+00:00", "Z")
    recent = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )

    coding = GuidanceRecord(
        key="coding.tests-required",
        content="Always write tests for new ranking logic.",
        kind="standard",
        durability="durable",
        effective_at=old_iso,
        updated_at=old_iso,
        source=GuidanceSource(receipt="Always write tests for ranking changes."),
    )
    chatter = GuidanceRecord(
        key="project.ui-color",
        content="Try a blue button on the settings page this afternoon.",
        kind="project_state",
        effective_at=recent,
        updated_at=recent,
        source=GuidanceSource(receipt="Blue button today."),
    )
    bank.replace_all([coding, chatter])

    out = guidance_recall(bank, query="how should we change ranking logic tests")
    assert out["hits"][0]["key"] == "coding.tests-required"
    assert out["hits"][0]["record_id"] == coding.record_id


def test_same_key_newer_project_state_wins(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    guidance_commit(
        bank,
        key="project.impl-choice",
        content="Use SQLite for the clean-room bank.",
        kind="project_state",
    )
    guidance_commit(
        bank,
        key="project.impl-choice",
        content="Use JSON files for the clean-room bank.",
        kind="project_state",
    )
    out = guidance_recall(bank, query="clean-room bank storage choice")
    assert "JSON files" in out["hits"][0]["content"]
