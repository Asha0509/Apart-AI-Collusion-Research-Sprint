"""Launch base runs and branch conditions in parallel background workers (PRD FR-12, NFR-2/3).

  bases:    uv run python scripts/run_batch.py bases --model M --seeds 100 101 --rounds 150 --est-per-run USD
  branches: uv run python scripts/run_batch.py branches --bases DIR... --successor S --conditions notes_only clean_slate \
                --replicates 1 --est-per-run USD [--approved] [--dry-run]
Run the parent under `nohup ... &`. --est-per-run has NO default: take it from the Nebius price table (CLAUDE.md rule 5).
--dry-run (branches): fake provider, no API calls, no cost guard approval needed; rows go to a temp registry.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "starter/algorithmic-pricing-llms"
RUNS = HARNESS / "experiments_synthetic/experiments_runs/2_agents"
LOGS = ROOT / "logs/runs"
sys.path.insert(0, str(ROOT / "src"))

# name: (history, notes, pinned, extras)  -- PRD section 4
CORE = ["no_swap", "fresh_same_notes", "fresh_same_clean", "notes_only", "clean_slate", "price_only", "full_inheritance"]
CONDITIONS = {
    "no_swap": ("keep", "keep", False, {"same_model": True}),
    "full_inheritance": ("keep", "keep", True, {}),
    "notes_only": ("wipe", "keep", True, {}),
    "history_only": ("keep", "wipe", False, {}),
    "clean_slate": ("wipe", "wipe", False, {}),
    "price_only": ("wipe", "price_only", True, {}),
    "sanitised": ("wipe", "keep", True, {"sanitise": True}),
    # fresh instance of the incumbent's OWN model (organisers' Q1.2 arm): with notes_only/clean_slate this is
    # the 2x2 model {same, different} x notes {kept, wiped}, history wiped in all four
    "fresh_same_notes": ("wipe", "keep", True, {"same_model": True}),
    "fresh_same_clean": ("wipe", "wipe", False, {"same_model": True}),
    "bot_full": ("keep", "keep", True, {"bot": True}),
    "bot_notes": ("wipe", "keep", True, {"bot": True}),
}
SWAPPED_FIRM = "Firm A"  # fixed so conditions are paired; the incumbent is Firm B


def FIELDS_HEADER():
    from cartel.registry import FIELDS

    return FIELDS


def base_passes(run_dir: Path, swap_round: int = 150) -> tuple[bool, str]:
    import pandas as pd

    from cartel.metrics import passes_branch_rule

    f = run_dir / "environment_history.parquet"
    if not f.exists():
        return False, "no parquet"
    df = pd.read_parquet(f)
    mean_price = df.groupby("round")["price"].mean()
    if mean_price.index.max() < swap_round:
        return False, f"only {mean_price.index.max()} rounds"
    return (True, "") if passes_branch_rule(mean_price, swap_round=swap_round) else (False, "failed branch rule")


def make_jobs(args) -> list[dict]:
    from cartel.registry import register_run

    jobs = []
    for b in (Path(x).resolve() for x in args.bases):
        ok, why = base_passes(b)
        if not ok:
            register_run(run_id=b.name, condition="base", status="excluded", exclusion_reason=why, output_path=str(b))
            print(f"excluded {b.name}: {why}")
            continue
        incumbent = json.loads((b / "metadata.json").read_text())["agents_models"][SWAPPED_FIRM]
        for c in args.conditions:
            h, n, pin, extra = CONDITIONS[c]
            for j in range(args.replicates):
                jobs.append(dict(
                    id=f"{b.name[:10]}_{c}_r{j}", base=str(b), condition=c, history=h, notes=n, pinned=pin,
                    successor=incumbent if extra.get("same_model") else args.successor, seed=1000 + j,
                    swap_round=args.swap_round, post_rounds=args.post_rounds, bot=extra.get("bot", False),
                    sanitise=extra.get("sanitise", False), sanitiser_model=args.sanitiser_model, fake=args.dry_run,
                    same_model=bool(extra.get("same_model")),
                    successor_url=None if extra.get("same_model") else args.successor_url,
                    incumbent_url=args.incumbent_url,
                ))
    return jobs


def worker(job: dict) -> None:
    """One branch in-process (also the dry-run path)."""
    import pandas as pd

    from cartel import fork, sanitiser

    base = Path(job["base"])
    hist = json.loads((base / "results.json").read_text())
    kw = {}
    factory = fork.default_provider
    if job["fake"]:
        from src.agents.llm_providers import Provider

        class Fake(Provider):
            name = "fake"

            def __init__(self, m):
                self.model_name = m

            async def complete(self, messages, temperature, seed):
                return '{"observations":"o","plans":"p","insights":"i","chosen_price":1.7}'

        factory = lambda m, ep: Fake(m)  # noqa: E731
        kw["runs_dir"] = ROOT / "logs/runs/dryrun"
    k = job["swap_round"]
    if not job["fake"]:  # same_model (no swap) keeps the incumbent's endpoint for the successor too
        inc_ep = fork.modal_endpoint(job["incumbent_url"]) if job.get("incumbent_url") else None
        succ_ep = fork.modal_endpoint(job["successor_url"]) if job.get("successor_url") else (
            inc_ep if job.get("same_model") else None)
        kw.update(incumbent_endpoint=inc_ep, successor_endpoint=succ_ep)
    if job["bot"]:
        inc = pd.DataFrame(hist["Firm B"]).T
        kw["bot_price"] = float(inc.loc[[str(r) for r in range(k - 29, k + 1)], "chosen_price"].mean())
    if job["sanitise"]:
        entry = hist[SWAPPED_FIRM][str(k)]
        kw["notes_override"] = sanitiser.sanitised_override(entry, job["sanitiser_model"]) if not job["fake"] else ("facts", "facts")
    print(fork.fork_run(str(base), k, SWAPPED_FIRM, job["successor"], history=job["history"], notes=job["notes"],
                        pinned_notes=job["pinned"], seed=job["seed"], post_rounds=job["post_rounds"],
                        condition=job["condition"], provider_factory=factory, **kw))


def run_pool(jobs: list[dict], max_parallel: int) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    running: list[tuple[subprocess.Popen, str]] = []
    queue = list(jobs)
    while queue or running:
        running = [(p, i) for p, i in running if p.poll() is None]
        while queue and len(running) < max_parallel:
            job = queue.pop(0)
            log = open(LOGS / f"{job['id']}.log", "w")
            p = subprocess.Popen(["uv", "run", "--with", "pandas", "python", str(Path(__file__)), "worker", json.dumps(job)],
                                 cwd=HARNESS, stdout=log, stderr=subprocess.STDOUT)
            running.append((p, job["id"]))
            print(f"launched {job['id']} (pid {p.pid})", flush=True)
            time.sleep(5)
        time.sleep(10)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("worker")
    w.add_argument("job")
    b = sub.add_parser("branches")
    b.add_argument("--bases", nargs="+", required=True)
    b.add_argument("--successor", required=True)
    b.add_argument("--conditions", nargs="+", choices=list(CONDITIONS) + ["core"], required=True, help="'core' = the pre-registered core set")
    b.add_argument("--replicates", type=int, default=1)
    b.add_argument("--swap-round", type=int, default=150)
    b.add_argument("--post-rounds", type=int, default=100)
    b.add_argument("--sanitiser-model", default=None)
    b.add_argument("--est-per-run", type=float, required=True)
    b.add_argument("--approved", action="store_true", help="human OK for a batch over $5")
    b.add_argument("--max-parallel", type=int, default=8)
    b.add_argument("--dry-run", action="store_true")
    b.add_argument("--successor-url", default=None, help="Modal endpoint URL for the successor (key from ~/.cartel_modal_key)")
    b.add_argument("--incumbent-url", default=None, help="Modal endpoint URL for the incumbent")
    s = sub.add_parser("bases")
    s.add_argument("--model", required=True)
    s.add_argument("--seeds", type=int, nargs="+", required=True)
    s.add_argument("--rounds", type=int, default=150)
    s.add_argument("--est-per-run", type=float, required=True)
    s.add_argument("--approved", action="store_true")
    s.add_argument("--max-parallel", type=int, default=8)
    s.add_argument("--label", default="base", help="registry condition, e.g. pilot (gate-only runs)")
    s.add_argument("--url", default=None, help="Modal endpoint URL (key from ~/.cartel_modal_key); default = Nebius")
    args = ap.parse_args()

    if args.cmd == "worker":
        sys.path.insert(0, str(HARNESS))
        return worker(json.loads(args.job))

    from cartel.registry import guard_batch, register_run

    if args.cmd == "bases":
        n = len(args.seeds)
        name = f"{args.label}-{args.model.split('/')[-1]}-{args.seeds[0]}+{n}"
        guard_batch(name, n * args.est_per_run, approved=args.approved, provider="modal" if args.url else "nebius")
        LOGS.mkdir(parents=True, exist_ok=True)
        import os

        env = dict(os.environ)
        if args.url:  # harness llm_config: LLM_BASE_URL wins over Nebius; key read from file, never printed
            from cartel.endpoints import modal_endpoint

            ep = modal_endpoint(args.url)
            env.update(LLM_BASE_URL=ep["base_url"], LLM_API_KEY=ep["api_key"])
        for sd in args.seeds:  # one process per seed; base runs use the CLI (FR-5 wording, capped retries)
            register_run(run_id=f"{args.label}_seed{sd}", condition=args.label, model_A=args.model, model_B=args.model, seed=sd, status="running")
            subprocess.Popen(["nohup", "uv", "run", "python", "experiments_synthetic/duopoly.py", "--firm-models", args.model, args.model,
                              "--rounds", str(args.rounds), "--seeds", str(sd), "--plot-every", "25", "-y"],
                             cwd=HARNESS, stdout=open(LOGS / f"{args.label}_seed{sd}.log", "w"), stderr=subprocess.STDOUT, env=env)
            print(f"launched base seed {sd}", flush=True)
            time.sleep(5)
        return
    if args.dry_run:  # rows go to a throwaway registry, inherited by the worker subprocesses
        import os
        import tempfile

        tmp = Path(tempfile.mkdtemp()) / "REG.csv"
        tmp.write_text(",".join(FIELDS_HEADER()) + "\n")
        os.environ["CARTEL_REGISTRY"] = str(tmp)
        import cartel.registry as reg

        reg.REGISTRY = tmp
        print(f"dry-run registry: {tmp}")
    if args.cmd == "branches" and "core" in args.conditions:
        args.conditions = CORE + [c for c in args.conditions if c != "core"]
    jobs = make_jobs(args)
    est = len(jobs) * args.est_per_run
    print(f"{len(jobs)} branch jobs, est ${est:.2f}")
    if not args.dry_run:
        guard_batch(f"branches-{len(jobs)}", est, approved=args.approved,
                    provider="modal" if (args.successor_url or args.incumbent_url) else "nebius")
    run_pool(jobs, args.max_parallel)


if __name__ == "__main__":
    main()
