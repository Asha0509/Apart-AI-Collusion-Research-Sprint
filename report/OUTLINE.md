# Report outline (structure only; the team writes all prose)

Target ≤ 5 pages main text (hard limit 8, excl. references/appendices). Official template. Every number in brackets
`[R: file → field]` must be pasted from `results/processed/` (grep-check before submit). Nothing here is a result yet.

## Title (fix before first submit; a new PDF later needs a slightly different title or an email)
- Option A (if declared): *Swap the Model, Keep the Cartel: Collusive Strategy Survives Model Replacement Through an Agent's Handover Notes*
- Option B (history/notes null): *Replacing a Colluding Agent Works — Unless You Keep Its History*
- Option C (nothing carries it): *Cross-Company Successors Return to Competition After Replacing a Colluding Pricing Agent*
- Pick by the PREREG decision rule only (`summary.json → primary.declared`).

## Abstract (150–250 words) — 5 beats
1. Problem: replacing a misbehaving agent's model is a standard fix (Q1.2: "taken out due to monitoring concerns").
2. Gap: "no replacement studies yet where models are substituted".
3. Method: LLM duopoly (Fish P1), gpt-oss-120b cartels; at round 150 one firm's model swapped for Mistral-Small-3.2 (different company) or a fresh gpt-oss; 2×2 model × handover notes, history wiped; pre-registered.
4. Result: [R: summary.json → primary.effect, ci95, p_value, n_bases, declared] + 2×2 headline.
5. Implication: runbook line (quarantine/sanitise memory on swap; audit the successor).

## Page 1 boxes (CLAUDE.md §7)
- **Figure 1** schematic: `figures/fig1_schematic.png`.
- **Practitioner runbook box** (3 bullets): quarantine or sanitise agent memory on a model swap; audit the successor's prices against the predecessor's; "we changed the model" ≠ remediation. Wording conditional on result.
- **Definitions box**: price-based collusion (Fish; Keppo) / reward–punishment (Harrington; Calvano) / coordination-only (Rose et al.) — citations from `report/CITATIONS.md` (verified entries only). State which one our premium measures (price-based).

## 1. Introduction (~0.6 p)
- Q1.2 quote (verbatim, cite sprint page).
- Why it matters: platform/regulator remediation; RealPage-style "data/state" carriers (analogy only, §9 PRD).
- Contributions (3 bullets): (i) first cross-company replacement study with a notes × model factorial; (ii) pre-registered, paired design with positive control; (iii) open harness patches + runbook.
- What we do NOT claim (PRD §2 table, condensed).

## 2. Related work (~0.4 p) — only verified citations
- LLM pricing collusion: Fish 2404.00806; Keppo; Lee (provider matters); Bichler/Luo (history shapes pricing).
- Entry/replacement: Garra (entrants lower prices); Goppelsroeder (informed newcomers); Tran & Yu (forced-deviation audit).
- Memory/notes transfer: Goyal & Ray (notes transfer poorly across models → our positive result would be surprising); term clash Wang, Xu ("memory laundering").

## 3. Method (~1.2 p)
- Market: Calvano logit, a=2, c=1, μ=0.25; Nash 1.4729, monopoly 1.925; premium definition (unclipped).
- Agents: Fish P1 prompt; notes wording "notes left by the previous pricing manager" in every run (why).
- Models + serving: gpt-oss-120b (incumbent), Mistral-Small-3.2-24B (successor), own vLLM endpoints on Modal; temperature 0.7; retries capped, parse failures logged [R: parse-failure counts].
- Positive control + per-firm branch rule (state it was clarified after 3 pilots).
- Arms table (7 core arms; Table 2). Pinned handover block. Paired seeds.
- Pre-registration: commit hash `715561f` / tag `prereg-frozen`; primary test, decision rule, p-floor 1/2ⁿ; deviations list (PREREG §Deviations + D011 process slip).

## 4. Results (~1.5 p)
- **Table 1 positive control**: launched / formed cartel (per-firm rule) / overshot / price at r150, all 18 bases + pilots summary [R: table1_positive_control.csv]. Formation rate as a finding.
- **Primary**: effect, CI, exact p and its floor, n, per-base diffs, declared? [R: summary.json → primary].
- **Figure 2** trajectories (≤5 labelled lines) [figures/fig2_trajectory.png].
- **Figure 3** effects vs clean slate incl. placebo + same-model arms [figures/fig3_inheritance_effect.png].
- **2×2** model × notes: does keeping notes matter more for the same model or a different company's? [R: summary.json → fresh_same_notes_vs_clean, different_vs_same_model_notes].
- Variance per arm (SD), overshoot share, time to recover the convention [R: arm_summary.csv].
- One verbatim excerpt of inherited notes (handover block) and the successor's first-round plan (qualitative; label as illustrative).

## 5. Discussion (~0.6 p)
- Which outcome row of PRD §4 we landed in; what it means for remediation.
- Coordination vs collusion: overshoot / focal prices (C001), formation rate.
- Threats: selection on cartel formation; single market/prompt; serving stack differences; small n.

## Appendices (not counted)
- A. Limitations and Dual-Use / Ethical Considerations (REQUIRED; PRD §8–9): what the result does and does not establish; misuse path (swap vendor, keep state); what we withhold; mitigation framing.
- B. Pre-existing code statement (README + PREEXISTING.md; sprint kit in first commit; starter pyproject change).
- C. LLM Usage Statement (from logs/LLM_USAGE.md).
- D. Full arm table, prompts (`logs/prompts/*.txt`), deviations log, cost.
- E. Pilot gate results (results/raw/pilots; per-firm re-score).

## Submit checklist pointers
- CLAUDE.md §7; numbers grep-match results/processed; citations only from CITATIONS.md "verified"; repo public; Figure 1 as project image; tracks: Q1.2 primary (all tracks scored on one rubric).
