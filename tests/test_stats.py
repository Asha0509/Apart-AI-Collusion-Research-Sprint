import numpy as np
import pytest

from cartel.stats import (
    cluster_bootstrap_ci,
    declare_inheritance,
    minimum_detectable_effect,
    sign_flip_permutation,
)


def test_permutation_all_positive_is_min_p():
    d = np.ones(10)
    assert sign_flip_permutation(d) == pytest.approx(1 / 2**10)


def test_permutation_null_is_large():
    d = np.array([1, -1] * 5, dtype=float)
    assert sign_flip_permutation(d) > 0.4


def test_bootstrap_contains_mean():
    v = np.random.default_rng(1).normal(0.3, 0.1, 12)
    lo, hi = cluster_bootstrap_ci(v)
    assert lo < v.mean() < hi


def test_mde_positive():
    assert 0 < minimum_detectable_effect(0.2, 12) < 1


def test_decision_rule():
    strong = np.full(12, 0.3) + np.random.default_rng(0).normal(0, 0.02, 12)
    assert declare_inheritance(strong, strong)["declared"]
    assert not declare_inheritance(strong * 0.1, strong)["declared"]  # below 0.15
