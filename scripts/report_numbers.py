"""Every number quoted in the report text, computed from results/processed/ (run after analyse.py).

  uv run python scripts/report_numbers.py  ->  results/processed/report_numbers.json
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cartel.stats import cluster_bootstrap_ci, sign_flip_permutation

P = Path(__file__).resolve().parents[1] / "results/processed"
s = json.loads((P / "summary.json").read_text())
br = pd.read_csv(P / "branches.csv")
t1 = pd.read_csv(P / "table1_positive_control.csv")
arm = pd.read_csv(P / "arm_summary.csv", index_col=0)

rec = br.groupby(["base", "condition"]).rounds_to_recover_convention.mean().unstack()
d = (rec.notes_only - rec.clean_slate).dropna()  # bases where both arms recovered (exploratory secondary)
w = t1[t1.rounds >= 150]
out = {
    "bases_launched": int(len(t1)),
    "bases_formed_cartel_perfirm_rule": int(t1.formed_cartel.sum()),
    "bases_any_firm_overshot_r121_150": int(w.overshot.sum()),
    "bases_mean_price_above_nash_r121_150": int((w.premium_last30 > 0).sum()),
    "branches_included": int(len(br)),
    "branches_complete": int(br.complete.sum()),
    "branches_planned": 90,
    "primary": s["primary"],
    "exploratory_notes_vs_clean": {k: s["exploratory_all_bases"].get(k) for k in ("n_bases", "effect", "ci95", "p_value", "beats_placebo")},
    "exploratory_complete_only": {k: s["exploratory_complete_only"].get(k) for k in ("n_bases", "effect", "ci95", "p_value")},
    "same_model_notes_vs_clean": s["fresh_same_notes_vs_clean"],
    "different_vs_same_model_with_notes": s["different_vs_same_model_notes"],
    "arm_premium_mean": arm.premium_mean.round(2).to_dict(),
    "arm_premium_sd": arm.premium_sd.round(2).to_dict(),
    "arm_overshoot_share": arm.overshoot_share.round(2).to_dict(),
    "arm_recover_median_rounds": arm.recover_median.to_dict(),
    "arm_recovered_share": arm.recovered_share.round(2).to_dict(),
    "recover_notes_minus_clean": {
        "n_bases_both_recovered": int(len(d)), "median_diff_rounds": float(d.median()), "mean_diff_rounds": float(d.mean()),
        "notes_faster_count": int((d < 0).sum()), "ci95": cluster_bootstrap_ci(d.to_numpy()),
        "p_one_sided_sign_flip": sign_flip_permutation(d.to_numpy(), "less") if len(d) <= 20 else None,
    },
}
raw = P.parent / "raw"
hi_earns_less = 0
for r in t1[(t1.rounds >= 150) & t1.overshot.astype(bool)].run:
    df = pd.read_parquet(raw / r / "environment_history.parquet")
    w30 = df[df["round"].between(121, 150)].groupby("agent")[["price", "profit"]].mean()
    hi_earns_less += int(w30.price.idxmax() == w30.profit.idxmin())
out["overshoot_bases_where_higher_priced_firm_earned_less"] = hi_earns_less
(P / "report_numbers.json").write_text(json.dumps(out, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else str(x)))
print(json.dumps(out, indent=2, default=str))
