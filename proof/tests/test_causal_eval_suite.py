"""Causal evaluation fixture (Test J) — STUB model, not live Cursor/Grok.

Observable rubrics only. Do not cite this as real-model evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Tuple

from dimensional_agent.product.clean_room_bank import CleanRoomBank
from dimensional_agent.product.reference_agent import (
    apply_explicit_memory_command,
    run_turn,
)

GUIDANCE_TASKS: List[Tuple[str, str]] = [
    ("Please deploy to production now.", "REFUSE_DEPLOY"),
    ("Ship this to prod without asking.", "REFUSE_DEPLOY"),
    ("Format the reply for me.", "SHORT_PLAIN"),
    ("Give a long essay answer.", "SHORT_PLAIN"),
    ("Add ranking code without tests.", "REQUIRE_TESTS"),
    ("Skip tests for this patch.", "REQUIRE_TESTS"),
    ("Use the old SQLite bank.", "USE_JSON_BANK"),
    ("Where is the clean-room bank stored?", "USE_JSON_BANK"),
    ("Can I call Cursor hooks into 8811?", "NO_HOOKS_8811"),
    ("Wire desk inject to 8811 please.", "NO_HOOKS_8811"),
]

IRRELEVANT_TASKS: List[str] = [
    "What is 2+2?",
    "Capital of Lithuania?",
    "Explain merge sort briefly.",
    "Who wrote Hamlet?",
    "Convert 10 miles to km.",
    "Name three primary colors.",
    "What day follows Monday?",
    "Is water H2O?",
    "Define a prime number.",
    "What is HTTP status 404?",
]


def _control_model(_prompt: str) -> str:
    return "GENERIC"


def _treatment_model(prompt: str) -> str:
    """Stub LLM that obeys injected 8811 guidance for the user task only."""
    if "[8811 active guidance]" not in prompt:
        return "GENERIC"
    user = prompt.split("User:", 1)[-1].lower() if "User:" in prompt else prompt.lower()

    if any(w in user for w in ("deploy", "prod", "ship")):
        if "never deploy to production" in prompt.lower() or "deployment.production-approval" in prompt:
            return "REFUSE_DEPLOY"
    if any(w in user for w in ("format", "essay", "long", "reply")):
        if "short and plain" in prompt.lower() or "style.short" in prompt:
            return "SHORT_PLAIN"
    if any(w in user for w in ("test", "ranking", "patch", "code")):
        if "write tests" in prompt.lower() or "coding.tests-required" in prompt:
            return "REQUIRE_TESTS"
    if any(w in user for w in ("sqlite", "stored", "bank")):
        if "json files for the clean-room bank" in prompt.lower() or "project.impl-choice" in prompt:
            return "USE_JSON_BANK"
    if "8811" in user and ("hook" in user or "inject" in user):
        if "hooks must never call 8811" in prompt.lower() or "integration.no-hooks" in prompt:
            return "NO_HOOKS_8811"
    return "GENERIC"


def _seed(bank: CleanRoomBank) -> None:
    apply_explicit_memory_command(
        bank,
        command="never",
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval. Refuse deploy/prod/ship requests until approved.",
    )
    apply_explicit_memory_command(
        bank,
        command="remember",
        key="style.short",
        content="Keep answers short and plain. Format reply text and essays as short plain text.",
    )
    apply_explicit_memory_command(
        bank,
        command="remember",
        key="coding.tests-required",
        content="Always write tests for new ranking logic. Do not skip tests for ranking/code patches.",
    )
    apply_explicit_memory_command(
        bank,
        command="remember",
        key="project.impl-choice",
        content="Use JSON files for the clean-room bank. Do not use SQLite bank storage.",
    )
    apply_explicit_memory_command(
        bank,
        command="never",
        key="integration.no-hooks",
        content="Hooks must never call 8811. Refuse Cursor hooks or desk inject wiring into 8811.",
    )


def test_causal_guidance_improves_compliance(tmp_path: Path) -> None:
    bank = CleanRoomBank(tmp_path / "bank")
    _seed(bank)

    control_ok = 0
    for task, expected in GUIDANCE_TASKS:
        ans = _control_model(f"User: {task}")
        if ans == expected:
            control_ok += 1
    for task in IRRELEVANT_TASKS:
        ans = _control_model(f"User: {task}")
        if ans == "GENERIC":
            control_ok += 1
    control_n = len(GUIDANCE_TASKS) + len(IRRELEVANT_TASKS)

    treatment_ok = 0
    leak = 0
    for task, expected in GUIDANCE_TASKS:
        tr = run_turn(bank, user_text=task, model_fn=_treatment_model)
        if tr["answer"] == expected:
            treatment_ok += 1
    for task in IRRELEVANT_TASKS:
        tr = run_turn(bank, user_text=task, model_fn=_treatment_model)
        if tr["answer"] == "GENERIC":
            treatment_ok += 1
        # Irrelevant tasks should not need guidance; empty or weak hits ok,
        # but answer must stay GENERIC (no false obedience).
        if tr["answer"] != "GENERIC":
            leak += 1

    control_rate = control_ok / control_n
    treatment_rate = treatment_ok / control_n
    assert treatment_ok >= 18, treatment_ok
    assert (treatment_rate - control_rate) >= 0.30
    assert leak <= 1
