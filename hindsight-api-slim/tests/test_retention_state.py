from hindsight_api.phoenix_metadata import PhoenixRetentionState
from hindsight_api.retention_state import (
    RETENTION_COLD_MIN_SCORE,
    RETENTION_HOT_MIN_SCORE,
    RETENTION_WARM_MIN_SCORE,
    classify_retention_state,
)


def test_retention_thresholds_are_explicit_and_ordered() -> None:
    assert RETENTION_HOT_MIN_SCORE == 0.75
    assert RETENTION_WARM_MIN_SCORE == 0.50
    assert RETENTION_COLD_MIN_SCORE == 0.25
    assert (
        RETENTION_HOT_MIN_SCORE
        > RETENTION_WARM_MIN_SCORE
        > RETENTION_COLD_MIN_SCORE
    )


def test_hot_warm_cold_classification_is_deterministic() -> None:
    assert classify_retention_state(0.976) == PhoenixRetentionState.HOT
    assert classify_retention_state(0.75) == PhoenixRetentionState.HOT
    assert classify_retention_state(0.74) == PhoenixRetentionState.WARM
    assert classify_retention_state(0.50) == PhoenixRetentionState.WARM
    assert classify_retention_state(0.49) == PhoenixRetentionState.COLD
    assert classify_retention_state(0.25) == PhoenixRetentionState.COLD


def test_current_low_score_memory_is_not_archive_candidate() -> None:
    assert classify_retention_state(0.2125, is_current=True) == PhoenixRetentionState.COLD
    assert classify_retention_state(0.0, is_current=True) == PhoenixRetentionState.COLD


def test_noncurrent_low_score_memory_can_be_archive_candidate() -> None:
    assert (
        classify_retention_state(0.2125, is_current=False)
        == PhoenixRetentionState.ARCHIVE_CANDIDATE
    )
    assert (
        classify_retention_state(0.0, is_current=False)
        == PhoenixRetentionState.ARCHIVE_CANDIDATE
    )


def test_protected_always_wins_regardless_of_score_or_currentness() -> None:
    for score in (0.0, 0.2, 0.5, 1.0):
        assert (
            classify_retention_state(score, is_current=False, protected=True)
            == PhoenixRetentionState.PROTECTED
        )


def test_score_input_is_clamped_before_classification() -> None:
    assert classify_retention_state(99.0) == PhoenixRetentionState.HOT
    assert (
        classify_retention_state(-99.0, is_current=False)
        == PhoenixRetentionState.ARCHIVE_CANDIDATE
    )


def test_controlled_07c_scores_classify_as_expected() -> None:
    assert classify_retention_state(0.976, is_current=True) == PhoenixRetentionState.HOT
    assert classify_retention_state(0.375, is_current=True) == PhoenixRetentionState.COLD
    assert classify_retention_state(0.2125, is_current=True) == PhoenixRetentionState.COLD
    assert (
        classify_retention_state(0.2125, is_current=False)
        == PhoenixRetentionState.ARCHIVE_CANDIDATE
    )
