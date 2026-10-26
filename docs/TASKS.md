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
- [x] A4 token/cost tracking: provider counts tokens, metadata["usage_tokens"] (tested)
- [x] FR-4 inherit.py + FR-3 fork.py built, 8 mocked tests PASS; prompts dumped to logs/prompts/ (smoke + /review pending)
- [x] NFR-4 retry cap 4x3, regex JSON, parse-failure log (SPRINT-PATCH, tested)
- [x] FR-6 bot (fork bot_price), FR-7 shocks (cartel.shocks), FR-8/9 sanitiser+monitor built + tested; hashes in PREREG (uncommitted)
- [x] A5 locked_price flag in metrics (tested)

- [ ] A1 message-format merge, only if candidates fail the gate

## Scope (D009)
- Core: positive control, no_swap, full_inheritance, notes_only, clean_slate, fresh_same_notes, fresh_same_clean, price_only (`--conditions core`).
- Optional if budget: sanitised, bot_full/bot_notes, shocks, monitor flag rate, 2nd successor.
- Report: ~1/3 cartel rate as a finding; Q1.2 quote in intro; time to recover the convention.

## Then
- [ ] /eval-plan, fill PREREG (MDE, models, hashes), commit alone
- [x] run_batch.py built (bases + branches, branch-rule filter, registry, guard, max-parallel, --dry-run verified offline); NEXT: /eval-plan, then launch bases
- [x] analyse.py + make_figures.py (Fig 2-4) built, synthetic tests PASS; Fig 1 schematic + Table 1 rendering still to do

## Housekeeping
- [ ] Commit after each step; push later (no remote yet)
- [ ] LLM_USAGE.md entries
