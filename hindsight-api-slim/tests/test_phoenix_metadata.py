from hindsight_api.phoenix_metadata import (
    PhoenixMemoryClass,
    PhoenixMemoryMetadata,
    PhoenixOutcome,
    PhoenixProvenance,
    PhoenixVerification,
    is_phoenix_metadata,
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
