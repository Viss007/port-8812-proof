# CORE Proof v3 — guidance relevance / abstention

Synthetic fixtures and score receipts for the CORE guidance ranker.
No private desk notes. No embeddings. No Windows Search retrieval.

## Verify quickly

1. `hashes.json` digests match `datasets/*` (SHA-256).
2. `datasets/blind_expected.json` was frozen **before** scoring (`blind_frozen_before_scoring: true`).
3. `reports/blind.json` → negatives FP **0/35**, positives misses **0/15**, `determinism: true`.
4. `reports/error_analysis.json` is the **old held-out** reclassified after use — not a clean validation set.
5. `reports/original_AFTER.json` → top-1 **0.941**; known abstention `pos-style-001`.
6. `../receipts/pytest-product_acceptance-21.txt` → **21 passed**.
7. `ranker_config.json` → method `idf_plus_min_exact_support_abstention`, `llm_in_ranker: false`, no benchmark phrase hacks.

Parent pack docs: `../AUDIT.md`, `../AGENT.md`, `../CLAIMS.json`, `../run.json`.
