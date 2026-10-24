# TASKS — living checklist (check against PRD.md §12 and logs/PLANNING_LOG.md; update as we go)

## Now (gate)
- [ ] Pilots running: gpt-oss-120b seeds 3-8 (3 procs), Hermes-4-405B, nemotron-3-super, MiniMax-M3 (s0-2). Batch pilot3 approved, est $5.40.
- [ ] On finish: `uv run python scripts/gate.py` -> PLANNING_LOG D002 -> decision memo (base model + different-company successor).
- [ ] Check Nebius dashboard spend vs estimate; `log_cost` actual.
- [ ] Fallback deadline: no passing base by ~09:00 IST Sat -> option 3 (focal-price reframe), decide BEFORE PREREG commit.

## Build (after gate; each: free test -> smoke -> prompt dump -> /review -> /log)
- [ ] A3 smoke-check successor candidate (5 rounds, <=$0.05)
- [ ] FR-5 wording in BOTH PP_P0 and GENERAL_PROMPT (A6) [/freeze]
- [ ] FR-2 per-firm provider in common.py (only if mixed endpoints needed; else same Nebius client, different model ids)
- [ ] A4 token/cost tracking in metadata
- [ ] FR-4 inheritance switches + FR-3 fork (src/cartel/fork.py, inherit.py) (A2), seed 1000+k (A7)
- [ ] NFR-4 retry cap 3-5, regex JSON, log parse failures
- [ ] FR-6 bot control, FR-7 shocks, FR-8/9 sanitiser+monitor (hash prompts into PREREG)
- [ ] A5 locked-price flag in metrics (descriptive)
- [ ] A1 message-format merge, only if candidates fail the gate

## Then
- [ ] /eval-plan, fill PREREG (MDE, models, hashes), commit alone
- [ ] run_batch.py, base runs, branches, controls, shocks (guard_batch every batch; >$5 needs OK)
- [ ] analyse.py, make_figures.py, Table 1; report checklist CLAUDE.md §7 (humans write prose)

## Housekeeping
- [ ] Commit after each step; push later (no remote yet)
- [ ] LLM_USAGE.md entries
