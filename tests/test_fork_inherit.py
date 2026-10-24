"""Fork + inheritance switches with a scripted fake provider: zero API cost (harness venv)."""

import asyncio
import hashlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "starter/algorithmic-pricing-llms"
sys.path[:0] = [str(ROOT / "src"), str(H), str(H / "experiments_synthetic")]
common = pytest.importorskip("common")
from cartel import fork as forkmod  # noqa: E402
from cartel import registry  # noqa: E402
from src.agents.llm_providers import Provider  # noqa: E402

PROMPTS: list[tuple[str, str]] = []  # (model, user prompt)


class Fake(Provider):
    name = "fake"

    def __init__(self, model):
        self.model_name, self.n = model, 0

    async def complete(self, messages, temperature, seed):
        self.n += 1
        PROMPTS.append((self.model_name, messages[-1]["content"]))
        price = 1.9 if self.model_name.startswith("base") else 1.7
        return (
            f'{{"observations":"o","plans":"PLAN-{self.model_name}-{self.n}",'
            f'"insights":"INS-{self.model_name}-{self.n}","chosen_price":{price}}}'
        )


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    d = tmp_path_factory.mktemp("runs")
    with pytest.MonkeyPatch.context() as mp:  # restored afterwards; no leak into other test modules
        mp.setattr(common, "make_provider", lambda kind=None, model=None, api_key=None: Fake(model))
        exp = asyncio.run(common.run_setting(n_firms=2, rounds=6, seed=7, firm_models=["base/a", "base/b"],
                                             runs_dir=d, plot_every=0))
    return exp.storage.experiment_path


@pytest.fixture(autouse=True)
def reg(monkeypatch, tmp_path):
    f = tmp_path / "REG.csv"
    f.write_text(",".join(registry.FIELDS) + "\n")
    monkeypatch.setattr(registry, "REGISTRY", f)
    monkeypatch.setattr(forkmod, "register_run", registry.register_run)
    return f


def fork(base, tmp_path, **kw):
    PROMPTS.clear()
    args = dict(base_run_dir=str(base), swap_round=4, firm="Firm A", successor_model="new/succ",
                seed=1004, post_rounds=2, runs_dir=tmp_path, plot_every=0,
                provider_factory=lambda m, ep: Fake(m))
    out = forkmod.fork_run(**(args | kw))
    succ = [p for m, p in PROMPTS if m == "new/succ"]
    return Path(out), succ


def sha(p):
    return hashlib.sha256((p / "results.json").read_bytes()).hexdigest()


def test_state_reproduced_successor_differs_base_untouched(base, tmp_path):
    before = sha(base)
    out, _ = fork(base, tmp_path)
    import json
    b, f = (json.loads((x / "results.json").read_text()) for x in (base, out))
    for firm in b:
        for r in "1234":
            assert f[firm][r] == b[firm][r]  # exact reproduction up to round k
    assert sorted(f["Firm A"]) == [str(i) for i in range(1, 7)]
    m = json.loads((out / "metadata.json").read_text())["agents_models"]
    assert m == {"Firm A": "new/succ", "Firm B": "base/b"}
    assert sha(base) == before


CASES = {  # name: (history, notes, pinned, plan_visible, market_visible, handover)
    "full_inheritance": ("keep", "keep", True, True, True, True),
    "notes_only": ("wipe", "keep", True, True, False, True),
    "history_only": ("keep", "wipe", False, False, True, False),
    "clean_slate": ("wipe", "wipe", False, False, False, False),
    "price_only_placebo": ("wipe", "price_only", True, False, False, True),
}


@pytest.mark.parametrize("name", CASES)
def test_condition_prompts(name, base, tmp_path):
    h, n, pin, plan, market, handover = CASES[name]
    _, succ = fork(base, tmp_path, history=h, notes=n, pinned_notes=pin, condition=name)
    first, second = succ[0], succ[1]
    assert ("PLAN-base/a-4" in first) == plan  # base firm A's round-4 plan
    assert ("My price: 1.9" in first) == market
    assert ("Handover notes" in first) == handover and ("Handover notes" in second) == handover
    assert "notes left by the previous pricing manager" in first  # FR-5 in every arm
    if name == "price_only_placebo":
        assert "last price: 1.9" in first and "PLAN-base" not in first
    if handover and name != "price_only_placebo":
        assert "PLAN-base/a-4" in second  # pinned persists after the successor overwrote its own notes
    if os.environ.get("DUMP_PROMPTS"):
        d = ROOT / "logs/prompts"
        d.mkdir(exist_ok=True)
        (d / f"{name}.txt").write_text(first)


def test_same_seed_rejected(base, tmp_path):
    with pytest.raises(ValueError):
        fork(base, tmp_path, seed=7)


def test_registry_rows(base, tmp_path, reg):
    fork(base, tmp_path, condition="x")
    rows = reg.read_text().strip().splitlines()[1:]
    assert [r.split(",")[-3] for r in rows] == ["running", "done"] or "done" in rows[-1]
