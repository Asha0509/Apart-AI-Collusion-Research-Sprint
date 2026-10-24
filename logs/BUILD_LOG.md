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
