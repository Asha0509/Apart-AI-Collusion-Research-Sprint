"""Fork a finished base run at round k and continue with firm i's model replaced. (PRD FR-2, FR-3)

TO BUILD (Claude Code, KICKOFF prompt 2). Harness facts (starter/algorithmic-pricing-llms):
- One provider for all firms is built in experiments_synthetic/common.py (`run_setting`, ~line 76):
  make it per-firm (~10 LOC, tag `# SPRINT-PATCH`).
- Per-agent state lives in Experiment.history[name][round] (src/experiment/experiment.py ~374-381):
  plans, insights, market_data. src/experiment/resume.py is the template for loading a run.
- Each branch replicate gets seed 1000+k. Never reuse the base seed.
- Write a registry row (cartel.registry.register_run) before launching each branch.
"""


def fork_run(
    base_run_dir: str,
    swap_round: int,
    firm: str,
    successor_model: str,
    history: str = "keep",
    notes: str = "keep",
    pinned_notes: bool = True,
    seed: int = 1000,
    post_rounds: int = 100,
) -> str:
    raise NotImplementedError("build in KICKOFF prompt 2")
