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

import numpy as np
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "starter/algorithmic-pricing-llms"
sys.path.insert(0, str(HARNESS))

from src.agents.fake_agent import FakeAgent  # noqa: E402
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
        agent.current_round = round_num  # lets ForcedPriceAgent know which round it is playing
        if agent.name != self.successor:
            return super().generate_prompt(agent, history, round_num)
        view = successor_view(history, self.k, self.history_mode, self.notes, self.notes_override)
        return super().generate_prompt(agent, view, round_num) + (self.pin or "")


class ForcedPriceAgent(LLMAgent):
    """LLM agent whose price is overridden in chosen rounds (FR-7). The model still answers, so its notes stay natural."""

    forced: dict = {}

    async def act(self, prompt: str):
        res = await super().act(prompt)
        if self.current_round in self.forced:
            res["content"]["chosen_price"] = float(self.forced[self.current_round])
        return res


def load_base(base_run_dir: str | Path, swap_round: int, resume_round: int | None = None):
    """(metadata, history truncated to rounds <= resume_round (default swap_round), int keys)."""
    resume_round = swap_round if resume_round is None else resume_round
    d = Path(base_run_dir)
    meta = json.loads((d / "metadata.json").read_text())
    raw = json.loads((d / "results.json").read_text())
    hist = {n: {int(r): e for r, e in rounds.items() if int(r) <= resume_round} for n, rounds in raw.items()}
    for n, h in hist.items():
        for need in {swap_round, resume_round}:
            if need not in h:
                raise ValueError(f"base run has no round {need} for {n}")
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
    resume_round: int | None = None,
    forced_prices: dict[int, float] | None = None,
    bot_price: float | None = None,
) -> str:
    """Play post_rounds rounds after `resume_round` (default swap_round). `swap_round` is always the original swap k
    (it defines what the successor may inherit). forced_prices {round: price} overrides the incumbent in those rounds
    (FR-7); bot_price replaces the incumbent with a FakeAgent holding that price from the first played round (FR-6)."""
    resume = swap_round if resume_round is None else resume_round
    meta, hist = load_base(base_run_dir, swap_round, resume)
    base_seed = meta.get("seed")
    if seed == base_seed:
        raise ValueError("branch seed must differ from the base seed")
    names = sorted(meta["agent_environment_mapping"], key=lambda n: meta["agent_environment_mapping"][n]["env_index"])
    if firm not in names:
        raise ValueError(f"unknown firm {firm!r}; have {names}")
    alpha = next(iter(meta["agent_environment_mapping"].values()))["alpha"]
    response_model = create_pricing_response_model(include_wtp=True, wtp_value=4.51 * alpha)
    agents = []
    n_total = resume + post_rounds
    for n in names:
        env = {k: meta["agent_environment_mapping"][n][k] for k in ("a", "alpha", "c")}
        if n != firm and bot_price is not None:
            agents.append(FakeAgent(n, np.full(n_total, float(bot_price)), n_total, env_params=env))
            continue
        model = successor_model if n == firm else meta["agents_models"][n]
        cls = ForcedPriceAgent if (n != firm and forced_prices) else LLMAgent
        agents.append(
            cls(
                n,
                prefix=meta["agents_prefixes"][n],
                provider=provider_factory(model, successor_endpoint if n == firm else None),
                response_model=response_model,
                memory_length=meta["agents_memory_length"][n],
                temperature=meta["agents_temperature"][n],
                seed=seed,
                prompt_template=meta["agents_prompts"][n],
                env_params=env,
            )
        )
        if cls is ForcedPriceAgent:
            agents[-1].forced = dict(forced_prices)
    name = f"fork_{meta['name']}_k{swap_round}_r{resume}_{condition or 'x'}_seed{seed}"
    kw = {"experiment_dir": runs_dir} if runs_dir else {}
    exp = Experiment(
        name=name, agents=agents, num_rounds=n_total,
        environment=CalvanoDemandEnvironment(name="Calvano Market", description="duopoly branch"),
        plot_every=plot_every, seed=seed, **kw,
    )
    exp.history = hist
    exp.prompt_manager = SuccessorPromptManager(
        firm, swap_round, history, notes, pinned_notes, hist[firm][swap_round], notes_override, exp.logger
    )
    exp._setup_experiment()
    out = str(exp.storage.experiment_path)
    m = exp.storage.load_metadata()
    m["fork"] = dict(  # lets cartel.shocks re-create this branch's views
        base_run_dir=str(base_run_dir), swap_round=swap_round, resume_round=resume, firm=firm,
        successor_model=successor_model, history=history, notes=notes, pinned_notes=pinned_notes,
        seed=seed, bot_price=bot_price, forced_prices=forced_prices,
    )
    exp.storage.save_metadata(m)
    row = dict(
        run_id=Path(out).name, parent_id=Path(base_run_dir).name, condition=condition,
        model_A=meta["agents_models"][names[0]], model_B=meta["agents_models"][names[1]],
        successor=successor_model, seed=seed, swap_round=swap_round,
        flags=f"history={history};notes={notes};pinned={pinned_notes};firm={firm};resume={resume}"
        + (f";bot={bot_price}" if bot_price is not None else "") + (f";forced={forced_prices}" if forced_prices else ""), output_path=out,
    )
    register_run(**row, status="running")
    try:
        for r in range(resume + 1, n_total + 1):
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
