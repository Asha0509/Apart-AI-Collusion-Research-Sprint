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


def test_guard_per_provider(tmp_path, monkeypatch):
    from cartel import registry as R

    log = tmp_path / "COST.csv"
    log.write_text("time_ist,batch,est_usd,actual_usd,cumulative_usd,notes\nx,old,50,,50,untagged\n")
    monkeypatch.setattr(R, "COSTLOG", log)
    R.guard_batch("b1", 4.0, provider="modal")  # untagged old row ignored
    R.log_cost("b1", 4.0, 3.0, "provider=modal")  # actual replaces estimate
    assert R.spent_so_far("modal") == 3.0
    with pytest.raises(RuntimeError):
        R.guard_batch("b2", 10.0, provider="modal")  # > $5 without approval
    with pytest.raises(RuntimeError):
        R.guard_batch("b3", 71.0, approved=True, provider="modal")  # over cap


def test_branch_rule_per_firm_catches_hidden_overshoot():
    from cartel.metrics import passes_branch_rule, passes_branch_rule_firms

    r = range(1, 151)
    df = pd.DataFrame({"A": [1.95] * 150, "B": [1.75] * 150}, index=r)  # A overshoots; the mean (1.85) does not
    assert passes_branch_rule(df.mean(axis=1), 150)
    assert not passes_branch_rule_firms(df, 150)
    ok = pd.DataFrame({"A": [1.80] * 150, "B": [1.78] * 150}, index=r)
    assert passes_branch_rule_firms(ok, 150)
