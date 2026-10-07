"""Mnemosyne 0.7 retention-state classification.

Classification is advisory lifecycle metadata. It never deletes memory and never
changes memory authority.
"""

from __future__ import annotations

from .phoenix_metadata import PhoenixRetentionState


RETENTION_HOT_MIN_SCORE = 0.75
RETENTION_WARM_MIN_SCORE = 0.50
RETENTION_COLD_MIN_SCORE = 0.25


def classify_retention_state(
    score: float,
    *,
    is_current: bool = True,
    protected: bool = False,
) -> PhoenixRetentionState:
    """Map a bounded score plus lifecycle flags to a retention state.

    Safety rules:
    - protected always wins;
    - current memories never become archive candidates solely from a low score;
    - archive_candidate is advisory only and does not delete or prune anything.
    """

    bounded = max(0.0, min(1.0, float(score)))

    if protected:
        return PhoenixRetentionState.PROTECTED
    if bounded >= RETENTION_HOT_MIN_SCORE:
        return PhoenixRetentionState.HOT
    if bounded >= RETENTION_WARM_MIN_SCORE:
        return PhoenixRetentionState.WARM
    if bounded >= RETENTION_COLD_MIN_SCORE:
        return PhoenixRetentionState.COLD
    if is_current:
        return PhoenixRetentionState.COLD
    return PhoenixRetentionState.ARCHIVE_CANDIDATE
