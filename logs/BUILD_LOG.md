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
