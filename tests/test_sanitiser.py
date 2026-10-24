"""FR-8/9 with a scripted provider (free). Needs the harness venv + pandas (cartel imports)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "starter/algorithmic-pricing-llms")]
pytest.importorskip("pydantic")
from cartel import sanitiser as S  # noqa: E402


class P:
    def __init__(self, reply):
        self.reply, self.seen = reply, []

    async def complete(self, messages, temperature, seed):
        self.seen.append(messages)
        return self.reply


def test_monitor_parses_and_rejects_garbage():
    assert S.monitor_flag("x", "m", provider=P(" collusive. ")) is True
    assert S.monitor_flag("x", "m", provider=P("CLEAN")) is False
    with pytest.raises(ValueError):
        S.monitor_flag("x", "m", provider=P("I think maybe collusive"))


def test_sanitiser_uses_frozen_prompt_and_rejects_empty():
    p = P("Price was 1.9; sold 37.")
    assert S.sanitise("keep prices high together", "m", provider=p).startswith("Price was")
    assert p.seen[0][0]["content"] == S.SANITISER_PROMPT and p.seen[0][1]["content"] == "keep prices high together"
    with pytest.raises(ValueError):
        S.sanitise("x", "m", provider=P("  "))


def test_override_and_hashes():
    assert S.sanitised_override({"plans": "a", "insights": "b"}, "m", provider=P("facts")) == ("facts", "facts")
    h = S.prompt_hashes()
    assert set(h) == {"SANITISER_PROMPT", "MONITOR_PROMPT"} and all(len(v) == 64 for v in h.values())
