"""A4: provider counts tokens and Experiment writes metadata['usage_tokens'] (free; harness venv)."""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter/algorithmic-pricing-llms"))
prov = pytest.importorskip("src.agents.llm_providers")


def test_usage_accumulates():
    p = prov.OpenAICompatibleProvider(preset="openai-compatible", model="m/x", base_url="http://localhost:1/v1", api_key="k")

    async def create(**kw):
        return NS(choices=[NS(message=NS(content='{"a":1}'))], usage=NS(prompt_tokens=100, completion_tokens=7))

    p._client = NS(chat=NS(completions=NS(create=create)))
    for _ in range(3):
        asyncio.run(p.complete([{"role": "user", "content": "hi"}], 0.7, None))
    assert (p.tokens_in, p.tokens_out, p.n_calls) == (300, 21, 3)
