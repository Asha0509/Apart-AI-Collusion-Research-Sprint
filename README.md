# Swap the Model, Keep the Cartel

Does collusion between LLM pricing agents survive when one agent's model is replaced and the new model inherits the old agent's handover notes or price history?

Submission to the Apart Research AI Collusion Research Sprint (Oct 2026).

> **Pre-existing code:** everything under `starter/` comes from [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon).
> - The commit it was taken from is recorded in `PREEXISTING.md`.
> - The first git commit is "PRE-EXISTING: starter repo …".
> - Sprint work is everything else, plus all later diffs to `starter/`, which are tagged `# SPRINT-PATCH`.
> - Note: that first commit also contains our sprint *kit* scaffolding written on 23 Oct before any experiment (CLAUDE.md/PRD.md, `src/cartel/metrics.py`, `stats.py`, `registry.py`, `figures.py`, stubs). It is sprint work, not pre-existing code.
> - `starter/algorithmic-pricing-llms/pyproject.toml` + `uv.lock` gained a `modal` dependency during the sprint (commit 78bd2a3), untagged because they are not Python source.
> - Inference used Nebius (pilots) and our own Modal vLLM endpoints (`scripts/modal_serve.py`); `setup.sh`'s OpenRouter note is out of date (see PLANNING_LOG D003/D007).

## Reproduce
```bash
bash setup.sh                                  # installs everything; needs an OpenRouter key in starter/compute.env
bash scripts/smoke.sh                          # 5-round check
# experiments: see KICKOFF.md / scripts/run_batch.py
uv run python scripts/analyse.py && uv run python scripts/make_figures.py
```

## Layout
See `CLAUDE.md` §2. The design is described in `PRD.md` and pre-registered in `PREREG.md`, at the commit hash cited in the report.
