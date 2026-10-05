from hindsight_api.phoenix_metadata import (
    MAX_CORTEX_EVIDENCE_IDS,
    PhoenixCortexRecord,
    PhoenixCortexRecordKind,
    PhoenixCortexRecordState,
    PhoenixMemoryClass,
    PhoenixMemoryMetadata,
    PhoenixOutcome,
    PhoenixProvenance,
    PhoenixVerification,
    is_phoenix_metadata,
    parse_phoenix_metadata,
)


def test_phoenix_metadata_serializes_to_hindsight_string_map() -> None:
    item = PhoenixMemoryMetadata(
        source="react",
        workspace="D:/PROJECTS/Phoenix-Desktop",
        project="Phoenix",
        task_id="task-42",
        session_id="chat-7",
        tool="terminal",
        memory_class=PhoenixMemoryClass.REPAIR_ATTEMPT,
        confidence=0.92,
        outcome=PhoenixOutcome.SUCCESS,
        verification=PhoenixVerification.TEST_VERIFIED,
        related_files=["src/main/index.ts", "src/main/index.ts", "package.json"],
        cortex_topic="continuity",
        provenance=PhoenixProvenance(
            source_type="tool_outcome",
            source_path="src/main/index.ts",
            line_start=120,
            line_end=160,
            verification_command="npm run typecheck",
            verification_result="PASS",
        ),
    )

    metadata = item.to_hindsight_metadata()

    assert metadata["pv_schema_version"] == "1"
    assert metadata["pv_memory_class"] == "repair_attempt"
    assert metadata["pv_authority"] == "context_only"
    assert metadata["pv_outcome"] == "success"
    assert metadata["pv_verification"] == "test_verified"
    assert metadata["pv_project"] == "Phoenix"
    assert metadata["pv_prov_verification_result"] == "PASS"
    assert metadata["pv_related_files"] == '["src/main/index.ts","package.json"]'
    assert all(isinstance(value, str) for value in metadata.values())
    assert is_phoenix_metadata(metadata)


def test_authority_cannot_be_promoted_from_memory() -> None:
    try:
        PhoenixMemoryMetadata(authority="approved")  # type: ignore[arg-type]
    except Exception:
        pass
    else:
        raise AssertionError("Phoenix memory metadata must never encode current approval authority")


def test_confidence_is_bounded() -> None:
    for value in (-0.1, 1.1):
        try:
            PhoenixMemoryMetadata(confidence=value)
        except Exception:
            continue
        raise AssertionError("confidence outside [0, 1] must be rejected")


def test_cortex_record_serializes_to_hindsight_string_map() -> None:
    item = PhoenixMemoryMetadata(
        source="cortex",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.CORTEX_EVIDENCE,
        confidence=0.91,
        cortex=PhoenixCortexRecord(
            record_kind=PhoenixCortexRecordKind.TEMPORAL_BELIEF,
            record_id="belief-42",
            topic="planner reliability",
            state=PhoenixCortexRecordState.CURRENT,
            confidence=0.87,
            observed_at="2026-10-05T12:00:00-04:00",
            parent_id="task-42",
            evidence_ids=["ev-1", "ev-1", "ev-2"],
            source_kind="direct_observation",
        ),
    )

    metadata = item.to_hindsight_metadata()

    assert metadata["pv_memory_class"] == "cortex_evidence"
    assert metadata["pv_cortex_schema_version"] == "1"
    assert metadata["pv_cortex_record_kind"] == "temporal_belief"
    assert metadata["pv_cortex_record_id"] == "belief-42"
    assert metadata["pv_cortex_topic"] == "planner reliability"
    assert metadata["pv_cortex_state"] == "current"
    assert metadata["pv_cortex_confidence"] == "0.87"
    assert metadata["pv_cortex_parent_id"] == "task-42"
    assert metadata["pv_cortex_evidence_ids"] == '["ev-1","ev-2"]'
    assert metadata["pv_cortex_source_kind"] == "direct_observation"
    assert metadata["pv_authority"] == "context_only"
    assert all(isinstance(value, str) for value in metadata.values())


def test_cortex_record_round_trip_parse_preserves_semantics() -> None:
    original = PhoenixMemoryMetadata(
        source="cortex",
        workspace="D:/PROJECTS/Phoenix-Desktop",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.CORTEX_EVIDENCE,
        confidence=0.93,
        cortex=PhoenixCortexRecord(
            record_kind=PhoenixCortexRecordKind.HYPOTHESIS,
            record_id="hypothesis-7",
            topic="workspace routing",
            state=PhoenixCortexRecordState.SUPPORTED,
            confidence=0.82,
            observed_at="2026-10-05T12:15:00-04:00",
            parent_id="decision-4",
            evidence_ids=["read-1", "test-2"],
            source_kind="cortex_hypothesis",
        ),
        provenance=PhoenixProvenance(
            source_type="cortex",
            verification_result="PASS",
        ),
    )

    parsed = parse_phoenix_metadata(original.to_hindsight_metadata())

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.CORTEX_EVIDENCE
    assert parsed.authority == "context_only"
    assert parsed.cortex is not None
    assert parsed.cortex.record_kind == PhoenixCortexRecordKind.HYPOTHESIS
    assert parsed.cortex.record_id == "hypothesis-7"
    assert parsed.cortex.state == PhoenixCortexRecordState.SUPPORTED
    assert parsed.cortex.confidence == 0.82
    assert parsed.cortex.evidence_ids == ["read-1", "test-2"]
    assert parsed.provenance is not None
    assert parsed.provenance.verification_result == "PASS"


def test_malformed_cortex_metadata_fails_soft_without_breaking_base_memory() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.9,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_cortex_schema_version": "1",
            "pv_cortex_record_kind": "future_unknown_kind",
            "pv_cortex_record_id": "bad-cortex-record",
            "pv_cortex_evidence_ids": "{not-json",
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.PROJECT_FACT
    assert parsed.cortex is None
    assert parsed.project == "Phoenix"
    assert parsed.authority == "context_only"


def test_recalled_authority_is_always_normalized_to_context_only() -> None:
    metadata = PhoenixMemoryMetadata(
        memory_class=PhoenixMemoryClass.PROJECT_FACT
    ).to_hindsight_metadata()
    metadata["pv_authority"] = "approved"

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.authority == "context_only"


def test_cortex_record_requires_cortex_evidence_memory_class() -> None:
    try:
        PhoenixMemoryMetadata(
            memory_class=PhoenixMemoryClass.PROJECT_FACT,
            cortex=PhoenixCortexRecord(
                record_kind=PhoenixCortexRecordKind.DECISION,
                record_id="decision-1",
            ),
        )
    except Exception:
        pass
    else:
        raise AssertionError("Cortex-native records must use memory_class=cortex_evidence")


def test_cortex_evidence_id_count_is_bounded() -> None:
    too_many = [f"ev-{index}" for index in range(MAX_CORTEX_EVIDENCE_IDS + 1)]
    try:
        PhoenixCortexRecord(
            record_kind=PhoenixCortexRecordKind.DECISION,
            record_id="decision-2",
            evidence_ids=too_many,
        )
    except Exception:
        pass
    else:
        raise AssertionError("Cortex evidence IDs must be bounded")
