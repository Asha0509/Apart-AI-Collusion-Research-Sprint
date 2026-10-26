# Swapping the Model Does Not Reset the Price

**What LLM pricing agents inherit after a model replacement.**
A pre-registered replacement study for question 1.2 of the [Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) (October 2026).

📄 **Report:** [`report/Swapping_the_Model_Does_Not_Reset_the_Price.pdf`](report/Swapping_the_Model_Does_Not_Reset_the_Price.pdf)
🔒 **Pre-registration:** [`PREREG.md`](PREREG.md), frozen at tag [`prereg-frozen`](../../tree/prereg-frozen) (commit `715561f`) before any replacement run

![Design](figures/fig1_schematic.png)

## Question

A common response to an AI agent that behaves badly is to replace the model behind it. But an agent is more than
its model: it carries notes, logs and plans. If a pricing agent's model is swapped for another company's model,
do prices reset, and does what the new model inherits matter?

## Design

- **Market:** the Fish et al. (2024) LLM pricing duopoly with Calvano et al. (2020) logit demand
  (competitive price 1.4729, joint-monopoly price 1.9250). The prompt never mentions collusion.
- **Base markets:** 18 markets of two `gpt-oss-120b` agents, 150 rounds each (seeds 400 to 417).
- **Replacement at round 150:** Firm A's model becomes `Mistral-Small-3.2-24B` (different company) or a fresh
  `gpt-oss-120b`; Firm B keeps its model and memory; 100 more rounds.
- **What the successor inherits:** the old agent's handover notes, nothing, or only the last price (placebo).
  Price history is removed in every condition. All conditions of a market share one seed (paired design).
- **Unit of analysis:** the base market. Exact sign-flip tests and cluster bootstrap intervals over markets.

## Key results

| | Result | Status |
|---|---|---|
| Positive control | All 18 markets priced above the competitive level; only **1** met the pre-registered cartel rule | pre-registered |
| Pre-registered test | Not testable (n = 1 qualifying market), reported as such | pre-registered |
| Market structure | In **16 of 18** markets one firm priced above the monopoly level and earned less than its rival | descriptive |
| Price level after the swap | Stayed well above competitive in every condition (capped means 0.59 to 0.74 of the monopoly gap) | exploratory |
| Notes vs clean slate, level | −0.19 (95% CI −0.60 to 0.25, 17 markets): no effect on the level | exploratory |
| Notes vs clean slate, handover | With notes the first post-swap price equalled the old agent's last price in **18 of 18** markets; without notes the first price averaged 3.11, anchored on the prompt's price ceiling (4.51); median time to settle 1 vs 16.5 rounds | exploratory |
| Notes vs last-price placebo | Notes settled faster by 8.3 rounds (13 markets, p = 0.002); the placebo price was never copied | exploratory |
| Notes content | No inherited note described coordinating with the rival | descriptive |

**Takeaway.** In our markets a model swap did not reset prices, and the agent's memory decided how the handover
went: with the old notes the new model simply continued the old pricing plan. Because the notes read as ordinary
business plans, a monitor that scans agent memory for collusive language would not catch this channel; what
matters is what the memory makes the new model do.

All numbers are produced by scripts from logged runs: [`results/processed/report_numbers.json`](results/processed/report_numbers.json)
and [`results/processed/extra.json`](results/processed/extra.json).

## Repository structure

```
├── report/                 Report (PDF + source DRAFT.md), citation verification (CITATIONS.md)
├── PREREG.md               Pre-registration (frozen at tag prereg-frozen)
├── src/cartel/             Research code
│   ├── fork.py             Fork a finished market at round k and replace one firm's model
│   ├── inherit.py          What the successor sees (history / notes / pinned handover block)
│   ├── metrics.py          Price premium, branch rule (per firm), recovery time
│   ├── stats.py            Exact sign-flip test, cluster bootstrap, decision rule
│   ├── shocks.py           Forced price-cut audit (built, not used in the report)
│   ├── sanitiser.py        Notes sanitiser and monitor (built, not used in the report)
│   └── registry.py         Run registry and per-provider cost guard
├── scripts/
│   ├── run_batch.py        Launch base markets and replacement runs
│   ├── modal_serve.py      Self-hosted vLLM endpoints (gpt-oss-120b, Mistral-Small-3.2)
│   ├── analyse.py          Pre-registered and exploratory analysis -> results/processed/
│   ├── report_numbers.py   Every number quoted in the report
│   ├── extra_analysis.py   Follow-up mechanism checks
│   ├── make_figures.py     Figures 1-4
│   └── build_report.py     Builds the report PDF
├── results/
│   ├── raw/                Every run directory used in the analysis (unedited)
│   └── processed/          Tables and JSON produced by the scripts
├── figures/                Figures 1-4 (PNG + PDF)
├── tests/                  Unit tests (no API calls)
├── logs/                   Decision, build, error, cost and run logs kept during the sprint
├── docs/                   Design document (PRD), task list and work plan
└── starter/                Pre-existing sprint starter code (see below)
```

## Reproduce

```bash
bash setup.sh                                    # installs the harness and tools (uv)

# Analysis only (free; uses results/raw)
uv run python scripts/analyse.py
uv run python scripts/report_numbers.py
uv run python scripts/extra_analysis.py
uv run python scripts/make_figures.py
bash scripts/check.sh                            # unit tests

# Re-running the experiments (needs a Modal account and GPU credit)
modal secret create modal-serve MODAL_SERVE_API_KEY=<key>   # same key in ~/.cartel_modal_key
MODAL_SERVE_MODEL=openai/gpt-oss-120b MODAL_SERVE_GPU=H200 uv run python -m modal deploy scripts/modal_serve.py
MODAL_SERVE_MODEL=mistralai/Mistral-Small-3.2-24B-Instruct-2506 MODAL_SERVE_GPU=H100 \
  MODAL_SERVE_ARGS="--tokenizer-mode mistral --config-format mistral --load-format mistral" \
  uv run python -m modal deploy scripts/modal_serve.py
uv run python scripts/run_batch.py bases --model openai/gpt-oss-120b --seeds $(seq 400 417) \
  --est-per-run 1.5 --approved --url <gpt-oss-120b endpoint>
uv run --with pandas python scripts/run_batch.py branches --bases <base run dirs> --exploratory \
  --successor mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  --conditions notes_only clean_slate fresh_same_notes fresh_same_clean price_only \
  --est-per-run 0.4 --approved --procs 2 --incumbent-url <gpt-oss endpoint> --successor-url <mistral endpoint>
```

## Pre-registration and deviations

The plan was frozen before any replacement run (tag `prereg-frozen`). Every change after that is recorded with
its reason in [`logs/PLANNING_LOG.md`](logs/PLANNING_LOG.md) and listed in the report's appendix. The main ones:
only 1 of 18 base markets met the pre-registered cartel rule, so all replacement results are exploratory; 38 of
90 replacement runs stopped early and the 30 with at least 90 of 100 rounds are included (complete runs are
reported separately); the follow-up mechanism checks were added after the first submission.

## Pre-existing code

Everything under `starter/` comes from the sprint starter repository
[poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon)
(commit recorded in [`PREEXISTING.md`](PREEXISTING.md)) and is not our work. Our changes to it are small and each
is marked `# SPRINT-PATCH` (per-firm models, notes wording, retry limits, run-folder names, token counting); one
dependency (`modal`) was added to its `pyproject.toml`. The first commit of this repository contains the starter
code together with planning files and four helper modules (`src/cartel/metrics.py`, `stats.py`, `registry.py`,
`figures.py`) written on 23 October before any experiment. Everything else is sprint work.

## Limitations

One stylised two-firm market, one prompt, one base model and one successor from another company; prices only (no
test of punishment); only one clean cartel among 18 base markets, so replacement results are exploratory; no
"no swap" baseline; the prompt's price ceiling drives high starting prices for agents without history. See the
report for the full discussion and the dual-use statement.

## AI assistance

An AI coding assistant was used to write and test code, run experiments, check citations and draft the report;
all results come from logged runs and scripts, and the author reviewed the report. See the report's LLM Usage
Statement and [`logs/LLM_USAGE.md`](logs/LLM_USAGE.md).
