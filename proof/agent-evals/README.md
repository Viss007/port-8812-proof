# Real-agent eval protocol (not retrieval accuracy)

This folder is the **integration** eval, not the recall benchmark.

Port 8812 does not intercept Cursor. An agent only recalls if it calls `guidance_recall`.
Obedience is the model. Do not mix those numbers with top-1 retrieval.

## Status

`NOT PROVED` for a live Cursor / Grok / ChatGPT coding agent until `runs.jsonl`
contains real session observations.

This stock Cursor parent talks to desk memory on `:8811`, not the people product
on `:8812`. Do not treat desk `pre_hook` as product evidence.

The 20-task causal suite in `test_causal_eval_suite.py` uses a **STUB** model.
It is not this eval.

## How to run later

1. Fresh Cursor chat with only the four product MCP tools (copy `mcp.example.json`).
2. Paste `docs/AGENT-INTEGRATION.md` as the generic instruction. No planted locks.
3. Isolated demo bank. Commit the locks listed in `tasks.json` first via CLI.
4. For each task, record A–F in `runs.jsonl`.
5. Recompute `summary.json` from the file. No film. No invented rows.
