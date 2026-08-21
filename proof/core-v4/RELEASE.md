# Port 8812 — frozen software release

**version:** `1.0.0`  
**codename:** continuity-core  
**released_at:** 2026-08-19T19:24:00+03:00  
**git_tag:** `v1.0.0`  
**git_sha:** `0ca0679a67d444a06aba2a43302c781ce3728a89`  
**tree_fingerprint:** `6b14f46ff9600804`  
**guidance_api_sha16:** `e01edac39a679f72`  
**product_acceptance:** **53 passed / 0 failed**

## What this release is

Buyer SKU: **CORE engine + Agent Kit + docs/proof**.

- Local deterministic guidance bank (JSON)
- MCP **`8812-product`** on **`127.0.0.1:8812`**
- Continuity Loop: durable commit → later sharp recall (or abstention)
- One agent setup path: `python -m dimensional_agent.product.cli setup`
- No embeddings, GPU, Qdrant, Voyage, or Windows Search required for CORE

## Compatibility

- Verified on **Windows** with Python **3.11+** (product venv from Bootstrap)
- POSIX bootstrap/start documented; Windows `setup` helper restarts via PowerShell
- Host: any MCP-capable agent (Cursor documented); human may need one MCP reload after first `mcp.json` write

## Known limitations (honest)

- Does not force every agent to call recall
- Does not force every model to obey guidance
- Not endless memory / not enforcement / not Cursor intercept
- LOCAL/API semantic profiles are **not** in this SKU
- Windows Search retrieval is **not** in this SKU
- Weak single-cue taste paraphrases may abstain by design (`pos-style-001` class)
- macOS/Linux: start server manually if `Start-8811Product.ps1` is unavailable; `setup` reports clearly

## Core promise

Port 8812 helps agents reduce amnesia. It increases continuity and effective capability. It does not cure amnesia and does not give an agent endless memory.

## Public proof

Hashed receipts: `Viss007/port-8812-site` → `proof/` (**Proof v4**).

## Agent €49 software verdict (qualitative)

Current working-session agent verdict: **YES** (software + Agent Kit worth €49).  
This is real-use evidence from one agent session, **not** a universal guarantee that every agent/host will behave the same.

