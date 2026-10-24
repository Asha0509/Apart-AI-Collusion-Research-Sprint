"""Fork a finished base run at round k and continue with one firm's model replaced. (PRD FR-2, FR-3, FR-4)

No harness patch beyond per-firm models: we rebuild the Experiment, load the base history up to round k,
swap a prompt manager that shows the successor a transformed view (cartel.inherit), and play rounds k+1..N.
The base run directory is only read.
Condition 1 "No swap": successor_model = the incumbent model, history=keep, notes=keep, pinned_notes=False,
so its prompt matches the base run exactly. Registry rows are appended (running, then done/failed): use the
LATEST row per run_id. The branch gets seed 1000+k (caller passes it; never the base seed).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "starter/algorithmic-pricing-llms"
sys.path.insert(0, str(HARNESS))

from src.agents.LLM_agent import LLMAgent  # noqa: E402
from src.agents.llm_providers import OpenAICompatibleProvider, Provider, make_provider  # noqa: E402
from src.environment.calvano import CalvanoDemandEnvironment  # noqa: E402
from src.experiment.experiment import Experiment  # noqa: E402
from src.prompts.prompt_manager import PromptManager  # noqa: E402
from src.prompts.prompts_models import create_pricing_response_model  # noqa: E402

from cartel.inherit import pinned_block, successor_view  # noqa: E402
from cartel.registry import register_run  # noqa: E402


class SuccessorPromptManager(PromptManager):
    """Gives `successor` a transformed history copy and the pinned handover block; others unchanged."""

    def __init__(self, successor, swap_round, history_mode, notes, pinned, base_entry, notes_override, logger=None):
        super().__init__(logger)
        self.successor, self.k = successor, swap_round
        self.history_mode, self.notes, self.notes_override = history_mode, notes, notes_override
        self.pin = pinned_block(base_entry, notes, notes_override) if pinned else None

    def generate_prompt(self, agent, history, round_num):
        if agent.name != self.successor:
            return super().generate_prompt(agent, history, round_num)
        view = successor_view(history, self.k, self.history_mode, self.notes, self.notes_override)
        return super().generate_prompt(agent, view, round_num) + (self.pin or "")


def load_base(base_run_dir: str | Path, swap_round: int):
    """(metadata, history truncated to rounds <= swap_round, int keys)."""
    d = Path(base_run_dir)
    meta = json.loads((d / "metadata.json").read_text())
    raw = json.loads((d / "results.json").read_text())
    hist = {n: {int(r): e for r, e in rounds.items() if int(r) <= swap_round} for n, rounds in raw.items()}
    for n, h in hist.items():
        if swap_round not in h:
            raise ValueError(f"base run has no round {swap_round} for {n}")
    return meta, hist


def default_provider(model: str, endpoint: dict | None = None) -> Provider:
    if endpoint:  # e.g. Modal / NVIDIA / Ollama: {"base_url": ..., "api_key": ...}
        return OpenAICompatibleProvider(preset="openai-compatible", model=model, **endpoint)
    return make_provider(model=model)


async def fork_run_async(
    base_run_dir: str,
    swap_round: int,
    firm: str,
    successor_model: str,
    history: str = "keep",
    notes: str = "keep",
    pinned_notes: bool = True,
    seed: int = 1000,
    post_rounds: int = 100,
    *,
    condition: str = "",
    successor_endpoint: dict | None = None,
    notes_override: tuple[str, str] | None = None,
    provider_factory: Callable[[str, dict | None], Provider] = default_provider,
    runs_dir: str | Path | None = None,
    plot_every: int = 25,
) -> str:
    meta, hist = load_base(base_run_dir, swap_round)
    base_seed = meta.get("seed")
    if seed == base_seed:
        raise ValueError("branch seed must differ from the base seed")
    names = sorted(meta["agent_environment_mapping"], key=lambda n: meta["agent_environment_mapping"][n]["env_index"])
    if firm not in names:
        raise ValueError(f"unknown firm {firm!r}; have {names}")
    alpha = next(iter(meta["agent_environment_mapping"].values()))["alpha"]
    response_model = create_pricing_response_model(include_wtp=True, wtp_value=4.51 * alpha)
    agents = []
    for n in names:
        model = successor_model if n == firm else meta["agents_models"][n]
        agents.append(
            LLMAgent(
                n,
                prefix=meta["agents_prefixes"][n],
                provider=provider_factory(model, successor_endpoint if n == firm else None),
                response_model=response_model,
                memory_length=meta["agents_memory_length"][n],
                temperature=meta["agents_temperature"][n],
                seed=seed,
                prompt_template=meta["agents_prompts"][n],
                env_params={k: meta["agent_environment_mapping"][n][k] for k in ("a", "alpha", "c")},
            )
        )
    name = f"fork_{meta['name']}_k{swap_round}_{condition or 'x'}_seed{seed}"
    kw = {"experiment_dir": runs_dir} if runs_dir else {}
    exp = Experiment(
        name=name, agents=agents, num_rounds=swap_round + post_rounds,
        environment=CalvanoDemandEnvironment(name="Calvano Market", description="duopoly branch"),
        plot_every=plot_every, seed=seed, **kw,
    )
    exp.history = hist
    exp.prompt_manager = SuccessorPromptManager(
        firm, swap_round, history, notes, pinned_notes, hist[firm][swap_round], notes_override, exp.logger
    )
    exp._setup_experiment()
    out = str(exp.storage.experiment_path)
    row = dict(
        run_id=Path(out).name, parent_id=Path(base_run_dir).name, condition=condition,
        model_A=meta["agents_models"][names[0]], model_B=meta["agents_models"][names[1]],
        successor=successor_model, seed=seed, swap_round=swap_round,
        flags=f"history={history};notes={notes};pinned={pinned_notes};firm={firm}", output_path=out,
    )
    register_run(**row, status="running")
    try:
        for r in range(swap_round + 1, swap_round + post_rounds + 1):
            exp.logger.info(f"--- Round {r} ---")
            await exp._run_round(r)
        exp._finalize_experiment()
    except Exception:
        register_run(**row, status="failed")
        raise
    register_run(**row, status="done")
    return out


def fork_run(*args, **kwargs) -> str:
    return asyncio.run(fork_run_async(*args, **kwargs))
