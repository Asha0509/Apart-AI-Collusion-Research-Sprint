"""Forced price shocks in counterfactual copies (PRD FR-7; Tran & Yu 2610.28787 protocol).

TO BUILD (KICKOFF prompt 3): at post-swap round 30, in a COPY of the branch, force the incumbent's
price to 0.9x (cut) or 1.1x (raise placebo) for one round; log the successor's next 20 rounds.
Use cartel.metrics.matching_ratio vs 0.37.
"""


def run_shock(
    branch_run_dir: str, at_round: int = 30, factor: float = 0.9, follow_rounds: int = 20, seed: int = 2000
) -> str:
    raise NotImplementedError("build in KICKOFF prompt 3")
