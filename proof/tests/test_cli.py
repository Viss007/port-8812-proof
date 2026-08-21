"""CLI ownership smoke."""

from __future__ import annotations

from pathlib import Path

from dimensional_agent.product import cli


def test_cli_health_list_backup_restore(tmp_path: Path, monkeypatch) -> None:
    bank_root = tmp_path / "demo-cli"
    monkeypatch.setenv("VISSAI_GUIDANCE_BANK_PATH", str(bank_root))
    from dimensional_agent.product.bank_path import reset_product_bank_cache
    from dimensional_agent.product.guidance_api import guidance_commit
    from dimensional_agent.product.clean_room_bank import CleanRoomBank

    reset_product_bank_cache()
    bank = CleanRoomBank(bank_root, role="demo")
    c = guidance_commit(bank, key="style.short", content="Keep answers short and plain.")
    rid = c["record"]["record_id"]
    assert cli.main(["health"]) == 0
    assert cli.main(["list", "--active"]) == 0
    assert cli.main(["show", rid]) == 0
    bak = tmp_path / "b.json"
    assert cli.main(["backup", str(bak)]) == 0
    assert bak.exists()
    assert cli.main(["reset", "--demo-confirm"]) == 0
    assert cli.main(["restore", str(bak)]) == 0
    assert cli.main(["path"]) == 0
