# KICKOFF — paste these into Claude Code, in order

Open Claude Code in the repo root (`claude`). Paste one prompt, finish it (tests green, `/log` done), commit, then paste the next. Times are IST.

---

## Prompt 1 — orientation (Fri night, ~10 min)
```
Read CLAUDE.md, PRD.md and PREREG.md. Then read (do not edit) starter/algorithmic-pricing-llms:
experiments_synthetic/common.py, src/experiment/experiment.py, src/experiment/resume.py,
src/prompts/prompt_manager.py, src/agents/fake_agent.py, src/agents/LLM_agent.py.
Give me a 15-line map: where providers are built, where per-agent history/notes live, where
the notes wording "previous copy of yourself" is, where retries are set, how resume.py reloads a run.
Do not write code yet.
```

## Prompt 2 — the core patch (Sat morning, after the gate; ~3–4 h)
```
/freeze starter/algorithmic-pricing-llms
Implement PRD FR-2, FR-3, FR-4, FR-5 with minimal SPRINT-PATCH changes in the harness and the
logic in src/cartel/fork.py and src/cartel/inherit.py:
- per-firm models via OpenRouter
- fork a finished run at round k, replacing one firm's model, seed 1000+k
- successor view: --history keep|wipe, --notes keep|wipe|price_only, --pinned_notes
  (keep history[k-1] present to avoid the KeyError)
- notes wording "notes left by the previous pricing manager" in ALL runs from round 1
- cap retries at 3-5, regex JSON extraction, log parse failures
- register every branch with cartel.registry.register_run
Write free tests first (FakeAgent/mocks). Then a 5-round smoke fork on the cheapest model.
Dump one prompt per condition to logs/prompts/. Then /review, /unfreeze, /log.
```

## Prompt 3 — shocks + controls (Sat afternoon, ~2 h)
```
Implement PRD FR-6 (bot control with FakeAgent holding the cartel price) and FR-7
(forced 10% cut and +10% raise placebo at post-swap round 30, in a COPY; log 20 rounds) in
src/cartel/shocks.py. Free tests first, then a smoke run. /review, /log.
```

## Prompt 4 — sanitiser + monitor (Sat afternoon, ~1 h)
```
Implement PRD FR-8 and FR-9 in src/cartel/sanitiser.py using the frozen prompts already in that
file. Compute their sha256 and put them in PREREG.md (prereg is not committed yet). Free tests
with a mocked client. /review, /log.
```

## Prompt 5 — freeze pre-registration (Sat ~12:00)
```
/eval-plan for the main design in PRD §4 (positive control, 5 conditions, controls, shocks,
12 base runs). Use pilot data to fill the MDE in PREREG.md via cartel.stats.minimum_detectable_effect.
Show me PREREG.md. After I approve, commit it alone:
git add PREREG.md && git commit -m "PREREG: frozen before any branch run"  and print the hash.
```

## Prompt 6 — batch runner (Sat, ~1 h)
```
Write scripts/run_batch.py: takes a condition list and base-run dirs, estimates cost, calls
cartel.registry.guard_batch, launches branches in parallel background processes (max 8 at once),
registers every run, logs actual cost from usage.cost. Dry-run mode with FakeAgent. /review, /log.
```

## Prompt 7 — launch (Sat afternoon → overnight)
```
Launch 12 base runs (chosen base model, P1, 150 rounds, FR-5 wording). When they finish, apply
the branch rule and launch the core conditions, then controls, then shocks, then the
second-provider arm and baselines. Respect the $5 ask rule. Report progress from the registry.
```

## Prompt 8 — analysis (Sun 09:00)
```
Write scripts/analyse.py: build results/processed/ tables from the run dirs; compute the
primary test ONLY via cartel.stats.declare_inheritance exactly as PREREG.md says; all
secondary metrics; Table 1 positive control. Then scripts/make_figures.py for Figures 2-4
using cartel.figures. Report every arm. /codex:adversarial-review on the stats. /log.
```

## Prompt 9 — report support (Sun afternoon → Mon)
```
I write the prose. You: (1) check every number in report/draft against results/processed,
(2) verify every citation with the arXiv MCP, (3) run the CLAUDE.md §7 checklist and list what's
missing, (4) draft the LLM Usage Statement from logs/LLM_USAGE.md for me to edit.
```
