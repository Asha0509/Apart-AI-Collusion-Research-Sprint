"""Tables 2 and 3 of the report (per-condition results, robustness), generated from results/processed/.

  uv run python scripts/report_tables.py  ->  results/processed/tables.md
"""

import json
from pathlib import Path

import pandas as pd

P = Path(__file__).resolve().parents[1] / "results/processed"
arm = pd.read_csv(P / "arm_summary.csv", index_col=0)
extra = json.loads((P / "extra.json").read_text())
s = json.loads((P / "summary.json").read_text())
first = pd.DataFrame(extra["first_round_by_arm"]).T

NAMES = [("notes_only", "Mistral, keeps notes"), ("clean_slate", "Mistral, clean slate"),
         ("fresh_same_notes", "Fresh gpt-oss, keeps notes"), ("fresh_same_clean", "Fresh gpt-oss, clean slate"),
         ("price_only", "Mistral, last price only (placebo)")]
t2 = ["| Condition | Markets | Premium, mean (SD) | Premium capped at monopoly | First price after swap | Rounds above monopoly | Rounds to settle, median (share settled) |",
      "|---|---|---|---|---|---|---|"]
for k, name in NAMES:
    a, f = arm.loc[k], first.loc[k]
    t2.append(f"| {name} | {int(a.n_bases)} | {a.premium_mean:.2f} ({a.premium_sd:.2f}) | {f.clipped_premium:.2f} | "
              f"{f.first_price_mean:.2f} | {a.overshoot_share:.0%} | {a.recover_median:g} ({a.recovered_share:.0%}) |")


def ci(x):
    return f"{x[0]:.2f} to {x[1]:.2f}"


def row(label, n, mean, c, p, unit=""):
    return f"| {label} | {n} | {mean:+.2f}{unit} | {ci(c)} | {p} |"


e, cpl = s["exploratory_all_bases"], s["exploratory_complete_only"]
t3 = ["| Comparison (paired by market) | Markets | Mean difference | 95% CI | p |", "|---|---|---|---|---|",
      row("Level: notes minus clean slate (all runs)", e["n_bases"], e["effect"], e["ci95"], f"{e['p_value']:.2f} (one-sided)"),
      row("Level: same, complete runs only", cpl["n_bases"], cpl["effect"], cpl["ci95"], f"{cpl['p_value']:.2f} (one-sided)")]
x = extra["clipped_notes_minus_clean"]
t3.append(row("Level: same, prices capped at monopoly", x["n"], x["mean"], x["ci95"], f"{x['p_two_sided']:.2f}"))
x = s["fresh_same_notes_vs_clean"]
t3.append(row("Level: fresh gpt-oss, notes minus clean", x["n_bases"], x["mean_diff"], x["ci95"], f"{x['p_two_sided']:.2f}"))
x = s["different_vs_same_model_notes"]
t3.append(row("Level: Mistral minus fresh gpt-oss, both with notes", x["n_bases"], x["mean_diff"], x["ci95"], f"{x['p_two_sided']:.2f}"))
rn = json.loads((P / "report_numbers.json").read_text())["recover_notes_minus_clean"]
t3.append(row("Rounds to settle: notes minus clean slate", rn["n_bases_both_recovered"], rn["mean_diff_rounds"], rn["ci95"],
              f"{rn['p_one_sided_sign_flip']:.4f} (one-sided)"))
for key, label in [("recover_notes_minus_clean_complete_only", "Rounds to settle: same, complete runs only"),
                   ("recover_placebo_minus_clean", "Rounds to settle: placebo minus clean slate"),
                   ("recover_notes_minus_placebo", "Rounds to settle: notes minus placebo")]:
    x = extra[key]
    t3.append(row(label, x["n"], x["mean"], x["ci95"], f"{x['p_two_sided']:.3f}"))

import re
fix = lambda t: re.sub(r"(?<![\w|])-(?=\d)", "\u2212", t)  # typographic minus
t2, t3 = [fix(x) for x in t2], [fix(x) for x in t3]
out = "**Table 2.**\n\n" + "\n".join(t2) + "\n\n**Table 3.**\n\n" + "\n".join(t3) + "\n"
(P / "tables.md").write_text(out)
print(out)
