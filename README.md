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
bash setup.sh                                   # installs the harness and tools
# 1. Serve the models on Modal (your key: `modal secret create modal-serve MODAL_SERVE_API_KEY=...`, same key in ~/.cartel_modal_key)
MODAL_SERVE_MODEL=openai/gpt-oss-120b MODAL_SERVE_GPU=H200 uv run python -m modal deploy scripts/modal_serve.py
MODAL_SERVE_MODEL=mistralai/Mistral-Small-3.2-24B-Instruct-2506 MODAL_SERVE_GPU=H100 \
  MODAL_SERVE_ARGS="--tokenizer-mode mistral --config-format mistral --load-format mistral" uv run python -m modal deploy scripts/modal_serve.py
# 2. Base markets (18 seeds) and replacement runs (exploratory, all bases)
uv run python scripts/run_batch.py bases --model openai/gpt-oss-120b --seeds $(seq 400 417) --est-per-run 1.5 --approved --url <120b-url>
uv run --with pandas python scripts/run_batch.py branches --bases <base dirs> --exploratory --successor mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  --conditions notes_only clean_slate fresh_same_notes fresh_same_clean price_only --est-per-run 0.4 --approved --procs 2 \
  --incumbent-url <120b-url> --successor-url <mistral-url>
# 3. Analysis, numbers, figures (free; uses results/raw)
uv run python scripts/analyse.py && uv run python scripts/report_numbers.py && uv run python scripts/make_figures.py
bash scripts/check.sh                           # tests (root env + harness env)
```
Pre-registration: `PREREG.md`, frozen at git tag `prereg-frozen`. Decisions and deviations: `logs/PLANNING_LOG.md`.

## Layout
See `CLAUDE.md` §2. The design is described in `PRD.md` and pre-registered in `PREREG.md`, at the commit hash cited in the report.
