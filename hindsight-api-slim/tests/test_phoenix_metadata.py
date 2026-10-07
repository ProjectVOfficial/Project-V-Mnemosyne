from hindsight_api.phoenix_metadata import (
    MAX_CLAIM_RELATION_IDS,
    PHOENIX_RETENTION_SCORE_VERSION,
    RETENTION_CONTRADICTION_PENALTY,
    RETENTION_STALENESS_PENALTY,
    RETENTION_WEIGHT_CONFIDENCE,
    RETENTION_WEIGHT_CORROBORATION,
    RETENTION_WEIGHT_ENVIRONMENT,
    RETENTION_WEIGHT_RECENCY,
    RETENTION_WEIGHT_UTILITY,
    RETENTION_WEIGHT_VERIFICATION,
    MAX_CORTEX_EVIDENCE_IDS,
    MAX_TOOL_LEARNING_EVIDENCE_IDS,
    PhoenixClaimLineage,
    PhoenixClaimResolutionState,
    PhoenixClaimState,
    PhoenixCortexRecord,
    PhoenixCortexRecordKind,
    PhoenixCortexRecordState,
    PhoenixMemoryClass,
    PhoenixMemoryMetadata,
    PhoenixRetentionMetadata,
    PhoenixRetentionState,
    PhoenixOutcome,
    PhoenixToolLearningKind,
    PhoenixToolLearningRecord,
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



def test_tool_learning_record_serializes_to_hindsight_string_map() -> None:
    item = PhoenixMemoryMetadata(
        source="react",
        project="Phoenix",
        tool="terminal",
        memory_class=PhoenixMemoryClass.REPAIR_ATTEMPT,
        confidence=0.94,
        outcome=PhoenixOutcome.SUCCESS,
        verification=PhoenixVerification.TEST_VERIFIED,
        tool_learning=PhoenixToolLearningRecord(
            record_kind=PhoenixToolLearningKind.REPAIR_ATTEMPT,
            record_id="repair-42",
            tool_name="terminal",
            operation="repair TypeScript verification failure",
            attempt=2,
            parent_id="task-42",
            previous_attempt_id="repair-41",
            failure_signature="TS2322 assignment mismatch",
            error_class="TypeScriptDiagnostic",
            error_code="TS2322",
            repair_summary="Corrected the incompatible assignment and reran typecheck.",
            evidence_ids=["typecheck-1", "typecheck-1", "typecheck-2"],
            observed_at="2026-10-06T04:45:00Z",
        ),
    )

    metadata = item.to_hindsight_metadata()

    assert metadata["pv_memory_class"] == "repair_attempt"
    assert metadata["pv_tool_learning_schema_version"] == "1"
    assert metadata["pv_tool_learning_record_kind"] == "repair_attempt"
    assert metadata["pv_tool_learning_record_id"] == "repair-42"
    assert metadata["pv_tool_learning_tool_name"] == "terminal"
    assert metadata["pv_tool_learning_attempt"] == "2"
    assert metadata["pv_tool_learning_previous_attempt_id"] == "repair-41"
    assert metadata["pv_tool_learning_error_code"] == "TS2322"
    assert metadata["pv_tool_learning_evidence_ids"] == '["typecheck-1","typecheck-2"]'
    assert metadata["pv_authority"] == "context_only"
    assert all(isinstance(value, str) for value in metadata.values())


def test_tool_learning_round_trip_preserves_semantics() -> None:
    original = PhoenixMemoryMetadata(
        source="tool",
        workspace="D:/PROJECTS/Phoenix-Desktop",
        project="Phoenix",
        tool="workspace.command",
        memory_class=PhoenixMemoryClass.SUCCESS_PATTERN,
        confidence=0.96,
        outcome=PhoenixOutcome.SUCCESS,
        verification=PhoenixVerification.COMMAND_VERIFIED,
        tool_learning=PhoenixToolLearningRecord(
            record_kind=PhoenixToolLearningKind.SUCCESS_PATTERN,
            record_id="success-pattern-7",
            tool_name="workspace.command",
            operation="run bounded verification after repair",
            attempt=3,
            parent_id="repair-chain-7",
            previous_attempt_id="repair-attempt-2",
            success_pattern="After the repair, rerun the narrow verification gate before broader regression.",
            evidence_ids=["gate-pass-7"],
            observed_at="2026-10-06T04:50:00Z",
        ),
        provenance=PhoenixProvenance(
            source_type="tool_outcome",
            verification_command="npm run typecheck",
            verification_result="PASS",
            tool_output_hash="ABCDEF",
        ),
    )

    parsed = parse_phoenix_metadata(original.to_hindsight_metadata())

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.SUCCESS_PATTERN
    assert parsed.authority == "context_only"
    assert parsed.tool_learning is not None
    assert parsed.tool_learning.record_kind == PhoenixToolLearningKind.SUCCESS_PATTERN
    assert parsed.tool_learning.record_id == "success-pattern-7"
    assert parsed.tool_learning.attempt == 3
    assert parsed.tool_learning.previous_attempt_id == "repair-attempt-2"
    assert parsed.tool_learning.evidence_ids == ["gate-pass-7"]
    assert parsed.provenance is not None
    assert parsed.provenance.tool_output_hash == "abcdef"


def test_tool_learning_kind_requires_matching_memory_class() -> None:
    try:
        PhoenixMemoryMetadata(
            memory_class=PhoenixMemoryClass.TOOL_RESULT,
            tool_learning=PhoenixToolLearningRecord(
                record_kind=PhoenixToolLearningKind.FAILURE,
                record_id="failure-1",
            ),
        )
    except Exception:
        pass
    else:
        raise AssertionError("Tool-learning record kind must map to its Phoenix memory class")


def test_tool_learning_evidence_id_count_is_bounded() -> None:
    too_many = [f"ev-{index}" for index in range(MAX_TOOL_LEARNING_EVIDENCE_IDS + 1)]
    try:
        PhoenixToolLearningRecord(
            record_kind=PhoenixToolLearningKind.TOOL_OUTCOME,
            record_id="tool-1",
            evidence_ids=too_many,
        )
    except Exception:
        pass
    else:
        raise AssertionError("Tool-learning evidence IDs must be bounded")


def test_malformed_tool_learning_metadata_fails_soft_without_breaking_base_memory() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.9,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_tool_learning_schema_version": "1",
            "pv_tool_learning_record_kind": "future_unknown_kind",
            "pv_tool_learning_record_id": "bad-tool-record",
            "pv_tool_learning_evidence_ids": "{not-json",
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.PROJECT_FACT
    assert parsed.tool_learning is None
    assert parsed.project == "Phoenix"
    assert parsed.authority == "context_only"


def test_tool_learning_and_cortex_envelopes_cannot_coexist_on_write() -> None:
    try:
        PhoenixMemoryMetadata(
            memory_class=PhoenixMemoryClass.CORTEX_EVIDENCE,
            cortex=PhoenixCortexRecord(
                record_kind=PhoenixCortexRecordKind.DECISION,
                record_id="decision-native-1",
            ),
            tool_learning=PhoenixToolLearningRecord(
                record_kind=PhoenixToolLearningKind.TOOL_OUTCOME,
                record_id="tool-native-1",
            ),
        )
    except Exception:
        pass
    else:
        raise AssertionError("Cortex and tool-learning native envelopes must be mutually exclusive")

def test_claim_lineage_serializes_to_hindsight_string_map() -> None:
    item = PhoenixMemoryMetadata(
        source="manual",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.95,
        claim=PhoenixClaimLineage(
            claim_key="phoenix:active-memory-provider",
            state=PhoenixClaimState.DISPUTED,
            value="mnemosyne",
            value_hash="A" * 64,
            supports_ids=["fact-1", "fact-1", "fact-2"],
            contradicts_ids=["fact-old"],
            supersedes_ids=["fact-legacy"],
            resolution_state=PhoenixClaimResolutionState.UNRESOLVED,
            resolution_basis="Conflicting observed evidence remains unresolved.",
            observed_at="2026-10-07T11:45:00-05:00",
        ),
    )

    metadata = item.to_hindsight_metadata()

    assert metadata["pv_claim_schema_version"] == "1"
    assert metadata["pv_claim_key"] == "phoenix:active-memory-provider"
    assert metadata["pv_claim_state"] == "disputed"
    assert metadata["pv_claim_value"] == "mnemosyne"
    assert metadata["pv_claim_value_hash"] == "a" * 64
    assert metadata["pv_claim_supports_ids"] == '["fact-1","fact-2"]'
    assert metadata["pv_claim_contradicts_ids"] == '["fact-old"]'
    assert metadata["pv_claim_supersedes_ids"] == '["fact-legacy"]'
    assert metadata["pv_claim_resolution_state"] == "unresolved"
    assert metadata["pv_authority"] == "context_only"
    assert all(isinstance(value, str) for value in metadata.values())


def test_claim_lineage_round_trip_preserves_semantics() -> None:
    original = PhoenixMemoryMetadata(
        source="cortex",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.CORTEX_EVIDENCE,
        confidence=0.93,
        cortex=PhoenixCortexRecord(
            record_kind=PhoenixCortexRecordKind.TEMPORAL_BELIEF,
            record_id="belief-provider-2",
            topic="active memory provider",
            state=PhoenixCortexRecordState.CURRENT,
            confidence=0.91,
        ),
        claim=PhoenixClaimLineage(
            claim_key="phoenix:active-memory-provider",
            state=PhoenixClaimState.CURRENT,
            value="mnemosyne",
            value_hash="b" * 64,
            supersedes_ids=["belief-provider-1"],
            resolution_state=PhoenixClaimResolutionState.RESOLVED,
            resolution_basis="Newer verified configuration evidence.",
            observed_at="2026-10-07T11:46:00-05:00",
        ),
    )

    parsed = parse_phoenix_metadata(original.to_hindsight_metadata())

    assert parsed is not None
    assert parsed.cortex is not None
    assert parsed.cortex.record_id == "belief-provider-2"
    assert parsed.claim is not None
    assert parsed.claim.claim_key == "phoenix:active-memory-provider"
    assert parsed.claim.state == PhoenixClaimState.CURRENT
    assert parsed.claim.value == "mnemosyne"
    assert parsed.claim.supersedes_ids == ["belief-provider-1"]
    assert parsed.claim.resolution_state == PhoenixClaimResolutionState.RESOLVED
    assert parsed.authority == "context_only"


def test_claim_lineage_can_coexist_with_tool_learning_record() -> None:
    original = PhoenixMemoryMetadata(
        source="tool",
        tool="workspace.write",
        memory_class=PhoenixMemoryClass.TOOL_RESULT,
        outcome=PhoenixOutcome.SUCCESS,
        verification=PhoenixVerification.TEST_VERIFIED,
        tool_learning=PhoenixToolLearningRecord(
            record_kind=PhoenixToolLearningKind.TOOL_OUTCOME,
            record_id="tool-provider-2",
            tool_name="workspace.write",
            operation="update provider configuration",
        ),
        claim=PhoenixClaimLineage(
            claim_key="phoenix:active-memory-provider",
            state=PhoenixClaimState.CURRENT,
            value="mnemosyne",
            value_hash="c" * 64,
            supports_ids=["belief-provider-2"],
            resolution_state=PhoenixClaimResolutionState.RESOLVED,
        ),
    )

    parsed = parse_phoenix_metadata(original.to_hindsight_metadata())

    assert parsed is not None
    assert parsed.tool_learning is not None
    assert parsed.tool_learning.record_id == "tool-provider-2"
    assert parsed.claim is not None
    assert parsed.claim.supports_ids == ["belief-provider-2"]
    assert parsed.authority == "context_only"


def test_claim_relation_categories_cannot_overlap() -> None:
    try:
        PhoenixClaimLineage(
            claim_key="phoenix:test-overlap",
            supports_ids=["record-1"],
            contradicts_ids=["record-1"],
        )
    except Exception:
        pass
    else:
        raise AssertionError("Claim target IDs must not appear in multiple relation categories")


def test_claim_native_record_cannot_relate_to_itself() -> None:
    try:
        PhoenixMemoryMetadata(
            memory_class=PhoenixMemoryClass.TOOL_RESULT,
            tool_learning=PhoenixToolLearningRecord(
                record_kind=PhoenixToolLearningKind.TOOL_OUTCOME,
                record_id="tool-self-1",
            ),
            claim=PhoenixClaimLineage(
                claim_key="phoenix:self-relation",
                contradicts_ids=["tool-self-1"],
            ),
        )
    except Exception:
        pass
    else:
        raise AssertionError("Claim lineage must not relate a native record to itself")


def test_claim_relation_id_count_is_bounded() -> None:
    too_many = [f"claim-{index}" for index in range(MAX_CLAIM_RELATION_IDS + 1)]
    try:
        PhoenixClaimLineage(
            claim_key="phoenix:bounded-relations",
            supports_ids=too_many,
        )
    except Exception:
        pass
    else:
        raise AssertionError("Claim relation IDs must be bounded")


def test_malformed_claim_lineage_fails_soft_without_breaking_base_memory() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.9,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_claim_schema_version": "1",
            "pv_claim_key": "phoenix:malformed-claim",
            "pv_claim_supports_ids": '["same-record"]',
            "pv_claim_contradicts_ids": '["same-record"]',
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.PROJECT_FACT
    assert parsed.claim is None
    assert parsed.project == "Phoenix"
    assert parsed.authority == "context_only"


def test_unknown_claim_enums_fail_soft_to_safe_defaults() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_claim_schema_version": "1",
            "pv_claim_key": "phoenix:future-claim",
            "pv_claim_state": "future_state",
            "pv_claim_resolution_state": "future_resolution",
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.claim is not None
    assert parsed.claim.state == PhoenixClaimState.UNKNOWN
    assert parsed.claim.resolution_state == PhoenixClaimResolutionState.UNRESOLVED
    assert parsed.authority == "context_only"


def test_invalid_claim_hash_fails_soft_without_breaking_base_memory() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_claim_schema_version": "1",
            "pv_claim_key": "phoenix:bad-hash",
            "pv_claim_value_hash": "not-a-sha256",
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.claim is None
    assert parsed.authority == "context_only"



def test_legacy_claim_claim_key_alias_remains_readable() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
    ).to_hindsight_metadata()
    metadata["pv_claim_schema_version"] = "1"
    metadata["pv_claim_claim_key"] = "mnemosyne-06c:legacy-claim-key"
    metadata["pv_claim_state"] = "disputed"
    metadata["pv_claim_resolution_state"] = "unresolved"

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.claim is not None
    assert parsed.claim.claim_key == "mnemosyne-06c:legacy-claim-key"
    assert parsed.authority == "context_only"


def test_retention_metadata_serializes_to_hindsight_string_map() -> None:
    item = PhoenixMemoryMetadata(
        source="manual",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.98,
        retention=PhoenixRetentionMetadata(
            score=0.86,
            state=PhoenixRetentionState.HOT,
            verification_strength=1.0,
            recency=0.91,
            corroboration=0.70,
            utility=0.60,
            environment_match=1.0,
            staleness_penalty=0.0,
            contradiction_penalty=0.0,
            scored_at="2026-10-07T17:00:00Z",
        ),
    )

    metadata = item.to_hindsight_metadata()

    assert metadata["pv_retention_schema_version"] == "1"
    assert metadata["pv_retention_score_version"] == PHOENIX_RETENTION_SCORE_VERSION
    assert metadata["pv_retention_score"] == "0.86"
    assert metadata["pv_retention_state"] == "hot"
    assert metadata["pv_retention_verification_strength"] == "1"
    assert metadata["pv_retention_recency"] == "0.91"
    assert metadata["pv_retention_corroboration"] == "0.7"
    assert metadata["pv_retention_utility"] == "0.6"
    assert metadata["pv_retention_environment_match"] == "1"
    assert metadata["pv_retention_staleness_penalty"] == "0"
    assert metadata["pv_retention_contradiction_penalty"] == "0"
    assert metadata["pv_authority"] == "context_only"
    assert all(isinstance(value, str) for value in metadata.values())


def test_retention_metadata_round_trip_preserves_semantics() -> None:
    original = PhoenixMemoryMetadata(
        source="manual",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.97,
        retention=PhoenixRetentionMetadata(
            score=0.49,
            state=PhoenixRetentionState.COLD,
            verification_strength=0.8,
            recency=0.3,
            corroboration=0.5,
            utility=0.4,
            environment_match=1.0,
            staleness_penalty=RETENTION_STALENESS_PENALTY,
            contradiction_penalty=0.0,
            scored_at="2026-10-07T17:05:00Z",
        ),
    )

    parsed = parse_phoenix_metadata(original.to_hindsight_metadata())

    assert parsed is not None
    assert parsed.retention is not None
    assert parsed.retention.score == 0.49
    assert parsed.retention.state == PhoenixRetentionState.COLD
    assert parsed.retention.staleness_penalty == RETENTION_STALENESS_PENALTY
    assert parsed.authority == "context_only"


def test_retention_components_and_penalties_are_bounded() -> None:
    for field in (
        "score",
        "verification_strength",
        "recency",
        "corroboration",
        "utility",
        "environment_match",
        "staleness_penalty",
        "contradiction_penalty",
    ):
        for value in (-0.01, 1.01):
            kwargs = dict(score=0.5, state=PhoenixRetentionState.WARM)
            kwargs[field] = value
            try:
                PhoenixRetentionMetadata(**kwargs)
            except Exception:
                continue
            raise AssertionError(f"{field} outside [0, 1] must be rejected")


def test_retention_weights_are_versioned_and_sum_to_one() -> None:
    total = (
        RETENTION_WEIGHT_VERIFICATION
        + RETENTION_WEIGHT_CONFIDENCE
        + RETENTION_WEIGHT_RECENCY
        + RETENTION_WEIGHT_CORROBORATION
        + RETENTION_WEIGHT_UTILITY
        + RETENTION_WEIGHT_ENVIRONMENT
    )
    assert PHOENIX_RETENTION_SCORE_VERSION == "1"
    assert total == 1.0
    assert RETENTION_STALENESS_PENALTY == 0.25
    assert RETENTION_CONTRADICTION_PENALTY == 0.10


def test_malformed_retention_metadata_fails_soft_without_breaking_base_memory() -> None:
    metadata = PhoenixMemoryMetadata(
        source="manual",
        project="Phoenix",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.9,
    ).to_hindsight_metadata()
    metadata.update(
        {
            "pv_retention_schema_version": "1",
            "pv_retention_score_version": "1",
            "pv_retention_score": "not-a-score",
            "pv_retention_state": "hot",
        }
    )

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.memory_class == PhoenixMemoryClass.PROJECT_FACT
    assert parsed.retention is None
    assert parsed.project == "Phoenix"
    assert parsed.authority == "context_only"


def test_legacy_memory_without_retention_metadata_is_unchanged() -> None:
    metadata = PhoenixMemoryMetadata(
        source="legacy",
        memory_class=PhoenixMemoryClass.PROJECT_FACT,
        confidence=0.77,
    ).to_hindsight_metadata()

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.retention is None
    assert parsed.source == "legacy"
    assert parsed.confidence == 0.77
    assert parsed.authority == "context_only"


def test_retention_coexists_with_claim_cortex_and_tool_learning_extensions() -> None:
    cortex_item = PhoenixMemoryMetadata(
        source="cortex",
        memory_class=PhoenixMemoryClass.CORTEX_EVIDENCE,
        cortex=PhoenixCortexRecord(
            record_kind=PhoenixCortexRecordKind.DECISION,
            record_id="decision-retention-1",
        ),
        claim=PhoenixClaimLineage(
            claim_key="phoenix:retention-coexistence",
            state=PhoenixClaimState.CURRENT,
        ),
        retention=PhoenixRetentionMetadata(
            score=0.9,
            state=PhoenixRetentionState.HOT,
        ),
    )
    parsed_cortex = parse_phoenix_metadata(cortex_item.to_hindsight_metadata())
    assert parsed_cortex is not None
    assert parsed_cortex.cortex is not None
    assert parsed_cortex.claim is not None
    assert parsed_cortex.retention is not None

    tool_item = PhoenixMemoryMetadata(
        source="tool",
        memory_class=PhoenixMemoryClass.TOOL_RESULT,
        tool_learning=PhoenixToolLearningRecord(
            record_kind=PhoenixToolLearningKind.TOOL_OUTCOME,
            record_id="tool-retention-1",
        ),
        retention=PhoenixRetentionMetadata(
            score=0.8,
            state=PhoenixRetentionState.WARM,
        ),
    )
    parsed_tool = parse_phoenix_metadata(tool_item.to_hindsight_metadata())
    assert parsed_tool is not None
    assert parsed_tool.tool_learning is not None
    assert parsed_tool.retention is not None


def test_protected_retention_state_requires_protected_reason_only_when_protected() -> None:
    protected = PhoenixRetentionMetadata(
        score=1.0,
        state=PhoenixRetentionState.PROTECTED,
        protected_reason="Constitutional or safety-critical memory.",
    )
    assert protected.state == PhoenixRetentionState.PROTECTED

    try:
        PhoenixRetentionMetadata(
            score=0.7,
            state=PhoenixRetentionState.WARM,
            protected_reason="must not be silently accepted",
        )
    except Exception:
        pass
    else:
        raise AssertionError("protected_reason must require state=protected")


def test_recalled_protected_retention_state_is_not_downgraded() -> None:
    metadata = PhoenixMemoryMetadata(
        source="constitution",
        memory_class=PhoenixMemoryClass.ARCHITECTURE_DECISION,
        retention=PhoenixRetentionMetadata(
            score=1.0,
            state=PhoenixRetentionState.PROTECTED,
            protected_reason="Constitutional memory.",
        ),
    ).to_hindsight_metadata()
    metadata["pv_authority"] = "approved"

    parsed = parse_phoenix_metadata(metadata)

    assert parsed is not None
    assert parsed.retention is not None
    assert parsed.retention.state == PhoenixRetentionState.PROTECTED
    assert parsed.retention.protected_reason == "Constitutional memory."
    assert parsed.authority == "context_only"
