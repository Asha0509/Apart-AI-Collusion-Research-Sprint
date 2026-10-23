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
