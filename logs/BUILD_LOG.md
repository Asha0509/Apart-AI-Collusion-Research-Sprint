# Build Log
Append one entry per function/module built or patched. Newest at bottom. IST timestamps.

<!-- TEMPLATE
## YYYY-MM-DD HH:MM IST — <function/module name>
- **Type:** new | SPRINT-PATCH to pre-existing
- **File:lines:** src/fork.py:12-88
- **Purpose:** (link PRD FR-#)
- **Tests:** tests/test_fork.py — PASS/FAIL (what was checked)
- **Smoke run:** 5 rounds on <model> — cost $0.0x — parse failures: 0
- **Prompt check:** logs/prompts/<condition>.txt reviewed by <name>
- **Review:** gstack review / self-review — issues found + fixed
- **Built by:** <human> with <Claude Code / Codex>
- **Notes / follow-ups:**
-->

## 2026-10-24 05:00 IST — storage.py SPRINT-PATCH: pid suffix on run dirs
- File: starter/algorithmic-pricing-llms/src/experiment/storage.py (create_experiment_dir). Test: next smoke run shows "_pidNNNN" in the dir name.

## 2026-10-24 05:10 IST — scripts/gate.py, scripts/pilot.sh edits
- New/changed (not starter/): gate.py labels runs by model via logs/pilot logs, adds sd_last30, firm_gap, overshoot_last30, ≥2/3 rule (PLANNING_LOG D004). pilot.sh: PILOT_MODELS required, sleep 5 between launches. Tests: none (script); pilot paid, no smoke. Built by Claude Code.

## 2026-10-24 05:15 IST — gate.py: shared-dir runs labelled CONTAMINATED
- scripts/gate.py: dirs claimed by >1 pilot log get model "CONTAMINATED(shared dir)" and are excluded from pass counts (ERROR_LOG 05:10). Test: ran gate.py (below). Built by Claude Code.

## 2026-10-24 06:00 IST — gate.py: split-log support; cost guard blocked pilot batch
- **Type:** new (scripts/, not starter/)
- **File:lines:** scripts/gate.py:21 — log stems with a `_partN` suffix map to the same model, so one model can run as several parallel processes.
- **Tests:** none; ran gate.py before the change only. Not yet re-run after it.
- **Runs / spend:** no runs launched. guard_batch refused a batch (est $5.40 > $5, assumptions unverified); awaiting human OK. Spend so far: $0 recorded via guard; Nebius actual spend unknown (harness has no usage tracking). No OpenRouter spend.
- **Also this session:** CLAUDE.md §1 and PRD corrected to Nebius-only (PLANNING_LOG D003); gate outcome FAIL logged (D002). Open: decide staged ($1.60) vs full ($5.40) batch.
- **Built by:** Claude Code

## 2026-10-24 14:20 IST — common.py SPRINT-PATCH: per-firm models (FR-2)
- **Type:** SPRINT-PATCH to pre-existing. **File:** starter/algorithmic-pricing-llms/experiments_synthetic/common.py (run_setting ~72-85,96,104; CLI `--firm-models` ~196; _run_all ~263). /freeze used, /unfreeze done.
- **Purpose:** PRD FR-2 / D003. One provider per firm; default (no flag) unchanged. Successor on another endpoint needs no harness change: OpenAICompatibleProvider already honours explicit base_url/api_key for non-openrouter presets.
- **Tests:** tests/test_per_firm.py — 3 PASS in the harness venv (distinct models per firm, default unchanged, wrong count raises). Skips in root env (no pydantic); cmd in file docstring. Root suite: 10 passed, 1 skipped.
- **Smoke run / prompt check / regression:** not yet run (needs a paid 5-round smoke; do with successor check A3). /review pending.
- **Spend:** $0. **Open:** run /review; smoke with --firm-models on two Nebius models.
- **Built by:** Claude Code

## 2026-10-24 14:40 IST — prompts.py SPRINT-PATCH: FR-5 notes wording
- **File:** starter/.../src/prompts/prompts.py (PP_P0 line ~6, GENERAL_PROMPT line ~50). /freeze used, cleared.
- **Change:** "written by a previous copy of yourself" and "which you wrote last time" -> "notes left by the previous pricing manager". Applies to P1/P2 (via PP_P0) and the notes template; GENERAL_PROMPT_NO_NOTES had no such text.
- **Tests:** tests/test_fr5_wording.py 3 PASS (harness venv). Prompt check: logs/prompts/base_FR5.txt (per-condition dumps follow once inherit.py exists).
- **Note:** all pilots ran with the OLD wording, so pilots are gate-only; base runs must be re-run with the new wording. Possible effect on cartel rate -> re-check pass rate on the real base runs.
- **Smoke / review:** pending. Spend $0.

## 2026-10-24 15:10 IST — LLM_agent.py / experiment.py SPRINT-PATCH: NFR-4 retries + regex + parse-failure log
- **File:** starter/.../src/agents/LLM_agent.py (MAX_RETRIES 15->4; regex `\{.*\}` extraction; PARSE_FAIL warning + `agent.parse_failures` counter) and src/experiment/experiment.py (max_retries 20->3). /freeze used, cleared.
- **Effect:** worst case ~4x4=16 calls/decision (was ~315). Applies to ALL runs started after this commit; pilots ran with old retries/parsing.
- **Tests:** tests/test_agent_parse.py 3 PASS (prose-wrapped JSON, 2 logged failures then recovery, cap + raise). Smoke/review pending. Spend $0.

## 2026-10-24 16:00 IST — src/cartel/inherit.py + fork.py (FR-3, FR-4, FR-5)
- **Type:** new. **Files:** src/cartel/inherit.py (successor_view, pinned_block), src/cartel/fork.py (SuccessorPromptManager, load_base, fork_run[_async], successor_endpoint for Modal/NVIDIA/Ollama).
- **Design:** no further harness patch. Real history is never edited; the successor gets a transformed copy per round; pinned handover block appended to every post-swap prompt; history[k] always kept (KeyError trap). Registry rows written (running, then done/failed; latest row wins). Branch seed must differ from base seed.
- **Tests:** tests/test_fork_inherit.py 8 PASS (harness venv, fake provider, 0 API): state reproduced exactly to round k, successor model id differs, base dir unchanged (sha256), per-condition prompts for full/notes-only/history-only/clean-slate/price-only, FR-5 phrase in every arm, pinned persists after successor overwrites notes, same-seed rejected, registry rows.
- **Prompt check:** logs/prompts/{full_inheritance,notes_only,history_only,clean_slate,price_only_placebo}.txt reviewed by Claude (human review pending). Note: on round k+1 notes_only shows the notes in the PLANS/INSIGHTS section AND the pinned block; later rounds PLANS hold the successor's own notes.
- **Smoke run / review:** pending. Spend $0.

## 2026-10-24 16:30 IST — /review of patches since 276b8c4 (self-review in the gstack checklist's terms; no remote/PR, base = first commit)
- **Scope:** common.py, prompts.py, LLM_agent.py, experiment.py, storage.py, fork.py, inherit.py, 4 test files. Gate scan: no tests removed/relaxed; only added tests.
- **Findings fixed:** (1) test module monkeypatched `common.make_provider` without restoring -> now `MonkeyPatch.context()`; (2) no-swap arm must use pinned_notes=False or its prompt differs from the base run -> documented in fork.py; (3) registry is append-only -> analysis must take the latest row per run_id (documented).
- **Finding to disclose (not reverted):** `starter/algorithmic-pricing-llms/pyproject.toml` gained `modal>=1.6.2` and `uv.lock` changed (+~990 lines) in commit 78bd2a3; I did not intend to commit it (came in via `git add -A` after the Modal install). It is a sprint change to a pre-existing file: keep (needed only for Modal hosting) and list in the report's pre-existing-code disclosure, or revert if Modal is not used.
- **Known ceilings (not defects):** regex `\{.*\}` is greedy (two JSON objects in one reply -> parse failure -> retry); successor_view deep-copies history per prompt (fine at 250 rounds).
- **Tests:** harness-env set 17 PASS together. Smoke runs and /codex adversarial review still pending (milestone).

## 2026-10-24 17:40 IST — A4 usage tracking, FR-6/7 (fork bot_price, forced_prices, shocks.py), FR-8/9 sanitiser, A5 locked_price
- **SPRINT-PATCH** llm_providers.py (tokens_in/out/n_calls from response.usage) and experiment.py (`metadata["usage_tokens"]` per model, summed). Harness frozen during edit, cleared.
- **New:** fork.py generalised (resume_round, forced_prices -> ForcedPriceAgent, bot_price -> FakeAgent, metadata["fork"]); shocks.py (run_shock copies from the branch, shock_response -> matching ratio); sanitiser.py (sanitise, monitor_flag raising on anything but COLLUSIVE/CLEAN, sanitised_override, prompt_hashes); metrics.locked_price.
- **Tests (0 API):** test_usage_tracking 1, test_fork_inherit 10 (bot holds price, forced cut at the right round in a copy only, identical before shock, branch sha unchanged), test_sanitiser 3, test_metrics +1. Run cmd in file docstrings (harness venv + --with pandas).
- **PREREG.md (uncommitted):** frozen prompt hashes filled. Human must approve before the PREREG commit.
- **Smoke / codex adversarial review:** pending. Spend $0.

## 2026-10-24 18:10 IST — Smoke run (A3 + per-firm + FR-5 + NFR-4 + A4 + fork), ~$0.05 est.
- **Base:** `duopoly.py --firm-models openai/gpt-oss-120b openai/gpt-oss-120b --rounds 8 --seeds 50` -> run 1792839635_..._seed50_pid44253. 0 PARSE_FAIL, new FR-5 wording in metadata, usage_tokens recorded (16 calls, 16.1k in, 18.8k out).
- **Fork:** k=6, Firm A -> Qwen/Qwen3-30B-A3B-Instruct-2507 (different company), history=wipe notes=keep pinned, seed 1006, 2 rounds. metadata agents_models differs for Firm A only; usage per model recorded; 0 parse failures; registry rows written (running, done). Run dir 1792839702_fork_..._pid44401 (smoke: exclude from analysis).
- **Bug found + fixed:** fork wrote to `experiments_runs/` in the harness root instead of `experiments_synthetic/experiments_runs/` (moved the smoke dir; default now fixed in fork.py).
- **Cost note:** gpt-oss emits ~1.2k output tokens/call (reasoning), so output tokens dominate; per 150-round run expect roughly 0.3M out + >1M in. Re-estimate once the Nebius price table is read.
- **Prompt check:** logs/prompts/*.txt dumped from the mocked run; real rendered prompt matches (FR-5 phrase present).

## 2026-10-24 18:50 IST — scripts/run_batch.py (KICKOFF prompt 6)
- **New:** `bases` (one background process per seed via duopoly.py --firm-models M M) and `branches` (applies passes_branch_rule, registers exclusions with reasons, builds paired jobs for the 9 conditions in PRD §4 plus bot/sanitised, seed 1000+replicate, max-parallel workers). `--est-per-run` is required (no invented default); guard_batch is called before any paid launch; >$5 needs `--approved` from the human.
- **registry.py:** `CARTEL_REGISTRY` env override so dry runs never touch logs/RUN_REGISTRY.csv.
- **Test:** dry-run on a real passing pilot base (gpt-oss seed 8), 3 conditions, fake provider: 3 forks written under logs/runs/dryrun, real registry unchanged. Not a pytest; no API cost.
- **Bug found by the dry-run:** relative base paths broke when workers ran from the harness dir -> resolved to absolute.
- **Open:** dry-run only covers `branches`; `bases` unrun (paid). Sanitised arm needs `--sanitiser-model`. A `rm -rf logs/runs` was denied by the permission hook; I did not retry (run /careful first if deleting).
