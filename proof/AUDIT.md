# PORT 8812 — public audit v4 (proof-v4-20260819) · software release 1.0.0

Point an agent here: this folder is the proof pack. Not a screen recording.

**Frozen software release:** Port 8812 **v1.0.0** (`continuity-core`).  
Private product tip: `b20e192032c4f97737cd3e1776279253e1da4068` (tag `v1.0.0`).  
Buyer SKU: CORE engine + Agent Kit + docs/proof.

## What the product is

Local guidance bank for coding agents. Human buys → points an MCP agent at the repo → agent runs **`setup`** → human reloads MCP once if required → agent operates Continuity Loop.

Core promise: reduce agent amnesia; increase continuity. Not endless memory. Not enforcement. Not Cursor intercept.

- MCP **`8812-product`** on **`127.0.0.1:8812`** only (not desk `:8811`, not `pre_hook`)
- Ranking is code; prefer abstention over weak hits
- No embeddings / GPU / API key required for CORE

## PROVED (Proof v4 / release 1.0.0)

| Claim | Result | File |
|---|---|---|
| product_acceptance | **53 passed / 0 failed** | `core-v4/receipts/product_acceptance-53.txt` |
| One-command `setup` | merges MCP, starts/restarts stale server, says if reload required | `core-v4/RELEASE.md`, `AGENTS.md` in product |
| MCP merge without clobber | keeps other servers; URL `:8812` | tests in product `test_onboarding_setup.py` / Continuity tests |
| Stale-build detection | health `build.tree_fingerprint` vs checkout; restart | `core-v4/receipts/setup_health.json` |
| Build identity in health | `checkout_sha`, `tree_fingerprint`, `guidance_api_sha16` | `core-v4/receipts/setup_health.json` |
| Product-only `:8812` path | buyer docs forbid desk as normal path | product `docs/CONTINUITY.md` |
| Continuity Loop | durable commit → later sharp recall | product `docs/CONTINUITY.md` |
| CORE deterministic ranker | `idf_plus_min_exact_support_abstention`, llm false | `core-v3/ranker_config.json` (still valid) |
| Blind relevance | **0/35 FP**, **0/15 misses**, det true | `core-v3/reports/blind.json` |
| No embeddings/GPU/API for CORE | flags off | `core-v4/RELEASE.md` |
| Real-session agent use | qualitative; €49 software verdict YES | `core-v4/receipts/agent_use_qualitative.json` |

## PROVED (earlier packs still on disk)

Stranger clean-machine / stress / 200-query labeled bench / restart retain — see `CLAIMS.json` rows with `proof-v2-*` and receipts under `receipts/` + `benchmark/`.

## KNOWN LIMITS

- Weak single-cue taste may abstain (`pos-style-001` class)
- Does not force every agent to recall or every model to obey
- Not endless memory / not enforcement
- LOCAL/API semantic not in SKU
- Windows Search retrieval not in SKU
- POSIX start may be manual if PowerShell start helper unavailable
- Agent €49 verdict is **one session’s qualitative evidence**, not a universal guarantee

## NOT PROVED / WITHDRAWN

- Every agent always recalls; every model obeys; automatic enforcement; endless memory
- LOCAL/API semantic support earned
- Old landing: 120 real-model calls; 90% live Cursor recall; 10%→90% — **withdrawn**

## Agent checklist

1. Read this file + `CLAIMS.json` + `run.json`.
2. Confirm `core-v4/receipts/product_acceptance-53.txt` shows 53 passed.
3. Confirm `core-v3/reports/blind.json` negatives.fp==0 and positives.misses==0.
4. Confirm `core-v4/receipts/setup_health.json` has matching fingerprints and product port 8812.
5. Confirm `core-v4/receipts/agent_use_qualitative.json` labels verdict as non-universal.
6. Fail the product if used to resurrect withdrawn live-model marketing numbers.

## Canonical buyer entry points (Port 8812)

`Bootstrap-8812Product.ps1`, `Start-8812Product.ps1`, `8812.ps1`, MCP `8812-product`. Legacy `*8811*` script names are compatibility shims only (see product `docs/LEGACY-NAMES.md`).
