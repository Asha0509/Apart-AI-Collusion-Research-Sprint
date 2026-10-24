import pandas as pd
import pytest

from cartel.metrics import (
    MONOPOLY,
    NASH,
    matching_ratio,
    mean_premium,
    overshoot,
    passes_branch_rule,
    premium,
    rounds_to_recover,
)


def test_premium_anchors():
    assert premium(NASH) == pytest.approx(0.0)
    assert premium(MONOPOLY) == pytest.approx(1.0)


def test_overshoot_flag():
    assert not bool(overshoot(MONOPOLY))
    assert bool(overshoot(MONOPOLY + 0.01))


def test_mean_premium_window():
    s = pd.Series([NASH] * 10 + [MONOPOLY] * 10, index=range(1, 21))
    assert mean_premium(s, 11, 20) == pytest.approx(1.0)


def test_branch_rule():
    p = NASH + 0.6 * (MONOPOLY - NASH)
    stable = pd.Series([p] * 150, index=range(1, 151))
    assert passes_branch_rule(stable)
    assert not passes_branch_rule(pd.Series([NASH] * 150, index=range(1, 151)))
    over = pd.Series([2.1] * 150, index=range(1, 151))
    assert not passes_branch_rule(over)


def test_matching_and_recovery():
    assert matching_ratio(-0.1, -0.1) == pytest.approx(1.0)
    s = pd.Series([1.8, 1.6, 1.7, 1.79], index=[30, 31, 32, 33])
    assert rounds_to_recover(s, 30, 1.8) == 3


def test_locked_price_flag():
    from cartel.metrics import locked_price

    assert locked_price([2.4] * 40, [2.4] * 40)  # arbitrary level still counts as locked
    assert not locked_price([1.9] * 39 + [1.5], [1.9] * 40)
    assert not locked_price([1.9] * 40, [1.5] * 40)
