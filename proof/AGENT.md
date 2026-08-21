# Agent prompt — audit PORT 8812 Proof v4 / release 1.0.0

You are checking whether Port 8812 v1.0.0 is a real local Continuity product (CORE + Agent Kit + proof), not a filmed demo.

Read `AUDIT.md`, `CLAIMS.json`, `run.json`, and `core-v4/RELEASE.md` first.

## Required checks

1. `core-v4/VERSION` == `1.0.0` and `core-v4/receipts/freeze.txt` lists product_acceptance=53 passed.
2. `core-v4/receipts/product_acceptance-53.txt` ends with `53 passed`.
3. `core-v4/receipts/setup_health.json` — `product_port` 8812, `not_desk_port` 8811, `build_compare.stale` false (or explains restart), HTTP labeled debug-only.
4. `core-v3/reports/blind.json` — FP 0/35, misses 0/15, determinism true (earned earlier; still valid).
5. `core-v3/ranker_config.json` — llm false; embeddings_required false; Windows Search recommended ignore.
6. `core-v4/receipts/agent_use_qualitative.json` — `eur49_software_verdict` YES and explicitly **not** a universal guarantee.
7. `CLAIMS.json` — every `status:proved` receipt path exists; withdrawn rows stay withdrawn.
8. Buyer path claims mention `8812-product` and `:8812`, not desk `pre_hook` as normal operation.

Report: PROVED / KNOWN LIMITS / NOT PROVED.

FAIL if this folder is used to justify 120 real-model calls, 90% Cursor recall, embeddings earned, Windows Search retrieval, or forced obedience.
