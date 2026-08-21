"""Bank reliability: atomic writes, races, corruption, stress."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from dimensional_agent.product.clean_room_bank import BankCorruptError, CleanRoomBank
from dimensional_agent.product.guidance_api import (
    guidance_commit,
    guidance_deactivate,
    guidance_recall,
)
from dimensional_agent.product.guidance_record import filter_active_guidance


def test_atomic_write_leaves_valid_json(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    guidance_commit(bank, key="a.lock", content="Alpha lock text here.")
    raw = bank.path.read_text(encoding="utf-8")
    json.loads(raw)
    assert '"schema": "8811.clean_room.v1"' in raw
    assert bank.bak_path.exists()


def test_concurrent_commits_same_key_one_active(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")

    def one(i: int) -> str:
        out = guidance_commit(
            bank,
            key="shared.lock",
            content=f"Version {i} of the shared lock content.",
        )
        return out["record"]["record_id"]

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(one, i) for i in range(40)]
        ids = [f.result() for f in as_completed(futs)]
    assert len(ids) == 40
    active = filter_active_guidance(bank.all_records())
    shared = [r for r in active if r.key == "shared.lock"]
    assert len(shared) == 1
    json.loads(bank.path.read_text(encoding="utf-8"))


def test_concurrent_commit_and_deactivate(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    first = guidance_commit(
        bank, key="race.lock", content="Initial race lock content."
    )
    rid = first["record"]["record_id"]

    def commit_new() -> None:
        guidance_commit(bank, key="race.lock", content="Replacement race lock content.")

    def deactivate_old() -> None:
        guidance_deactivate(bank, rid)

    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(commit_new)
        f2 = ex.submit(deactivate_old)
        f1.result()
        f2.result()
    json.loads(bank.path.read_text(encoding="utf-8"))
    active = [r for r in filter_active_guidance(bank.all_records()) if r.key == "race.lock"]
    assert len(active) <= 1


def test_truncated_file_recovers_from_bak(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    guidance_commit(bank, key="keep.lock", content="Must survive truncation of the live file.")
    assert bank.bak_path.exists()
    bank.path.write_text("{not json", encoding="utf-8")
    bank2 = CleanRoomBank(tmp_path / "bank")
    recs = bank2.all_records()
    assert any(r.key == "keep.lock" for r in recs)
    assert bank2.recovered_from_backup


def test_malformed_without_bak_raises(tmp_path: Path) -> None:
    root = tmp_path / "bank"
    bank = CleanRoomBank(root, role="demo")
    bank.path.write_text("{broken", encoding="utf-8")
    if bank.bak_path.exists():
        bank.bak_path.unlink()
    with pytest.raises(BankCorruptError):
        CleanRoomBank(root).all_records()


def test_backup_restore_roundtrip(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")
    c = guidance_commit(bank, key="style.short", content="Keep answers short and plain.")
    rid = c["record"]["record_id"]
    dest = tmp_path / "export.json"
    bank.backup(dest)
    bank.replace_all([])
    assert bank.all_records() == []
    bank.restore(dest)
    assert bank.get(rid) is not None
    out = guidance_recall(bank, query="short plain answers")
    assert out["hits"][0]["record_id"] == rid


def test_demo_reset_refuses_real(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "real-bank", role="real")
    guidance_commit(bank, key="x.lock", content="Do not wipe this real bank.")
    with pytest.raises(PermissionError):
        bank.reset_demo()
    assert bank.all_records()


def test_demo_reset_ok(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "demo-bank", role="demo")
    guidance_commit(bank, key="x.lock", content="Wipeable demo lock content.")
    bank.reset_demo()
    assert bank.all_records() == []


def test_stress_1000_mixed_ops(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank", role="demo")

    def op(i: int) -> str:
        kind = i % 5
        if kind == 0:
            out = guidance_commit(
                bank,
                key=f"k.{i % 17}",
                content=f"Guidance body number {i} with enough words.",
            )
            return "commit:" + out["record"]["record_id"]
        if kind == 1:
            guidance_recall(bank, query="guidance body number enough words")
            return "recall"
        if kind == 2:
            guidance_commit(
                bank,
                key=f"k.{i % 17}",
                content=f"Supersede body number {i} with enough words.",
            )
            return "supersede"
        if kind == 3:
            recs = [r for r in bank.all_records() if r.status == "active"]
            if recs:
                guidance_deactivate(bank, recs[0].record_id)
                return "deactivate"
            return "deactivate_skip"
        guidance_recall(bank, query="unrelated astronomy pineapple 42")
        return "neg"

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(op, i) for i in range(1000)]
        results = [f.result() for f in as_completed(futs)]
    assert len(results) == 1000
    payload = json.loads(bank.path.read_text(encoding="utf-8"))
    assert isinstance(payload["records"], list)
    active = filter_active_guidance(bank.all_records())
    seen: dict[tuple[str, str, str], str] = {}
    for r in active:
        k = (r.key, r.scope.type, r.scope.id)
        assert k not in seen
        seen[k] = r.record_id
    q = "guidance body number enough words"
    first = None
    for _ in range(20):
        ids = [h["record_id"] for h in guidance_recall(bank, query=q)["hits"]]
        if first is None:
            first = ids
        assert ids == first
