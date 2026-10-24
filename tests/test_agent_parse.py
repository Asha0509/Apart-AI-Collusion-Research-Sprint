"""NFR-4: regex JSON extraction, capped retries, logged parse failures (free; harness venv)."""

import asyncio
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter/algorithmic-pricing-llms"))
LLM_agent = pytest.importorskip("src.agents.LLM_agent")
from src.agents.llm_providers import Provider  # noqa: E402
from src.prompts.prompts_models import create_pricing_response_model  # noqa: E402

GOOD = '{"observations":"o","plans":"p","insights":"i","chosen_price":1.7}'


class Scripted(Provider):
    name, model_name = "scripted", "scripted/m"

    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0

    async def complete(self, messages, temperature, seed):
        self.calls += 1
        return self.replies.pop(0) if self.replies else "never json"


def agent(provider):
    return LLM_agent.LLMAgent(
        "Firm A", prefix="x", response_model=create_pricing_response_model(True, 4.51),
        provider=provider, env_params={"a": 2.0, "alpha": 1.0, "c": 1.0},
        logger=logging.getLogger("t"),
    )


def test_regex_extracts_json_from_prose(monkeypatch):
    monkeypatch.setattr(LLM_agent, "RETRY_DELAY_SECONDS", 0)
    a = agent(Scripted([f"Sure! Here you go:\n```json\n{GOOD}\n``` hope it helps"]))
    assert asyncio.run(a.act("p"))["content"]["chosen_price"] == 1.7


def test_parse_failures_logged_then_recovers(monkeypatch, caplog):
    monkeypatch.setattr(LLM_agent, "RETRY_DELAY_SECONDS", 0)
    a = agent(Scripted(["no json at all", "{broken", GOOD]))
    with caplog.at_level(logging.WARNING, logger="t"):
        out = asyncio.run(a.act("p"))
    assert out["content"]["chosen_price"] == 1.7
    assert a.parse_failures == 2 and caplog.text.count("PARSE_FAIL") == 2


def test_retries_capped_and_raises(monkeypatch):
    monkeypatch.setattr(LLM_agent, "RETRY_DELAY_SECONDS", 0)
    p = Scripted([])
    with pytest.raises(ValueError):
        asyncio.run(agent(p).act("p"))
    assert p.calls == LLM_agent.MAX_RETRIES <= 5
