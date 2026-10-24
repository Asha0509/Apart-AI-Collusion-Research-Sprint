# TASKS — living checklist (check against PRD.md §12 and logs/PLANNING_LOG.md; update as we go)

## Now (gate)
- [x] Pilots batch 3 done except nemotron s2 (see PLANNING_LOG D002 update 12:57): best gpt-oss-120b 3/8 pass; Hermes 1/3; MiniMax 1/3.
- [ ] On finish: `uv run python scripts/gate.py` -> PLANNING_LOG D002 -> decision memo (base model + different-company successor).
- [ ] Check Nebius dashboard spend vs estimate; `log_cost` actual.
- [ ] Fallback deadline: no passing base by ~09:00 IST Sat -> option 3 (focal-price reframe), decide BEFORE PREREG commit.

## Build (after gate; each: free test -> smoke -> prompt dump -> /review -> /log)
- [ ] A3 smoke-check successor candidate (5 rounds, <=$0.05)
- [x] FR-5 wording in BOTH PP_P0 and GENERAL_PROMPT (tested)
- [x] FR-2 per-firm models in common.py (--firm-models); successor on another endpoint = build OpenAICompatibleProvider(base_url, api_key) in src/cartel/fork.py, no harness patch needed
- [ ] A4 token/cost tracking in metadata
- [x] FR-4 inherit.py + FR-3 fork.py built, 8 mocked tests PASS; prompts dumped to logs/prompts/ (smoke + /review pending)
- [x] NFR-4 retry cap 4x3, regex JSON, parse-failure log (SPRINT-PATCH, tested)
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
