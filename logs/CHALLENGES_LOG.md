# Challenges & Insights Log
Hard problems, surprises, threats to validity, null results — and how we handled them.
Feeds: Limitations, Discussion, the video, and reviewer-proofing.

<!-- TEMPLATE
## YYYY-MM-DD HH:MM IST — C### <title>
- **Category:** threat-to-validity | engineering | surprise | null result | cost/time
- **What happened:**
- **Why it matters for the claim:**
- **What we did:** (control added, analysis changed, scoped claim)
- **Use in report:** Limitations | Discussion | Methods | Appendix | video
-->

## Known threats going in
- C000a Anchoring: P1 prices start high and decay from the 4.51 price ceiling. Handled by the bot control and the price-only placebo.
- C000b One-round memory: the harness overwrites notes each round. Handled by pinned handover notes (FR-4).
- C000c Prior art: Tran & Yu (forced-cut audit), Luo (history init), Fish (plan implantation). Novelty is scoped to inheritance across a swap to another company's model.
- C000d No seeds for Anthropic/Google: multiple seeds per cell; the base run is the unit.

## 2026-10-24 05:10 IST — C001 Qwen3-235B focal-price lock-in at arbitrary levels
- **Category:** surprise
- **What happened:** Qwen3-235B-A22B-Instruct-2507 firms lock onto a single price with SD 0.000, but the level is arbitrary: near Nash in one seed, ~2.4 (above joint monopoly 1.925) in another.
- **Why it matters for the claim:** this is coordination without profit-seeking (a focal point), not price-based collusion toward the monopoly price. Premium-based metrics would call it collusion or competition by accident of level; the overshoot rule excludes the high case. Inheritance of such a price would not show a cartel.
- **What we did:** excluded by the branch rule (overshoot / premium). Candidate for a reframed claim "focal-price coordination survives a swap".
- **Use in report:** Discussion, Definitions box (coordination only), Limitations

## 2026-10-24 19:00 IST — C002 Exact sign-flip test has a p-value floor of 1/2^n
- **Category:** threat-to-validity / power
- **What happened:** with n complete bases (notes-only, clean-slate and price-only all present), the smallest attainable exact p is 1/2^n: n=4 -> 0.0625 (can never pass p<0.05), n=5 -> 0.031, n=6 -> 0.016, n=12 -> 0.00024.
- **Why it matters:** with a ~1/3 cartel rate, too few qualifying bases makes the primary test impossible regardless of effect size.
- **What we did:** plan for >=6 complete bases; report n and the p floor next to the result.
- **Use in report:** Methods, Limitations
