"""Causal + organic capture acceptance (Tests I / J skeleton)."""

from __future__ import annotations

from pathlib import Path

from dimensional_agent.product.clean_room_bank import CleanRoomBank
from dimensional_agent.product.guidance_api import guidance_recall
from dimensional_agent.product.reference_agent import (
    apply_explicit_memory_command,
    run_turn,
)


def _stub_model(prompt: str) -> str:
    # Observable: mentions approval if guidance present
    if "Never deploy" in prompt or "production-approval" in prompt:
        return "REFUSING_DEPLOY_NEEDS_APPROVAL"
    return "GENERIC_OK"


def test_organic_capture_survives_restart(tmp_path: Path) -> None:
    root = tmp_path / "bank"
    bank = CleanRoomBank(root)
    apply_explicit_memory_command(
        bank,
        command="never",
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval.",
    )
    apply_explicit_memory_command(
        bank,
        command="remember",
        key="style.short",
        content="Keep answers short and plain.",
    )
    # Restart = new bank object same path
    bank2 = CleanRoomBank(root)
    assert len(bank2.all_records()) == 2
    out = guidance_recall(bank2, query="deploy production")
    assert out["hits"][0]["key"] == "deployment.production-approval"

    apply_explicit_memory_command(
        bank2,
        command="replace",
        key="deployment.production-approval",
        content="Deploy only with written ticket approval.",
    )
    bank3 = CleanRoomBank(root)
    out2 = guidance_recall(bank3, query="deploy production")
    assert "written ticket" in out2["hits"][0]["content"]
    assert len([r for r in bank3.all_records() if r.status == "active"]) == 2


def test_causal_treatment_vs_control(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    apply_explicit_memory_command(
        bank,
        command="never",
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval.",
    )
    task = "Please deploy to production now."
    control = _stub_model(f"You are a careful coding agent.\n\nUser: {task}\nAssistant:")
    treatment = run_turn(bank, user_text=task, model_fn=_stub_model)
    assert control == "GENERIC_OK"
    assert treatment["answer"] == "REFUSING_DEPLOY_NEEDS_APPROVAL"
    assert treatment["record_ids"]
