"""analyse.py on synthetic run dirs with known premiums (free, root env)."""

import csv
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from cartel.metrics import MONOPOLY, NASH
from cartel.registry import FIELDS

spec = importlib.util.spec_from_file_location("analyse", Path(__file__).resolve().parents[1] / "scripts/analyse.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

K = 150


def price(prem):
    return NASH + prem * (MONOPOLY - NASH)


def make_run(root, name, base, cond, prem, status="done"):
    d = root / name
    d.mkdir()
    rows = [dict(round=r, agent=a, price=(price(prem) if (a == "Firm A" and r > K) else 1.8), profit=1.0)
            for r in range(1, K + 101) for a in ("Firm A", "Firm B")]
    pd.DataFrame(rows).to_parquet(d / "environment_history.parquet")
    (d / "metadata.json").write_text(json.dumps({"fork": dict(condition=cond, base_run_dir=f"/x/{base}", swap_round=K,
                                     firm="Firm A", seed=1000, successor_model="s/m", forced_prices=None)}))
    return dict(run_id=name, condition=cond, status=status)


@pytest.fixture
def world(tmp_path):
    rows = []
    for i in range(6):
        b = f"base{i}"
        rows += [make_run(tmp_path, f"{b}_n", b, "notes_only", 0.6 + 0.01 * i),
                 make_run(tmp_path, f"{b}_c", b, "clean_slate", 0.1),
                 make_run(tmp_path, f"{b}_p", b, "price_only", 0.2)]
    rows.append(make_run(tmp_path, "smoke", "base0", "smoke_notes_only", 5.0))  # never counted
    rows.append(make_run(tmp_path, "failed", "base0", "notes_only", 5.0, status="failed"))  # never counted
    reg = tmp_path / "REG.csv"
    with reg.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows([{k: r.get(k, "") for k in FIELDS} for r in rows])
    return sorted(p for p in tmp_path.glob("*") if p.is_dir()), A.latest_registry(reg)


def test_primary_matches_constructed_effect(world):
    runs, reg = world
    br = A.branch_rows(runs, reg)
    assert len(br) == 18  # smoke + failed excluded
    res = A.primary(A.per_base(br))
    assert res["n_bases"] == 6
    assert res["effect"] == pytest.approx(0.525, abs=1e-9)  # mean(0.60..0.65) - 0.10
    assert res["declared"] is True and res["p_value"] == pytest.approx(1 / 64)


def test_incomplete_bases_not_used(world):
    runs, reg = world
    br = A.branch_rows(runs, reg)
    br = br[~((br.base == "base0") & (br.condition == "clean_slate"))]
    assert A.primary(A.per_base(br))["n_bases"] == 5


def test_figures_from_synthetic(world, tmp_path, monkeypatch):
    import importlib.util as u

    runs, reg = world
    br = A.branch_rows(runs, reg)
    s = u.spec_from_file_location("mf", Path(__file__).resolve().parents[1] / "scripts/make_figures.py")
    MF = u.module_from_spec(s)
    s.loader.exec_module(MF)
    monkeypatch.setattr(MF, "RAW", runs[0].parent)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "figures").mkdir()
    MF.fig2(br, 150)
    tab = A.per_base(br)
    MF.fig3(tab)
    assert (tmp_path / "figures/fig2_trajectory.png").exists() and (tmp_path / "figures/fig3_inheritance_effect.png").exists()


def test_floor_dropped_and_arm_summary(world):
    runs, reg = world
    br = A.branch_rows(runs, reg)
    br = br[~((br.base == "base0") & (br.condition == "clean_slate"))]
    res = A.primary(A.per_base(br))
    assert res["p_floor"] == 0.5 ** 5 and res["dropped"] == {"base0": ["clean_slate"]}
    s = A.arm_summary(br)
    assert s.loc["clean_slate", "n_bases"] == 5 and s.loc["notes_only", "premium_sd"] > 0
    assert "recover_median" in s
