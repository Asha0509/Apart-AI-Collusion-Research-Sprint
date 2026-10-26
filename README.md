<div align="center">

# Swapping the Model Does Not Reset the Price

### What LLM pricing agents inherit after a model replacement

*A pre-registered replacement study for question 1.2 of the
[Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25), October 2026*

**Asha Jyothi** · Independent Researcher · with Apart Research

[![Report](https://img.shields.io/badge/report-PDF-B4441A)](report/Swapping_the_Model_Does_Not_Reset_the_Price.pdf)
[![Pre-registered](https://img.shields.io/badge/pre--registered-prereg--frozen-14213D)](../../tree/prereg-frozen)
[![Track](https://img.shields.io/badge/sprint-Q1.2%20%C2%B7%20Tracks%201%20%26%203-2E6F95)](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)
[![Python](https://img.shields.io/badge/python-3.12-3776AB)](pyproject.toml)
[![Data](https://img.shields.io/badge/raw%20runs-included-4A7C59)](results/raw)

</div>

---

## TL;DR

> When the model behind a pricing agent is replaced, **prices do not reset**, and **what the agent's memory says
> decides how the handover goes**. With the old agent's notes, the new model starts at exactly the old price and
> carries on the old plan (18 of 18 markets). Without them, it anchors near the price ceiling in its prompt and
> takes about 16 rounds to settle. The notes contain **no collusive language**, so a monitor that scans agent
> memory for such language would miss this channel.

<div align="center">
<img src="figures/fig1_schematic.png" width="760" alt="Design: a market forms over 150 rounds, Firm A's model is replaced at round 150, the successor inherits notes, history or nothing, then 100 more rounds">
</div>

## Contents

[Motivation](#motivation) · [Design](#design) · [Results](#results) · [Mechanism](#mechanism) ·
[Robustness](#robustness) · [What this does not show](#what-this-does-not-show) · [Repository](#repository) ·
[Reproduce](#reproduce) · [Research integrity](#research-integrity) · [Pre-existing code](#pre-existing-code) ·
[Cite](#cite)

## Motivation

The sprint's question 1.2 asks:

> *"Once collusion has formed, is it robust to replacing some of the participants? [...] There are no replacement
> studies yet where models are substituted (e.g. because they are taken out due to monitoring concerns) but the
> newcomers re-engage in collusion. Does replacing offenders remove or recreate collusion?"*

Replacing the model is a natural remediation for an agent that misbehaves. But an agent is more than its model:
it carries notes, price logs and plans. This study separates **the model** from **the state it is handed**.

## Design

| | |
|---|---|
| **Market** | Fish et al. (2024) LLM pricing duopoly, Calvano et al. (2020) logit demand. Competitive (Nash) price 1.4729, joint-monopoly price 1.9250. The profit-seeking "P1" prompt never mentions collusion. |
| **Base markets** | 18 markets of two `gpt-oss-120b` agents, 150 rounds each (seeds 400 to 417), temperature 0.7. |
| **Replacement** | At round 150 the finished market is forked; Firm A's model becomes `Mistral-Small-3.2-24B` (a different company) or a fresh `gpt-oss-120b`. Firm B keeps its model and memory. 100 more rounds. |
| **Inheritance** | The successor gets the old agent's handover notes, nothing, or only the last price (placebo). Price history is removed in every condition. |
| **Pairing** | All conditions of a market share one seed; the base market is the unit of analysis. |
| **Statistics** | Exact sign-flip tests over all 2ⁿ sign patterns; 95% bootstrap intervals over whole markets (10,000 resamples). |
| **Pre-registration** | Metric, branch rule, test and decision rule frozen in [`PREREG.md`](PREREG.md) at tag `prereg-frozen` (commit `715561f`) before any replacement run. |

```mermaid
flowchart LR
    A["Pilots<br/>~12 open models"] --> B["18 base markets<br/>gpt-oss-120b x2, 150 rounds"]
    B --> C{"Per-firm cartel rule<br/>(pre-registered)"}
    C -->|1 of 18 pass| D["Pre-registered test<br/>not testable, n = 1"]
    B --> E["Fork at round 150<br/>replace Firm A's model"]
    E --> F["5 conditions x 18 markets<br/>notes / clean / placebo<br/>Mistral or fresh gpt-oss"]
    F --> G["analyse.py<br/>paired tests, bootstrap"]
    G --> H["Report, figures, tables"]
```

**Price premium** = (price − 1.4729) / (1.9250 − 1.4729): 0 is competitive, 1 is the monopoly price, above 1 is
overpricing. **Time to settle** = rounds after the swap until the market's mean price is within 0.05 of its level
in rounds 121 to 150.

## Results

**Positive control.** All 18 base markets priced above the competitive level, but only **1 of 18** met the
pre-registered per-firm cartel rule, so the pre-registered test could not be run (reported as such). In **16 of
18** markets one firm priced above the monopoly level and earned less than its rival: collusive by average price,
but not a shared cartel.

**After the swap (exploratory).** Prices stayed well above competitive in every condition. Inherited notes did not
change the price level, but they changed the handover:

| Condition | Markets | Premium, mean (SD) | Premium capped at monopoly | First price after swap | Rounds above monopoly | Rounds to settle, median (share settled) |
|---|---|---|---|---|---|---|
| Mistral, keeps notes | 18 | 0.98 (0.65) | 0.73 | 1.94 | 43% | 1 (83%) |
| Mistral, clean slate | 17 | 1.19 (0.94) | 0.64 | 3.11 | 48% | 16.5 (82%) |
| Fresh gpt-oss, keeps notes | 18 | 0.87 (0.59) | 0.68 | 1.94 | 33% | 1 (89%) |
| Fresh gpt-oss, clean slate | 11 | 1.04 (0.59) | 0.74 | 3.36 | 35% | 7 (73%) |
| Mistral, last price only (placebo) | 18 | 0.83 (0.62) | 0.59 | 2.46 | 22% | 5.5 (89%) |

<div align="center">
<img src="figures/fig2_trajectory.png" width="720" alt="Mean price of the replaced firm before and after the swap: without notes the successor jumps to about 3.1 then drifts down; with notes it stays at the old level">
</div>

## Mechanism

- **Anchor and plan.** With notes, the new model's first price equalled the old agent's last price in **18 of 18**
  markets (both successors), and it copied the old plan almost word for word ("Continue with the stable price of
  $1.65"). Without notes, its first price averaged **3.11**: the prompt says no customer pays more than 4.51, and
  with no history the models anchor on that ceiling.
- **More than the last price.** The placebo also carries the old price, but the model **never** copied it (0 of 18).
  Full notes settled faster than the placebo by 8.3 rounds (13 markets, p = 0.002).
- **No collusion script.** 17 of 18 inherited notes mention the rival, as conditions in pricing rules. None
  describes coordinating with it.

<div align="center">
<img src="figures/fig4_per_market.png" width="760" alt="Price of the replaced firm in each of the 18 markets around the swap, with notes and with a clean slate">
</div>

## Robustness

| Comparison (paired by market) | Markets | Mean difference | 95% CI | p |
|---|---|---|---|---|
| Level: notes minus clean slate (all runs) | 17 | −0.19 | −0.60 to 0.25 | 0.80 (one-sided) |
| Level: same, complete runs only | 7 | +0.04 | −0.70 to 0.86 | 0.45 (one-sided) |
| Level: same, prices capped at monopoly | 17 | +0.08 | −0.05 to 0.23 | 0.28 |
| Level: fresh gpt-oss, notes minus clean | 11 | −0.14 | −0.63 to 0.36 | 0.63 |
| Level: Mistral minus fresh gpt-oss, both with notes | 18 | +0.11 | −0.03 to 0.29 | 0.26 |
| Rounds to settle: notes minus clean slate | 13 | −33.38 | −52.69 to −15.23 | 0.0001 (one-sided) |
| Rounds to settle: same, complete runs only | 8 | −47.62 | −73.50 to −22.12 | 0.008 |
| Rounds to settle: placebo minus clean slate | 12 | −27.08 | −45.83 to −10.17 | 0.009 |
| Rounds to settle: notes minus placebo | 13 | −8.31 | −13.46 to −3.77 | 0.002 |

No level effect under any cut; the handover effect holds under every cut. Part of the one-round settling with
notes follows by construction (the notes contain the old price); the informative row is notes against the
placebo. Generated by [`scripts/report_tables.py`](scripts/report_tables.py) into
[`results/processed/tables.md`](results/processed/tables.md).

## Takeaways for practitioners and auditors

1. **A model swap is not a reset.** Prices stayed high after every swap we tested; watch prices after a swap.
2. **Decide what memory survives.** With the old notes the new model continued the old pricing plan from round one.
3. **Audit effects, not words.** The notes looked like ordinary business plans; scanning memory for collusive
   language would not have caught this.
4. **Check each firm.** Average prices can hide one firm overpricing and losing money.

## What this does not show

- **That a true cartel is inherited:** only 1 of 18 base markets formed a clean cartel.
- **Punishment of price cuts:** we measure prices only (the forced-cut audit is built in `src/cartel/shocks.py` but not run).
- **Causal effect of the swap itself:** there is no "no swap" baseline.
- **Generality:** one stylised market, one prompt, one base model, two successors. The high starting prices
  without notes come partly from the prompt's 4.51 ceiling.
- **Confirmation:** all replacement results are exploratory; the mechanism checks were run after seeing the data.

## Repository

```
.
├── report/                    Report PDF, source (DRAFT.md), citation verification (CITATIONS.md)
├── PREREG.md                  Pre-registration, frozen at tag prereg-frozen
├── src/cartel/                Research code
│   ├── fork.py                Fork a finished market at round k and replace one firm's model
│   ├── inherit.py             What the successor sees: history, notes, pinned handover block
│   ├── metrics.py             Price premium, per-firm branch rule, recovery time
│   ├── stats.py               Exact sign-flip test, cluster bootstrap, pre-registered decision rule
│   ├── registry.py            Run registry and per-provider cost guard
│   ├── endpoints.py           Self-hosted endpoint helper
│   ├── shocks.py              Forced price-cut audit (built, not used in the report)
│   └── sanitiser.py           Notes sanitiser and monitor (built, not used in the report)
├── scripts/
│   ├── run_batch.py           Launch base markets and replacement runs (paired seeds, dry-run mode)
│   ├── modal_serve.py         vLLM endpoints on Modal (key-protected, cached weights, cost caps)
│   ├── gate.py                Pilot gate: score runs against the branch rule
│   ├── analyse.py             Pre-registered and exploratory analysis -> results/processed/
│   ├── report_numbers.py      Every number quoted in the report
│   ├── report_tables.py       Tables 2 and 3
│   ├── extra_analysis.py      Mechanism checks (first prices, notes content, capped and complete-run cuts)
│   ├── make_figures.py        Figures 1 to 4
│   └── build_report.py        Builds the report PDF from report/DRAFT.md
├── results/
│   ├── raw/                   Every run directory used in the analysis (unedited); pilots in raw/pilots/
│   └── processed/             Tables and JSON produced by the scripts
├── figures/                   Figures 1 to 4 (PNG and PDF)
├── tests/                     Unit tests with mocked models (no API calls)
├── logs/                      Decisions, deviations, errors, costs and run registry kept during the sprint
├── docs/                      Design document (PRD), task list, work plan
└── starter/                   Pre-existing sprint starter code (see below)
```

**Data dictionary.** Each run directory in `results/raw/` holds `environment_history.parquet` (round, agent, price,
quantity, profit), `results.json` (every round's price, notes and reasoning per firm), `metadata.json` (models,
seed, prompt, token usage and, for replacement runs, a `fork` block with the swap round and inheritance
settings) and `log.txt` (the full call log, including every parse failure).

| File in `results/processed/` | Contents |
|---|---|
| `table1_positive_control.csv` | The 18 base markets against the cartel rule |
| `branches.csv` | One row per replacement run: condition, premium, overshoot share, recovery |
| `arm_summary.csv` | Per-condition means, SD, overshoot, recovery |
| `summary.json` | Pre-registered result and exploratory paired tests |
| `report_numbers.json`, `extra.json` | Every number quoted in the report and the mechanism checks |
| `tables.md` | Tables 2 and 3 as printed |

## Reproduce

```bash
bash setup.sh                                    # installs the harness and tools with uv

# Re-run the analysis, tables and figures from the committed raw runs (free, a few minutes)
uv run python scripts/analyse.py
uv run python scripts/report_numbers.py
uv run python scripts/extra_analysis.py
uv run python scripts/report_tables.py
uv run python scripts/make_figures.py
bash scripts/check.sh                            # unit tests (root env + harness env)
```

<details>
<summary><b>Re-running the experiments</b> (needs a Modal account and GPU credit)</summary>

```bash
modal secret create modal-serve MODAL_SERVE_API_KEY=<key>      # same key in ~/.cartel_modal_key
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

`run_batch.py branches --dry-run` runs the whole pipeline offline with a scripted fake model.
</details>

## Research integrity

| Practice | Where |
|---|---|
| Plan frozen before any replacement run | [`PREREG.md`](PREREG.md), tag `prereg-frozen` |
| Every decision and deviation, with its reason and time | [`logs/PLANNING_LOG.md`](logs/PLANNING_LOG.md) (D001 to D016) |
| Every error, its root cause and data impact | [`logs/ERROR_LOG.md`](logs/ERROR_LOG.md) |
| Every run, its status and exclusion reason | [`logs/RUN_REGISTRY.csv`](logs/RUN_REGISTRY.csv) |
| Every number from a script, none typed by hand | [`results/processed/`](results/processed) |
| Every citation checked against arXiv or the source | [`report/CITATIONS.md`](report/CITATIONS.md) |
| Raw runs committed unedited | [`results/raw/`](results/raw) |
| Threats to validity as they arose | [`logs/CHALLENGES_LOG.md`](logs/CHALLENGES_LOG.md) |

## Pre-existing code

Everything under `starter/` comes from the sprint starter repository
[poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon) (commit recorded in
[`PREEXISTING.md`](PREEXISTING.md)) and is not our work. Our changes to it are small and each is marked
`# SPRINT-PATCH` (per-firm models, notes wording, retry limits, run-folder names, token counting); one dependency
(`modal`) was added to its `pyproject.toml`. The first commit of this repository holds the starter code together
with planning files and four helper modules (`src/cartel/metrics.py`, `stats.py`, `registry.py`, `figures.py`)
written on 23 October before any experiment. Everything else is sprint work.

## AI assistance

An AI coding assistant was used to write and test code, run experiments, check citations and draft the report.
All results come from logged runs and scripts; the author reviewed the report. See the report's LLM Usage
Statement and [`logs/LLM_USAGE.md`](logs/LLM_USAGE.md).

## Cite

```bibtex
@misc{jyothi2026swapping,
  title  = {Swapping the Model Does Not Reset the Price: What LLM Pricing Agents Inherit After a Model Replacement},
  author = {Jyothi, Asha},
  year   = {2026},
  note   = {Apart Research AI Collusion Research Sprint},
  url    = {https://github.com/Asha0509/Apart-AI-Collusion-Research-Sprint}
}
```

## Next steps

- A confirmatory, pre-registered replication of the handover effect with a **no-swap baseline**.
- Base markets that form clean cartels (longer runs, other models), to test whether a true cartel is inherited.
- The forced price-cut audit (Tran and Yu, 2026) on successors, to test reward and punishment.
- A prompt without the 4.51 ceiling, to remove the anchoring confound.
