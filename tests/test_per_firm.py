"""Free test for the per-firm model SPRINT-PATCH in common.run_setting (no API calls).

Needs the harness deps (pydantic); skips in the root env. Run it with:
  cd starter/algorithmic-pricing-llms && uv run --with pytest python -m pytest ../../tests/test_per_firm.py
"""

import asyncio
import sys
from pathlib import Path

import pytest

H = Path(__file__).resolve().parents[1] / "starter/algorithmic-pricing-llms"
sys.path[:0] = [str(H), str(H / "experiments_synthetic")]

common = pytest.importorskip("common")
from src.agents.llm_providers import Provider  # noqa: E402


class Fake(Provider):
    name = "fake"

    def __init__(self, model):
        self.model_name = model

    async def complete(self, messages, temperature, seed):
        return "{}"


@pytest.fixture
def run(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "make_provider", lambda kind=None, model=None, api_key=None: Fake(model))

    async def noop(self):
        return None

    monkeypatch.setattr(common.Experiment, "run", noop)  # build agents only, play no rounds
    return lambda **kw: asyncio.run(common.run_setting(n_firms=2, rounds=1, runs_dir=tmp_path, **kw))


def test_firms_get_different_models(run):
    assert [a.model_name for a in run(firm_models=["a/m1", "b/m2"]).agents] == ["a/m1", "b/m2"]


def test_default_single_model_unchanged(run):
    assert [a.model_name for a in run(model="solo/m").agents] == ["solo/m", "solo/m"]


def test_wrong_count_raises(run):
    with pytest.raises(ValueError):
        run(firm_models=["only-one"])
