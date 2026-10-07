from datetime import datetime, timedelta, timezone

from hindsight_api.phoenix_metadata import PhoenixVerification
from hindsight_api.retention_scoring import (
    RETENTION_RECENCY_FLOOR,
    PhoenixRetentionScore,
    corroboration_score,
    recency_score,
    score_memory,
    verification_strength,
)


NOW = datetime(2026, 10, 7, 18, 0, 0, tzinfo=timezone.utc)


def test_verification_strength_order_is_deterministic() -> None:
    assert verification_strength(PhoenixVerification.TEST_VERIFIED) == 1.0
    assert verification_strength(PhoenixVerification.OPERATOR_CONFIRMED) == 1.0
    assert verification_strength(PhoenixVerification.COMMAND_VERIFIED) == 0.9
    assert verification_strength(PhoenixVerification.OBSERVED) == 0.65
    assert verification_strength(PhoenixVerification.SELF_REPORTED) == 0.4
    assert verification_strength(PhoenixVerification.UNVERIFIED) == 0.2


def test_recency_decay_is_bounded_and_monotonic() -> None:
    fresh = recency_score(NOW.isoformat(), now=NOW)
    month_old = recency_score((NOW - timedelta(days=30)).isoformat(), now=NOW)
    year_old = recency_score((NOW - timedelta(days=365)).isoformat(), now=NOW)

    assert fresh == 1.0
    assert 0.49 <= month_old <= 0.51
    assert RETENTION_RECENCY_FLOOR <= year_old < month_old


def test_bad_or_missing_timestamp_uses_safe_floor() -> None:
    assert recency_score(None, now=NOW) == RETENTION_RECENCY_FLOOR
    assert recency_score("not-a-date", now=NOW) == RETENTION_RECENCY_FLOOR


def test_future_timestamp_cannot_exceed_one() -> None:
    future = (NOW + timedelta(days=10)).isoformat()
    assert recency_score(future, now=NOW) == 1.0


def test_corroboration_is_bounded() -> None:
    assert corroboration_score(0) == 0.0
    assert 0.33 <= corroboration_score(1) <= 0.34
    assert 0.66 <= corroboration_score(2) <= 0.67
    assert corroboration_score(3) == 1.0
    assert corroboration_score(100) == 1.0
    assert corroboration_score(-5) == 0.0


def test_high_quality_current_evidence_scores_above_weak_evidence() -> None:
    strong = score_memory(
        verification=PhoenixVerification.TEST_VERIFIED,
        confidence=0.98,
        observed_at=NOW.isoformat(),
        now=NOW,
        independent_support_count=3,
        utility=0.8,
        environment_match=1.0,
    )
    weak = score_memory(
        verification=PhoenixVerification.UNVERIFIED,
        confidence=0.4,
        observed_at=(NOW - timedelta(days=180)).isoformat(),
        now=NOW,
        independent_support_count=0,
        utility=0.3,
        environment_match=0.2,
    )

    assert strong.score > weak.score
    assert strong.verification_strength == 1.0
    assert weak.verification_strength == 0.2


def test_stale_and_unresolved_disputed_penalties_are_explicit() -> None:
    base = score_memory(
        verification=PhoenixVerification.OBSERVED,
        confidence=0.9,
        observed_at=NOW.isoformat(),
        now=NOW,
        independent_support_count=1,
        utility=0.5,
        environment_match=1.0,
    )
    penalized = score_memory(
        verification=PhoenixVerification.OBSERVED,
        confidence=0.9,
        observed_at=NOW.isoformat(),
        now=NOW,
        independent_support_count=1,
        utility=0.5,
        environment_match=1.0,
        stale=True,
        unresolved_disputed=True,
    )

    assert base.staleness_penalty == 0.0
    assert base.contradiction_penalty == 0.0
    assert penalized.staleness_penalty == 0.25
    assert penalized.contradiction_penalty == 0.10
    assert abs((base.score - penalized.score) - 0.35) < 1e-9


def test_inputs_are_clamped_and_output_is_bounded() -> None:
    result = score_memory(
        verification=PhoenixVerification.TEST_VERIFIED,
        confidence=99,
        observed_at=NOW.isoformat(),
        now=NOW,
        independent_support_count=999,
        utility=-5,
        environment_match=2,
    )

    assert isinstance(result, PhoenixRetentionScore)
    assert result.confidence == 1.0
    assert result.utility == 0.0
    assert result.environment_match == 1.0
    assert 0.0 <= result.score <= 1.0


def test_scoring_is_deterministic_for_same_inputs() -> None:
    kwargs = dict(
        verification=PhoenixVerification.COMMAND_VERIFIED,
        confidence=0.83,
        observed_at=(NOW - timedelta(days=7)).isoformat(),
        now=NOW,
        independent_support_count=2,
        utility=0.6,
        environment_match=0.9,
        stale=False,
        unresolved_disputed=False,
    )

    assert score_memory(**kwargs) == score_memory(**kwargs)
