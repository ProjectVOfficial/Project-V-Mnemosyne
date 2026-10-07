"""Deterministic Mnemosyne 0.7 memory scoring.

Scoring affects retrieval preference only. It never grants execution authority
and never deletes memory.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import pow

from pydantic import BaseModel, ConfigDict, Field

from .phoenix_metadata import (
    PhoenixVerification,
    RETENTION_CONTRADICTION_PENALTY,
    RETENTION_STALENESS_PENALTY,
    RETENTION_WEIGHT_CONFIDENCE,
    RETENTION_WEIGHT_CORROBORATION,
    RETENTION_WEIGHT_ENVIRONMENT,
    RETENTION_WEIGHT_RECENCY,
    RETENTION_WEIGHT_UTILITY,
    RETENTION_WEIGHT_VERIFICATION,
)


RETENTION_RECENCY_HALF_LIFE_DAYS = 30.0
RETENTION_RECENCY_FLOOR = 0.15
RETENTION_CORROBORATION_TARGET = 3

VERIFICATION_STRENGTH: dict[PhoenixVerification, float] = {
    PhoenixVerification.UNVERIFIED: 0.20,
    PhoenixVerification.SELF_REPORTED: 0.40,
    PhoenixVerification.OBSERVED: 0.65,
    PhoenixVerification.COMMAND_VERIFIED: 0.90,
    PhoenixVerification.TEST_VERIFIED: 1.00,
    PhoenixVerification.OPERATOR_CONFIRMED: 1.00,
}


class PhoenixRetentionScore(BaseModel):
    """Explainable deterministic score before retention-state classification."""

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    verification_strength: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    corroboration: float = Field(ge=0.0, le=1.0)
    utility: float = Field(ge=0.0, le=1.0)
    environment_match: float = Field(ge=0.0, le=1.0)
    staleness_penalty: float = Field(ge=0.0, le=1.0)
    contradiction_penalty: float = Field(ge=0.0, le=1.0)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def verification_strength(verification: PhoenixVerification) -> float:
    return VERIFICATION_STRENGTH[verification]


def recency_score(
    observed_at: str | None,
    *,
    now: datetime,
    half_life_days: float = RETENTION_RECENCY_HALF_LIFE_DAYS,
    floor: float = RETENTION_RECENCY_FLOOR,
) -> float:
    """Return bounded exponential time decay with an explicit non-zero floor."""

    if observed_at is None:
        return floor

    try:
        observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        return floor

    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)

    normalized_now = now
    if normalized_now.tzinfo is None:
        normalized_now = normalized_now.replace(tzinfo=timezone.utc)

    age_seconds = max(0.0, (normalized_now - observed).total_seconds())
    age_days = age_seconds / 86400.0
    raw = pow(0.5, age_days / half_life_days)
    return _clamp01(max(floor, raw))


def corroboration_score(independent_support_count: int) -> float:
    """Normalize independent corroboration; duplicates are counted upstream."""

    count = max(0, int(independent_support_count))
    return _clamp01(count / RETENTION_CORROBORATION_TARGET)


def score_memory(
    *,
    verification: PhoenixVerification,
    confidence: float,
    observed_at: str | None,
    now: datetime,
    independent_support_count: int = 0,
    utility: float = 0.5,
    environment_match: float = 0.5,
    stale: bool = False,
    unresolved_disputed: bool = False,
) -> PhoenixRetentionScore:
    """Compute an explainable, bounded retrieval score.

    This function is intentionally pure: no deletion, no mutation, no authority
    decisions, and no hidden model judgment.
    """

    confidence = _clamp01(confidence)
    utility = _clamp01(utility)
    environment_match = _clamp01(environment_match)

    verify = verification_strength(verification)
    recency = recency_score(observed_at, now=now)
    corroboration = corroboration_score(independent_support_count)

    positive = (
        verify * RETENTION_WEIGHT_VERIFICATION
        + confidence * RETENTION_WEIGHT_CONFIDENCE
        + recency * RETENTION_WEIGHT_RECENCY
        + corroboration * RETENTION_WEIGHT_CORROBORATION
        + utility * RETENTION_WEIGHT_UTILITY
        + environment_match * RETENTION_WEIGHT_ENVIRONMENT
    )

    stale_penalty = RETENTION_STALENESS_PENALTY if stale else 0.0
    contradiction_penalty = (
        RETENTION_CONTRADICTION_PENALTY if unresolved_disputed else 0.0
    )
    score = _clamp01(positive - stale_penalty - contradiction_penalty)

    return PhoenixRetentionScore(
        score=score,
        verification_strength=verify,
        confidence=confidence,
        recency=recency,
        corroboration=corroboration,
        utility=utility,
        environment_match=environment_match,
        staleness_penalty=stale_penalty,
        contradiction_penalty=contradiction_penalty,
    )
