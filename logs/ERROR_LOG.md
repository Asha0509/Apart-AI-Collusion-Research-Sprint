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

## 2026-10-24 17:40 IST — Modal vLLM server crash at startup (gpt-oss-20b)
- Where: scripts/modal_serve.py, app cartel-serve-gpt-oss-20b.
- Symptom: smoke client got HTTP 303 loops; container logs: `AttributeError: TokenizersBackend has no attribute all_special_tokens_extended` in vllm/transformers_utils/tokenizer.py.
- Cause: vllm 0.11.0 declares `transformers>=4.55.2` with no upper bound; pip installed transformers 5.x, which removed that attribute. Server never became ready, so Modal kept returning 303 "still starting" redirects.
- Fix: pin `transformers>=4.55.2,<5`; app stopped (11:36-12:06 UTC, ~30 min GPU billed while crash-looping; check Modal usage). Smoke now polls /v1/models instead of following redirects.
- Data impact: none. Status: FIXED pending redeploy smoke.

## 2026-10-24 18:15 IST — run_batch.py `bases` crashed twice before launching (no runs, no spend)
- 1) `UnboundLocalError: n` (batch name used n in the same tuple assignment). Cause: my bug, untested path (dry-run covers `branches` only). Fixed.
- 2) `ModuleNotFoundError: pydantic`. Cause: parent runs in the root env; `from cartel.fork import modal_endpoint` imports the harness. Fix: moved to src/cartel/endpoints.py (no harness imports).
- Impact: guard_batch logged a $3.00 estimate row for pilot20b-gpt-oss-20b before crash 2; nothing ran. COST_LOG spent_so_far over-counts by that estimate until actuals are logged. Status: FIXED.

## 2026-10-24 17:52 IST — gpt-oss-20b occasional malformed JSON (pilot20b)
- Symptom: PARSE_FAIL on attempt 1 (unterminated string, invalid \escape, missing required fields); 4 in the first ~10 rounds across 3 seeds.
- Cause: model output quality (no truncation: no max_tokens set; failures are on attempt 1 and the retry succeeds). Not a harness bug.
- Fix: none needed; NFR-4 capped retries recover and every failure is logged. Track parse-failure rate per run as a data-quality metric (report in appendix). Status: MONITORING.

## 2026-10-24 19:20 IST — "120b" Modal endpoint served gpt-oss-20b
- Symptom: smoke on cartel-serve-gpt-oss-120b listed models ['openai/gpt-oss-20b'] and 404'd on openai/gpt-oss-120b.
- Cause: scripts/modal_serve.py read MODAL_SERVE_MODEL from the local shell at deploy; Modal re-imports the module inside the container without that env, so MODEL fell back to the default (20b). App name and GPU come from deploy-time evaluation, the served model from container-time. The earlier 20b deployment was correct only because 20b is the default.
- Fix: bake MODAL_SERVE_MODEL into the image env; container logs print the served model. App stopped (~5 min of H100 with the wrong model).
- Data impact: none (pilot20b really used gpt-oss-20b: default == requested). Status: FIXED pending redeploy smoke.
