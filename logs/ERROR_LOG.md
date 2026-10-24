# Error Log
Log every error immediately. Never delete; update Status.

<!-- TEMPLATE
## YYYY-MM-DD HH:MM IST — E### <short title>
- **Where:** file/function/run_id
- **Symptom:**
- **Exact message:** ```<paste>```
- **Cause:**
- **Fix:** (commit hash)
- **Impact on data:** none | runs <ids> excluded/rerun (also note in RUN_REGISTRY)
- **Status:** OPEN | FIXED | WONTFIX (reason)
-->

## 2026-10-24 04:52 IST — Qwen/Qwen3.5-397B-A17B pilot failed at round 1
- Error: Nebius 400 BadRequest "System message must be at the beginning."
- Cause: model's chat template requires the system message first; harness message order differs.
- Fix: none — model dropped from pilots (would need a harness patch). Data impact: none.

## 2026-10-24 05:00 IST — Run-directory collision (data integrity)
- Symptom: seed-0 runs missing for Qwen3-235B, DeepSeek-V4.1-Flash, gpt-oss-120b; one seed-0 dir (1792791427…) shared by several models.
- Cause: StorageManager names dirs f"{unix_time}_{name}" with exist_ok=True; parallel launches in the same second collide silently.
- Fix: SPRINT-PATCH in src/experiment/storage.py appends _pid{pid}. Data impact: round-1 seed-0 dir 1792791427… EXCLUDED (contaminated). Round-2 pilots launched before the patch: check for shared seed dirs.

## 2026-10-24 05:10 IST — Round-2 seed-0 dir 1792796721… shared by 4 launches
- Where: experiments_runs/2_agents/1792796721_duopoly_setting_P1_mem100_seed0 (launched before the pid patch; Kimi-K3, GLM-5.3, Qwen3.5-397B, DeepSeek-V4-Pro all logged it).
- Cause: same as the same-second collision above. Kimi/GLM were writing until killed (~23:19 UTC); only DeepSeek continues.
- Impact: DeepSeek-V4-Pro seed 0 is SUSPECT (log.txt/results.json may be mixed; parquet rewritten from DeepSeek memory but unverified). gate.py maps the dir to whichever log it finds last, so its model label is unreliable. Seeds 1,2 are unique dirs. Status: OPEN; treat seed 0 as excluded unless parquet/metadata verified as DeepSeek-only.
- Also: round-1 dirs for Qwen3-235B, Qwen3-30B, gpt-oss each list 3 dirs in their logs, with 1792791427…seed0 shared by 4 logs (excluded).

## 2026-10-24 06:20 IST — google/gemma-3-27b-it pilot failed at round 1
- Error: Nebius 400 "Conversation roles must alternate user/assistant/user/assistant/..."
- Cause: model's chat template rejects the harness message order (same class as Qwen3.5). Fix: none; model dropped (would need a harness patch). Data impact: none; its share of the batch is unspent.
