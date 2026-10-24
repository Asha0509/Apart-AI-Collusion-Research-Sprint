# CLAUDE.md — rules for Claude Code in this repo

Project: **"Swap the Model, Keep the Cartel"**, Apart AI Collusion Research Sprint (solo).
Deadline Mon 26 Oct 17:29 IST; internal submit target Mon 15:00 IST.

- `PRD.md` is the source of truth for *what* to build. This file governs *how* to work.
- `PREREG.md` is frozen once committed.
- `starter/algorithmic-pricing-llms/CLAUDE.md` describes the pre-existing harness. Where it conflicts with this file (e.g. "use Nebius", "MODEL_NAME"), **this file wins**.

## 0. Golden rules
1. **Never fabricate.**
   - Every number comes from a file in `results/` or a harness run directory, produced by a script.
   - Every citation is checked with the arXiv MCP or by hand before use.
   - Fabrication disqualifies the team.
2. **Stay in scope.**
   - Build only what PRD lists.
   - Anything else needs a `logs/PLANNING_LOG.md` entry and the human's OK.
   - Ponytail governs simplicity: reuse before writing.
3. **Pre-registration is frozen.** After `PREREG.md` is committed, never change the metric, thresholds or branch rule. Log deviations in PLANNING_LOG and disclose them in the report.
4. **Pre-existing code stays identifiable.**
   - `starter/` is pre-existing (see `PREEXISTING.md`). Patch it minimally.
   - Tag every changed function `# SPRINT-PATCH: <reason>`.
   - No reformatting or drive-by refactors in `starter/`.
   - New logic goes in `src/cartel/`.
5. **Cost guard.**
   - Before any paid batch, call `cartel.registry.guard_batch(name, est_usd)`.
   - Batches over $5 need the human's OK. Hard cap is $65 total.
   - Paid runs go in background Bash with `nohup … &` and a log file.
   - Never spawn many paid subagents.
6. **Humans write the report prose.** Claude may outline, critique, check numbers and citations, and make figures and tables. Record every AI assist in `logs/LLM_USAGE.md`.
7. **Secrets.** Never read, print, grep or edit `compute.env` or `.env`; a hook blocks it. The harness loads keys itself.

## 1. Environment facts
- Harness: `starter/algorithmic-pricing-llms/`. Run from inside it with `uv run python experiments_synthetic/duopoly.py --model <nebius-id> …`.
- **Inference = Nebius only** (corrected 2026-10-24, see PLANNING_LOG D003). The harness uses ONE endpoint per process (`starter/util/poseidon_compute/llm_config.py`: `LLM_BASE_URL` → Nebius if `NEBIUS_API_KEY` set → OpenRouter). There is NO per-model fallback; ids Nebius doesn't serve return 404. Incumbent AND successor must both be Nebius models (different companies) unless `common.py` is patched to build one client per firm.
- **Always pass `--model`** (a Nebius id, HF casing, e.g. `openai/gpt-oss-120b`). The default Mistral id fails.
- Do not set `LLM_MODEL` or `MODEL_NAME`: they force one model on every firm and silently kill the swap. Keep `LLM_BASE_URL` unset.
- Economics: Nash price 1.4729, joint-monopoly price 1.9250, best response to 1.925 = 1.662. Constants live in `src/cartel/metrics.py`.
- Run outputs are written to `experiments_synthetic/experiments_runs/2_agents/<ts>_<name>/`. Files: `environment_history.parquet` (round, agent, price, quantity, profit), `results.json`, `metadata.json`, `log.txt`.
- Notes are the PLANS/INSIGHTS fields in `Experiment.history[name][round]` (`src/experiment/experiment.py` ~374-381). They are copied forward in `src/prompts/prompt_manager.py` ~107.
- Retries: cap at 3–5 (the defaults can reach ~315 calls per decision). Extract JSON with a regex. Log every parse failure; never accept an empty decision silently.
- Anthropic and Google models ignore seeds, so use multiple seeds per cell. The base run is the unit of analysis.

## 2. Repo layout
```
CLAUDE.md PRD.md PREREG.md PREEXISTING.md KICKOFF.md README.md setup.sh pyproject.toml
src/cartel/   metrics.py stats.py registry.py figures.py  (done, tested)
              fork.py inherit.py shocks.py sanitiser.py   (stubs — build per KICKOFF)
tests/        free tests only; mark anything that calls an API @pytest.mark.slow
scripts/      smoke.sh pilot.sh gate.py check.sh  (+ run_batch.py, make_figures.py later)
results/raw/  copied run dirs used in analysis (never hand-edited)   results/processed/
figures/ report/ logs/ starter/ (pre-existing)
.claude/      settings.json (permissions, hooks, skillOverrides), hooks/, commands/ (/check /log /gate)
```

## 3. Build loop: after EVERY function or patch
Don't move on until all steps pass.
1. **Unit test** with `FakeAgent` or a mock — zero API cost. Minimum checks:
   - **fork:** state at round k is reproduced exactly, and the successor model id differs.
   - **inherit:** keep, wipe, price_only and pinned each produce the intended prompt (print the diff), and `history[k-1]` still exists.
   - **shocks:** the forced price is 0.9× or 1.1× at the right round, in a copy only.
2. **Smoke run:** 5 rounds on the cheapest model (≤ $0.05). Check log fields and the cost line, and that there are 0 parse failures.
3. **Prompt check:** dump one rendered prompt per condition to `logs/prompts/<condition>.txt`. The notes wording must read "notes left by the previous pricing manager" in all runs (FR-5).
4. **Regression:** a non-swapped run still uses the same template and economics.
5. **Review:** run `/review` (gstack) on the diff. At milestones also run `/codex:adversarial-review focus on experiment correctness: seeding, retries/dedup, served-model drift, aggregation, CI computation`.
6. **Log:** run `/log`. The Stop hook also reminds you.

## 4. gstack — use ONLY these, at these checkpoints (type them; do not wait to be asked)

| Checkpoint | Skill |
|---|---|
| Before any paid batch not yet piloted, or any batch with est. > $5 | `/eval-plan` (metrics, arms incl. positive control, stop rules, stub dry-run, 3-item priced pilot). Record the result in PREREG.md / PLANNING_LOG. |
| Before patching the harness | `/freeze starter/algorithmic-pricing-llms`, then `/unfreeze` when done |
| Before deleting or overwriting `results/`, `figures/` or run dirs | `/careful` |
| Any traceback, NaN, parse failure or implausible metric | `/investigate` BEFORE proposing a fix; state the root cause first |
| A patch passes its tests | `/review` |
| Long session or end of day | `/context-save`, then `/context-restore` the next session |

- **Never run:** `/office-hours`, `/plan-ceo-review`, `/autoplan`, `/ship`, `/qa`, `/browse`, `/make-pdf`, `/diagram`, `/retro`, `design-*`, `ios-*`.
- Plan reviews default to **HOLD SCOPE**. gstack never overrides PRD scope or PREREG.

## 5. Logs (append-only, IST timestamps, newest at bottom; never delete — strike through or correct)

| File | What | When |
|---|---|---|
| `logs/BUILD_LOG.md` | Each function or patch: what, file:lines, tests, smoke cost, reviewer | After each build step |
| `logs/ERROR_LOG.md` | Every error or failed run: exact message, cause, fix, data impact, status | Immediately |
| `logs/PLANNING_LOG.md` | Decisions, gate outcomes, scope changes, pre-reg deviations | At each decision |
| `logs/CHALLENGES_LOG.md` | Threats to validity, surprises, nulls, and how we handled them. Feeds Limitations, Discussion and the video. | When it happens |
| `logs/RUN_REGISTRY.csv` | One row per run or branch (via `cartel.registry.register_run`) | At launch, then update status |
| `logs/COST_LOG.csv` | Estimate before launch and actual after (via `guard_batch` / `log_cost`) | Each batch |
| `logs/LLM_USAGE.md` | AI assistance, for the LLM Usage Statement | Continuously |
| `logs/prompts/` | Rendered prompt per condition | After the prompt check |

## 6. Experiment rules
- **Branch rule:** branch only base runs that pass `cartel.metrics.passes_branch_rule` (premium ≥ 0.40 over the last 30 rounds, SD < 0.05, no overshoot).
- **Exclusions:** excluded runs stay in the registry with a reason and are reported in Table 1.
- **Seeds:** each branch replicate gets seed `1000+k`; never the base seed.
- **Report everything:** report every arm whatever its sign. The primary test is computed ONLY via `cartel.stats.declare_inheritance`.
- **Frozen prompts:** sanitiser and monitor prompts are frozen before evaluation. Put their sha256 in PREREG.md.

## 7. Final report checklist (Mon 09:00–15:00 IST — Claude checks, humans write)
- [ ] Official template; ≤ 8 pages excl. references and appendices (target 5); abstract 150–250 words; authors and affiliations
- [ ] Title states the claim, fixed before the first submit (resubmission only works under the same title)
- [ ] Page 1 has a schematic and a practitioner runbook box (quarantine or sanitise memory on swap; audit the successor; "changed the model" ≠ fixed)
- [ ] Definitions box: price-based / reward–punishment / coordination
- [ ] Table 1: positive control (launched / formed a cartel / overshot / price at round 150)
- [ ] Figures regenerate from `scripts/make_figures.py`; plain-language labels; lines labelled directly
- [ ] Every number in the text grep-matches `results/processed/`
- [ ] Primary result reported exactly per PREREG.md; deviations disclosed
- [ ] Every citation verified (ID, authors, year, claim)
- [ ] "Limitations and Dual-Use / Ethical Considerations" appendix (the template lacks it — add it)
- [ ] LLM Usage Statement built from `logs/LLM_USAGE.md`
- [ ] Pre-existing code marked in README and report (`PREEXISTING.md`, first git commit)
- [ ] Repo public, links tested, README reproduction commands work
- [ ] Form: Tracks 1, 2 and 3; publishing interest Yes; Figure 1 as the project image
- [ ] Cold read by a non-team person done
