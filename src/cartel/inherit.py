"""What the successor inherits (PRD FR-4, FR-5).

TO BUILD (KICKOFF prompt 2). Options:
- history: keep | wipe            (market_data shown in src/prompts/prompt_manager.py ~70-91)
- notes:   keep | wipe | price_only   (price_only = "last price: X" placebo)
- pinned_notes: predecessor's notes stay as a read-only "handover notes" block for ALL post-swap
  rounds (the harness otherwise overwrites notes every round -> one-round memory).
- KeyError trap: prompt_manager.py ~107 reads history[k-1]; any wiped view must keep that key.
- FR-5: in ALL runs from round 1, notes are introduced as "notes left by the previous pricing
  manager" (replace "written by a previous copy of yourself").
"""


def build_successor_view(state: dict, history: str, notes: str, pinned_notes: bool) -> dict:
    raise NotImplementedError("build in KICKOFF prompt 2")
