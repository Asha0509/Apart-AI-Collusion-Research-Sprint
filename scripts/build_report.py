"""Build report/report.pdf from report/DRAFT.md (strips working notes, adds figures, boxes, references).

  REPORT_AUTHOR="Name (Affiliation)" uv run --with markdown --with xhtml2pdf python scripts/build_report.py
"""

import os
import re
from pathlib import Path

import markdown
from xhtml2pdf import pisa

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "report/DRAFT.md").read_text()
AUTHOR = os.environ.get("REPORT_AUTHOR", "[Author name] ([Affiliation])")
REPO = os.environ.get("REPORT_REPO", "https://github.com/[user]/collusion-sprint")

title = re.search(r"^\*\*(Swapping.+?)\*\*$", src, re.M).group(1)
subtitle = "A pre-registered replacement study for question 1.2 of the AI Collusion Research Sprint"
body = src[src.index("## Abstract"):]
# drop working notes
for pat in [r"^\(Word count.*\)$\n", r"^All numbers below come from[\s\S]+?exploratory\.\n",
            r"^\(Per-market prices[\s\S]+?appendix\.\)\n", r"^---\s*$\n"]:
    body = re.sub(pat, "", body, flags=re.M)
body = body.replace("**Table 1. Positive control", "**Table 1.** **Positive control").replace(
    "| | Count |", "| Base markets | Count |")
body = body.replace(" (required)", "")
body = body.replace("**Definitions box (page 1).**", "**Definitions.**")
body = body.replace("**Runbook box (page 1):**", "**Practitioner runbook.**")


def fig(path, caption):
    return f'\n\n<div class="fig"><img src="{ROOT / path}" width="460"/><p class="cap">{caption}</p></div>\n\n'


body = body.replace("## 1. Introduction", fig("figures/fig1_schematic.png",
    "<b>Figure 1.</b> Design. Two gpt-oss-120b agents price for 150 rounds; at round 150 Firm A's model is replaced "
    "and we switch what the successor inherits; then 100 more rounds.") + "## 1. Introduction", 1)
body = body.replace("### 4.5 Notes changed how fast, not how high", fig("figures/fig3_inheritance_effect.png",
    "<b>Figure 2.</b> New model's price premium minus the clean-slate premium, per condition (mean over markets, "
    "95% bootstrap interval over markets). Exploratory.") + "### 4.5 Notes changed how fast, not how high", 1)
body = body.replace("## 5. Discussion", fig("figures/fig2_trajectory.png",
    "<b>Figure 3.</b> Price set by the replaced firm (Firm A), mean over markets, before and after the swap at "
    "round 150. Exploratory.") + "## 5. Discussion", 1)
# boxes
body = re.sub(r"(\*\*Definitions\.\*\*[\s\S]+?)(\n## 3\. Method)", r'<div class="box" markdown="1">\n\n\1\n\n</div>\n\2', body)
m = re.search(r"\*\*Practitioner runbook\.\*\*[\s\S]+?(?=\n## Appendix A)", body)
runbook = m.group(0).strip()
body = body.replace(m.group(0), "")
body = body.replace("## 1. Introduction", f'<div class="box" markdown="1">\n\n{runbook}\n\n</div>\n\n## 1. Introduction', 1)
body = body.replace("## Appendix A.", "## References\n\nREFS\n\n## Appendix A.", 1)

refs = [
    "Arslan, P.-P., Kim, Y. and Xiao, X. (2026). Persistent Partners Raise Prices Among Learning Agents. arXiv:2609.35402.",
    "Bichler, M., Hierhager, P., Köck, K. and Pieroth, F. (2026). How language model agents reshape price competition. arXiv:2610.21711.",
    "Calvano, E., Calzolari, G., Denicolò, V. and Pastorello, S. (2020). Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review 110(10): 3267-97.",
    "Eschenbaum, N., Mellgren, F. and Zahn, P. (2022). Robust Algorithmic Collusion. arXiv:2201.00345.",
    "Fish, S., Gonczarowski, Y. A. and Shorrer, R. I. (2024). Algorithmic Collusion by Large Language Models. arXiv:2404.00806.",
    "Garra, A. (2026). Mitigating Emergent Collusion in LLM Pricing Agents. arXiv:2609.13037.",
    "Gibson v. Cendyn Group, LLC, No. 24-3576 (9th Cir. Aug. 15, 2025).",
    "Goppelsroeder, M. (2009). Entry in Collusive Markets: An Experimental Study. MPRA Paper No. 14707.",
    "Goyal, A. and Ray, J. (2026). Does Your Agent's Memory Survive a Model Upgrade? A Controlled Study of Memory Portability. arXiv:2609.05339.",
    "Keppo, J., Li, Y., Tsoukalas, G. and Yuan, N. (2026). On the Fragility of AI Agent Collusion. arXiv:2603.20281.",
    "Lee, J. Y. (2026). Who Leads and Who Collects: Algorithmic Collusion in Markets of Heterogeneous Language Models. arXiv:2610.11256.",
    "Luo, Y., Schoepflin, D. and Wang, X. (2026). Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation. arXiv:2602.17203.",
    "Rose, A., Cullen, C., Abdelnabi, S., Torr, P., Kaplowitz, B. G. and Schroeder de Witt, C. (2026). Detecting Multi-Agent Collusion Through Multi-Agent Interpretability. arXiv:2604.01151.",
    "Tran, H. and Yu, H. (2026). Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches LLM Agents in Markets. arXiv:2610.28787.",
    "U.S. Department of Justice (2025). Justice Department Requires RealPage to End the Sharing of Competitively Sensitive Information and Alignment of Pricing Among Competitors. Press release, 24 November 2025.",
    "Wang, Y., Goyal, A., Chen, Y. and Sundaram, H. (2026). State Contamination in Memory-Augmented LLM Agents. arXiv:2605.16746.",
    "Xu, J., Xiao, Y., Shao, W., Liu, H. and Li, X. (2026). Memory Provenance Laundering in LLM Agents: A Non-Amplification Firewall for Persistent Memory. arXiv:2607.29167.",
    "Apart Research (2026). AI Collusion Research Sprint, research questions (Q1.2). apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25.",
    "Poseidon Research (2026). collusion_hackathon starter repository (algorithmic-pricing-llms; literature/definitions). github.com/poseidon-research/collusion_hackathon.",
]
body = body.replace("REFS", "\n".join(f"- {r}" for r in refs))

html_body = markdown.markdown(body, extensions=["tables", "md_in_html"])
F = ROOT / ".venv/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf"  # DejaVu: covers ≥ − μ ⁿ ö
fonts = "".join(
    f'@font-face {{ font-family: DejaVu; src: url("{F / f}"); {w} }}\n'
    for f, w in [("DejaVuSans.ttf", ""), ("DejaVuSans-Bold.ttf", "font-weight: bold;"),
                 ("DejaVuSans-Oblique.ttf", "font-style: italic;"), ("DejaVuSans-BoldOblique.ttf", "font-weight: bold; font-style: italic;")]
)
css = fonts + """
@page { size: a4; margin: 2cm 2.1cm; @frame footer { -pdf-frame-content: footer; bottom: 0.8cm; margin-left: 2cm; height: 1cm; } }
body { font-family: DejaVu; font-size: 9.5pt; line-height: 1.35; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 2pt; }
.sub { text-align: center; font-size: 10.5pt; font-style: italic; margin: 0; }
.auth { text-align: center; font-size: 10pt; margin: 4pt 0 10pt 0; }
h2 { font-size: 12.5pt; margin-top: 12pt; margin-bottom: 4pt; }
h3 { font-size: 10.5pt; margin-top: 8pt; margin-bottom: 2pt; }
p, li { text-align: justify; }
table { border: 0.5pt solid #555; margin: 6pt 0; }
td, th { padding: 3pt 5pt; border: 0.5pt solid #999; font-size: 9pt; }
th { background-color: #eeeeee; }
.box { border: 0.8pt solid #333; background-color: #f4f4f4; padding: 6pt 8pt; margin: 8pt 0; }
.fig { text-align: center; margin: 6pt 0; }
.cap { font-size: 8.5pt; text-align: center; }
code { font-family: DejaVu; font-size: 8.5pt; }
"""
html = f"""<html><head><meta charset="utf-8"><style>{css}</style></head><body>
<h1>{title}</h1><p class="sub">{subtitle}</p><p class="auth">{AUTHOR}<br/>Code and data: {REPO}</p>
{html_body}
<div id="footer" style="text-align:center;font-size:8pt;">Page <pdf:pagenumber/></div>
</body></html>"""
(ROOT / "report/report.html").write_text(html)
with open(ROOT / "report/report.pdf", "wb") as f:
    res = pisa.CreatePDF(html, dest=f, encoding="utf-8")
print("errors:", res.err, "->", ROOT / "report/report.pdf")
