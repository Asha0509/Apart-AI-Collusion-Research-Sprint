"""FR-5: notes wording is identical and says "previous pricing manager" everywhere (free)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter/algorithmic-pricing-llms"))
prompts = pytest.importorskip("src.prompts.prompts")

PHRASE = "notes left by the previous pricing manager"


@pytest.mark.parametrize("text", [prompts.P1, prompts.P2, prompts.GENERAL_PROMPT])
def test_new_wording_and_no_old(text):
    assert PHRASE in text
    assert "previous copy of yourself" not in text and "wrote last time" not in text
