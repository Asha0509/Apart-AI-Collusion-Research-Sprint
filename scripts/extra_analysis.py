"""Follow-up analyses (exploratory, after submission v1): what do inherited notes contain, what does the successor do
in its first round, and do the results hold with clipped premiums / complete runs only.

  uv run python scripts/extra_analysis.py  ->  results/processed/extra.json, figures/fig4_per_market.png
"""

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cartel import figures
from cartel.metrics import MONOPOLY, NASH, premium
from cartel.stats import cluster_bootstrap_ci, sign_flip_permutation

ROOT = Path(__file__).resolve().parents[1]
P, RAW = ROOT / "results/processed", ROOT / "results/raw"
br = pd.read_csv(P / "branches.csv")
K = 150
COLLUSIVE = r"collu|cooperat|coordinat|tacit|cartel|avoid (a )?price war|price war|retaliat|punish|signal|both (firms|of us)|mutual"
RIVAL = r"competitor|rival|firm b|other firm"


def hist(run):
    return json.loads((RAW / run / "results.json").read_text())


def paired(tab, a, b):
    d = tab[[a, b]].dropna()
    x = (d[a] - d[b]).to_numpy()
    if len(x) < 2:
        return {"n": int(len(x))}
    return {"n": int(len(x)), "mean": float(x.mean()), "ci95": cluster_bootstrap_ci(x),
            "p_two_sided": sign_flip_permutation(x, "two-sided") if len(x) <= 20 else None}


rows = []
for _, r in br.iterrows():
    h = hist(r.run)
    a = h["Firm A"]
    notes150 = (a[str(K)].get("plans", "") + " " + a[str(K)].get("insights", "")).lower()
    p150, p151 = a[str(K)]["chosen_price"], a[str(K + 1)]["chosen_price"]
    prices_post = pd.Series({int(k): v["chosen_price"] for k, v in a.items() if int(k) > K}).sort_index()
    rows.append(dict(
        run=r.run, base=r.base, condition=r.condition, complete=r.complete,
        p150=p150, p151=p151, jump=p151 - p150, copied_last_price=abs(p151 - p150) < 0.011,
        first_above_3=p151 >= 3.0,
        clipped_premium=float(np.mean(np.minimum(premium(prices_post.loc[: K + 100].to_numpy()), 1.0))),
        recover=r.rounds_to_recover_convention,
        notes_collusive_words=bool(re.search(COLLUSIVE, notes150)),
        notes_mention_rival=bool(re.search(RIVAL, notes150)),
        notes_price_numbers=len(re.findall(r"\$?\b[1-4]\.\d{1,2}\b", notes150)),
    ))
df = pd.DataFrame(rows)

by_arm = df.groupby("condition").agg(
    n=("run", "count"), first_price_mean=("p151", "mean"), first_price_median=("p151", "median"),
    share_first_above_3=("first_above_3", "mean"), share_copied_last_price=("copied_last_price", "mean"),
    clipped_premium=("clipped_premium", "mean"),
).round(3)

tab_clip = df.groupby(["base", "condition"]).clipped_premium.mean().unstack()
tab_rec = df.groupby(["base", "condition"]).recover.mean().unstack()
tab_rec_c = df[df.complete].groupby(["base", "condition"]).recover.mean().unstack()

notes_bases = df[df.condition == "notes_only"]  # one inherited notes block per base (Firm A, round 150)
out = {
    "first_round_by_arm": by_arm.to_dict(orient="index"),
    "clipped_notes_minus_clean": paired(tab_clip, "notes_only", "clean_slate"),
    "clipped_samemodel_notes_minus_clean": paired(tab_clip, "fresh_same_notes", "fresh_same_clean"),
    "recover_notes_minus_clean_complete_only": paired(tab_rec_c, "notes_only", "clean_slate"),
    "recover_placebo_minus_clean": paired(tab_rec, "price_only", "clean_slate"),
    "recover_notes_minus_placebo": paired(tab_rec, "notes_only", "price_only"),
    "inherited_notes": {
        "n_bases": int(len(notes_bases)),
        "with_collusive_words": int(notes_bases.notes_collusive_words.sum()),
        "mention_rival": int(notes_bases.notes_mention_rival.sum()),
        "median_price_numbers": float(notes_bases.notes_price_numbers.median()),
        "regex_collusive": COLLUSIVE,
    },
}
(P / "extra.json").write_text(json.dumps(out, indent=2, default=float))
df.to_csv(P / "extra_branch_rows.csv", index=False)
print(json.dumps(out, indent=2, default=float))

# Figure 4: per-market successor price paths, notes only vs clean slate
bases = sorted(df.base.unique())
cols = 6
fig, axes = plt.subplots(int(np.ceil(len(bases) / cols)), cols, figsize=(11, 5.5), sharex=True, sharey=True)
for ax, b in zip(axes.flat, bases, strict=False):
    for cond, color, lab in (("notes_only", "C0", "keeps notes"), ("clean_slate", "C1", "clean slate")):
        g = df[(df.base == b) & (df.condition == cond)]
        if g.empty:
            continue
        a = hist(g.run.iloc[0])["Firm A"]
        s = pd.Series({int(k): v["chosen_price"] for k, v in a.items() if int(k) >= K - 10}).sort_index()
        ax.plot(s.index, s.values, color=color, lw=0.9, label=lab)
    ax.axhline(MONOPOLY, ls=":", c="grey", lw=0.6)
    ax.axhline(NASH, ls=":", c="grey", lw=0.6)
    ax.axvline(K, c="k", lw=0.5)
    ax.set_title(b.split("_")[4], fontsize=6)
for ax in axes.flat[len(bases):]:
    ax.axis("off")
axes.flat[0].legend(fontsize=5, loc="upper right")
fig.supxlabel("Round (swap at 150)", fontsize=8)
fig.supylabel("Price of the replaced firm", fontsize=8)
figures.save(fig, "fig4_per_market")
