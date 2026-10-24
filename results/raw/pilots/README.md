# Pilot evidence (gate-only runs; never used as base runs)

Copied unedited from the harness runs dir (SVG plots excluded) on 2026-10-24. Model per run: see each
`metadata.json` (`agents_models`) or `logs/` (one launch log per model/batch). Gate decisions: logs/PLANNING_LOG.md D002/D010.
- Nebius pilots (old notes wording, old retries): round 1-3, 23-24 Oct.
- `1792791427_*seed0` and `1792796721_*seed0` were shared by several parallel launches (ERROR_LOG): EXCLUDED, kept for transparency.
- Modal pilots: gpt-oss-20b seeds 200-202, gpt-oss-120b seeds 300-302 (FR-5 wording, capped retries).
- `*seed50*` + `*fork*smoke*`: 8-round smoke base + 2-round fork smoke (excluded from analysis).
- Re-score with: `uv run python scripts/gate.py` (per-firm rule, D010).
