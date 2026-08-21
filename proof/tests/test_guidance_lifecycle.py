"""Product acceptance: structured lifecycle (Tests C, E, F, G, H core)."""

from __future__ import annotations

from dimensional_agent.product.guidance_record import (
    GuidanceRecord,
    GuidanceSource,
    apply_retract,
    apply_supersede,
    filter_active_guidance,
)


def test_explicit_supersede_removes_old_from_active() -> None:
    r1 = GuidanceRecord(
        key="deployment.production-approval",
        content="Never deploy to production without explicit approval.",
        kind="lock",
        source=GuidanceSource(receipt="Never deploy without asking me first."),
    )
    r2 = GuidanceRecord(
        key="deployment.production-approval",
        content="Deploy to production only after written approval in the ticket.",
        kind="lock",
        source=GuidanceSource(receipt="Replace: approval must be in the ticket."),
    )
    bank = apply_supersede([r1], new_record=r2)
    by_id = {r.record_id: r for r in bank}
    assert by_id[r1.record_id].status == "superseded"
    assert by_id[r2.record_id].status == "active"
    assert r2.supersedes == r1.record_id
    active = filter_active_guidance(bank)
    assert [r.record_id for r in active] == [r2.record_id]


def test_retract_removes_from_active() -> None:
    r1 = GuidanceRecord(key="k", content="A", kind="lock")
    r2 = GuidanceRecord(key="k", content="B", kind="lock")
    bank = apply_supersede([r1], new_record=r2)
    bank = apply_retract(bank, r2.record_id)
    assert filter_active_guidance(bank) == []


def test_plan_meta_excluded_from_normal_guidance() -> None:
    lock = GuidanceRecord(key="k.lock", content="Real lock", kind="lock")
    meta = GuidanceRecord(
        key="k.plan",
        content="THIS WAKE build sequence leftover=foo",
        kind="plan_meta",
        status="active",
    )
    active = filter_active_guidance([lock, meta])
    assert [r.record_id for r in active] == [lock.record_id]


def test_test_status_excluded() -> None:
    real = GuidanceRecord(key="k", content="Real", kind="lock")
    probe = GuidanceRecord(
        key="k.test",
        content="Smoke probe smoke-abc",
        kind="lock",
        status="test",
    )
    active = filter_active_guidance([real, probe])
    assert [r.record_id for r in active] == [real.record_id]


def test_dead_superseded_excluded_even_if_semantically_perfect() -> None:
    old = GuidanceRecord(
        key="deploy",
        content="Never deploy to production without explicit approval.",
        kind="lock",
    )
    new = GuidanceRecord(
        key="deploy",
        content="Never deploy to production without explicit approval. Always.",
        kind="lock",
    )
    bank = apply_supersede([old], new_record=new)
    active = filter_active_guidance(bank)
    assert len(active) == 1
    assert active[0].record_id == new.record_id


def test_empty_active_bank() -> None:
    assert filter_active_guidance([]) == []
