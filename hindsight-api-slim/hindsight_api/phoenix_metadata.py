"""Phoenix-native metadata schema for Project V // Mnemosyne.

This module is intentionally additive. It serializes Phoenix-specific memory
semantics into Hindsight's existing string metadata map so the proven public
Retain/Recall contract does not need to change.

Memory remains context, never authority.
"""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PHOENIX_METADATA_SCHEMA_VERSION = "1"
PHOENIX_METADATA_PREFIX = "pv_"
PHOENIX_CORTEX_SCHEMA_VERSION = "1"
PHOENIX_TOOL_LEARNING_SCHEMA_VERSION = "1"
PHOENIX_CLAIM_SCHEMA_VERSION = "1"

MAX_CORTEX_RECORD_ID_LENGTH = 256
MAX_CORTEX_TOPIC_LENGTH = 512
MAX_CORTEX_STATE_TEXT_LENGTH = 64
MAX_CORTEX_SOURCE_KIND_LENGTH = 128
MAX_CORTEX_OBSERVED_AT_LENGTH = 128
MAX_CORTEX_EVIDENCE_IDS = 32

MAX_TOOL_LEARNING_RECORD_ID_LENGTH = 256
MAX_TOOL_LEARNING_TOOL_NAME_LENGTH = 128
MAX_TOOL_LEARNING_OPERATION_LENGTH = 512
MAX_TOOL_LEARNING_ERROR_CLASS_LENGTH = 128
MAX_TOOL_LEARNING_ERROR_CODE_LENGTH = 128
MAX_TOOL_LEARNING_FAILURE_SIGNATURE_LENGTH = 512
MAX_TOOL_LEARNING_REPAIR_SUMMARY_LENGTH = 1024
MAX_TOOL_LEARNING_SUCCESS_PATTERN_LENGTH = 1024
MAX_TOOL_LEARNING_OBSERVED_AT_LENGTH = 128
MAX_TOOL_LEARNING_EVIDENCE_IDS = 32

MAX_CLAIM_KEY_LENGTH = 256
MAX_CLAIM_VALUE_LENGTH = 1024
MAX_CLAIM_VALUE_HASH_LENGTH = 64
MAX_CLAIM_RECORD_ID_LENGTH = 256
MAX_CLAIM_RELATION_IDS = 32
MAX_CLAIM_RESOLUTION_BASIS_LENGTH = 1024
MAX_CLAIM_OBSERVED_AT_LENGTH = 128


class PhoenixMemoryClass(StrEnum):
    CONVERSATION = "conversation"
    USER_PREFERENCE = "user_preference"
    PROJECT_FACT = "project_fact"
    ARCHITECTURE_DECISION = "architecture_decision"
    TOOL_RESULT = "tool_result"
    REPAIR_ATTEMPT = "repair_attempt"
    FAILURE = "failure"
    SUCCESS_PATTERN = "success_pattern"
    PROTOCOL_EVENT = "protocol_event"
    CORTEX_EVIDENCE = "cortex_evidence"
    WATCHTOWER_CONTEXT = "watchtower_context"
    SECURITY_EVENT = "security_event"
    EXPERIMENT_RESULT = "experiment_result"


class PhoenixOutcome(StrEnum):
    UNKNOWN = "unknown"
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    NO_CHANGE = "no_change"


class PhoenixVerification(StrEnum):
    UNVERIFIED = "unverified"
    SELF_REPORTED = "self_reported"
    OBSERVED = "observed"
    COMMAND_VERIFIED = "command_verified"
    TEST_VERIFIED = "test_verified"
    OPERATOR_CONFIRMED = "operator_confirmed"


class PhoenixReversibility(StrEnum):
    UNKNOWN = "unknown"
    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


class PhoenixCortexRecordKind(StrEnum):
    DECISION = "decision"
    LEARNED_OUTCOME = "learned_outcome"
    TEMPORAL_BELIEF = "temporal_belief"
    HYPOTHESIS = "hypothesis"
    KNOWLEDGE_GAP = "knowledge_gap"
    CURIOSITY_FINDING = "curiosity_finding"
    PREDICTION = "prediction"
    COUNCIL_SYNTHESIS = "council_synthesis"
    EXPERIMENT_RESULT = "experiment_result"


class PhoenixCortexRecordState(StrEnum):
    CURRENT = "current"
    HISTORICAL = "historical"
    PENDING = "pending"
    RESOLVED = "resolved"
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class PhoenixToolLearningKind(StrEnum):
    TOOL_OUTCOME = "tool_outcome"
    REPAIR_ATTEMPT = "repair_attempt"
    FAILURE = "failure"
    SUCCESS_PATTERN = "success_pattern"


class PhoenixClaimState(StrEnum):
    CURRENT = "current"
    HISTORICAL = "historical"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"
    UNKNOWN = "unknown"


class PhoenixClaimResolutionState(StrEnum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    NOT_APPLICABLE = "not_applicable"


TOOL_LEARNING_MEMORY_CLASS: dict[PhoenixToolLearningKind, PhoenixMemoryClass] = {
    PhoenixToolLearningKind.TOOL_OUTCOME: PhoenixMemoryClass.TOOL_RESULT,
    PhoenixToolLearningKind.REPAIR_ATTEMPT: PhoenixMemoryClass.REPAIR_ATTEMPT,
    PhoenixToolLearningKind.FAILURE: PhoenixMemoryClass.FAILURE,
    PhoenixToolLearningKind.SUCCESS_PATTERN: PhoenixMemoryClass.SUCCESS_PATTERN,
}


class PhoenixProvenance(BaseModel):
    """Where the memory came from and how an outcome was verified."""

    model_config = ConfigDict(extra="forbid")

    source_type: str | None = None
    source_path: str | None = None
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    sha256: str | None = None
    observed_at: str | None = None
    verification_command: str | None = None
    verification_result: str | None = None
    tool_output_hash: str | None = None

    @field_validator("sha256", "tool_output_hash")
    @classmethod
    def normalize_hash(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        return value or None


class PhoenixCortexRecord(BaseModel):
    """Bounded Cortex semantics carried inside Phoenix-native metadata."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = PHOENIX_CORTEX_SCHEMA_VERSION
    record_kind: PhoenixCortexRecordKind
    record_id: str = Field(min_length=1, max_length=MAX_CORTEX_RECORD_ID_LENGTH)
    topic: str | None = Field(default=None, max_length=MAX_CORTEX_TOPIC_LENGTH)
    state: PhoenixCortexRecordState = PhoenixCortexRecordState.UNKNOWN
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    observed_at: str | None = Field(default=None, max_length=MAX_CORTEX_OBSERVED_AT_LENGTH)
    parent_id: str | None = Field(default=None, max_length=MAX_CORTEX_RECORD_ID_LENGTH)
    evidence_ids: list[str] = Field(default_factory=list, max_length=MAX_CORTEX_EVIDENCE_IDS)
    source_kind: str | None = Field(default=None, max_length=MAX_CORTEX_SOURCE_KIND_LENGTH)

    @field_validator("record_id")
    @classmethod
    def normalize_record_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Cortex record_id must not be empty")
        return value

    @field_validator("topic", "observed_at", "parent_id", "source_kind")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("evidence_ids")
    @classmethod
    def normalize_evidence_ids(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for raw in value:
            item = str(raw).strip()
            if not item:
                continue
            if len(item) > MAX_CORTEX_RECORD_ID_LENGTH:
                raise ValueError(
                    f"Cortex evidence id exceeds {MAX_CORTEX_RECORD_ID_LENGTH} characters"
                )
            if item not in seen:
                seen.add(item)
                result.append(item)
        if len(result) > MAX_CORTEX_EVIDENCE_IDS:
            raise ValueError(
                f"Cortex evidence_ids exceeds {MAX_CORTEX_EVIDENCE_IDS} entries"
            )
        return result


class PhoenixToolLearningRecord(BaseModel):
    """Bounded tool outcome / repair-learning semantics for Phoenix memory."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = PHOENIX_TOOL_LEARNING_SCHEMA_VERSION
    record_kind: PhoenixToolLearningKind
    record_id: str = Field(min_length=1, max_length=MAX_TOOL_LEARNING_RECORD_ID_LENGTH)
    tool_name: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_TOOL_NAME_LENGTH)
    operation: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_OPERATION_LENGTH)
    attempt: int = Field(default=1, ge=1)
    parent_id: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_RECORD_ID_LENGTH)
    previous_attempt_id: str | None = Field(
        default=None, max_length=MAX_TOOL_LEARNING_RECORD_ID_LENGTH
    )
    failure_signature: str | None = Field(
        default=None, max_length=MAX_TOOL_LEARNING_FAILURE_SIGNATURE_LENGTH
    )
    error_class: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_ERROR_CLASS_LENGTH)
    error_code: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_ERROR_CODE_LENGTH)
    repair_summary: str | None = Field(
        default=None, max_length=MAX_TOOL_LEARNING_REPAIR_SUMMARY_LENGTH
    )
    success_pattern: str | None = Field(
        default=None, max_length=MAX_TOOL_LEARNING_SUCCESS_PATTERN_LENGTH
    )
    evidence_ids: list[str] = Field(default_factory=list, max_length=MAX_TOOL_LEARNING_EVIDENCE_IDS)
    observed_at: str | None = Field(default=None, max_length=MAX_TOOL_LEARNING_OBSERVED_AT_LENGTH)

    @field_validator("record_id")
    @classmethod
    def normalize_record_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tool-learning record_id must not be empty")
        return value

    @field_validator(
        "tool_name",
        "operation",
        "parent_id",
        "previous_attempt_id",
        "failure_signature",
        "error_class",
        "error_code",
        "repair_summary",
        "success_pattern",
        "observed_at",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("evidence_ids")
    @classmethod
    def normalize_evidence_ids(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for raw in value:
            item = str(raw).strip()
            if not item:
                continue
            if len(item) > MAX_TOOL_LEARNING_RECORD_ID_LENGTH:
                raise ValueError(
                    f"Tool-learning evidence id exceeds {MAX_TOOL_LEARNING_RECORD_ID_LENGTH} characters"
                )
            if item not in seen:
                seen.add(item)
                result.append(item)
        if len(result) > MAX_TOOL_LEARNING_EVIDENCE_IDS:
            raise ValueError(
                f"Tool-learning evidence_ids exceeds {MAX_TOOL_LEARNING_EVIDENCE_IDS} entries"
            )
        return result


class PhoenixClaimLineage(BaseModel):
    """Bounded claim lineage used for provenance and contradiction handling."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = PHOENIX_CLAIM_SCHEMA_VERSION
    claim_key: str = Field(min_length=1, max_length=MAX_CLAIM_KEY_LENGTH)
    state: PhoenixClaimState = PhoenixClaimState.UNKNOWN
    value: str | None = Field(default=None, max_length=MAX_CLAIM_VALUE_LENGTH)
    value_hash: str | None = Field(default=None, max_length=MAX_CLAIM_VALUE_HASH_LENGTH)
    supports_ids: list[str] = Field(default_factory=list, max_length=MAX_CLAIM_RELATION_IDS)
    contradicts_ids: list[str] = Field(default_factory=list, max_length=MAX_CLAIM_RELATION_IDS)
    supersedes_ids: list[str] = Field(default_factory=list, max_length=MAX_CLAIM_RELATION_IDS)
    resolution_state: PhoenixClaimResolutionState = PhoenixClaimResolutionState.UNRESOLVED
    resolution_basis: str | None = Field(
        default=None, max_length=MAX_CLAIM_RESOLUTION_BASIS_LENGTH
    )
    observed_at: str | None = Field(default=None, max_length=MAX_CLAIM_OBSERVED_AT_LENGTH)

    @field_validator("claim_key")
    @classmethod
    def normalize_claim_key(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Claim key must not be empty")
        return value

    @field_validator("value", "resolution_basis", "observed_at")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("value_hash")
    @classmethod
    def normalize_value_hash(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if not value:
            return None
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ValueError("Claim value_hash must be a 64-character SHA-256 hex digest")
        return value

    @field_validator("supports_ids", "contradicts_ids", "supersedes_ids")
    @classmethod
    def normalize_relation_ids(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for raw in value:
            item = str(raw).strip()
            if not item:
                continue
            if len(item) > MAX_CLAIM_RECORD_ID_LENGTH:
                raise ValueError(
                    f"Claim relation id exceeds {MAX_CLAIM_RECORD_ID_LENGTH} characters"
                )
            if item not in seen:
                seen.add(item)
                result.append(item)
        if len(result) > MAX_CLAIM_RELATION_IDS:
            raise ValueError(f"Claim relation list exceeds {MAX_CLAIM_RELATION_IDS} entries")
        return result

    @model_validator(mode="after")
    def validate_relation_categories(self) -> "PhoenixClaimLineage":
        supports = set(self.supports_ids)
        contradicts = set(self.contradicts_ids)
        supersedes = set(self.supersedes_ids)
        overlap = (
            (supports & contradicts)
            | (supports & supersedes)
            | (contradicts & supersedes)
        )
        if overlap:
            raise ValueError(
                "Claim relation target cannot appear in more than one relation category"
            )
        return self


class PhoenixMemoryMetadata(BaseModel):
    """Phoenix-native semantics carried through Hindsight-compatible metadata."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1"] = PHOENIX_METADATA_SCHEMA_VERSION
    source: str | None = None
    workspace: str | None = None
    project: str | None = None
    task_id: str | None = None
    session_id: str | None = None
    tool: str | None = None
    memory_class: PhoenixMemoryClass = PhoenixMemoryClass.CONVERSATION
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    # Safety invariant: recalled memory can inform reasoning but can never carry
    # current execution authority or approval.
    authority: Literal["context_only"] = "context_only"

    outcome: PhoenixOutcome = PhoenixOutcome.UNKNOWN
    verification: PhoenixVerification = PhoenixVerification.UNVERIFIED
    reversibility: PhoenixReversibility = PhoenixReversibility.UNKNOWN
    related_files: list[str] = Field(default_factory=list)
    related_process: str | None = None
    cortex_topic: str | None = None
    cortex: PhoenixCortexRecord | None = None
    tool_learning: PhoenixToolLearningRecord | None = None
    claim: PhoenixClaimLineage | None = None
    provenance: PhoenixProvenance | None = None

    @field_validator(
        "source",
        "workspace",
        "project",
        "task_id",
        "session_id",
        "tool",
        "related_process",
        "cortex_topic",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("related_files")
    @classmethod
    def normalize_related_files(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in value:
            item = str(item).strip()
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @model_validator(mode="after")
    def validate_native_memory_classes(self) -> "PhoenixMemoryMetadata":
        if self.cortex is not None and self.tool_learning is not None:
            raise ValueError("Memory cannot carry Cortex and tool-learning native envelopes together")
        if self.cortex is not None and self.memory_class != PhoenixMemoryClass.CORTEX_EVIDENCE:
            raise ValueError("Cortex-native records must use memory_class=cortex_evidence")
        if self.tool_learning is not None:
            expected = TOOL_LEARNING_MEMORY_CLASS[self.tool_learning.record_kind]
            if self.memory_class != expected:
                raise ValueError(
                    f"Tool-learning kind {self.tool_learning.record_kind.value} "
                    f"must use memory_class={expected.value}"
                )

        # Claim lineage may coexist with either native envelope, but when an
        # owning stable record ID is available it may never relate the record to
        # itself. Base memories without a native stable ID are checked later by
        # the Phoenix write adapter once their durable ID is known.
        if self.claim is not None:
            owner_ids: set[str] = set()
            if self.cortex is not None:
                owner_ids.add(self.cortex.record_id)
            if self.tool_learning is not None:
                owner_ids.add(self.tool_learning.record_id)
            related_ids = (
                set(self.claim.supports_ids)
                | set(self.claim.contradicts_ids)
                | set(self.claim.supersedes_ids)
            )
            if owner_ids & related_ids:
                raise ValueError("Claim lineage cannot relate a native record to itself")
        return self

    def to_hindsight_metadata(self) -> dict[str, str]:
        """Serialize to Hindsight's existing dict[str, str] metadata contract."""

        data = self.model_dump(mode="json")
        provenance = data.pop("provenance", None)
        cortex = data.pop("cortex", None)
        tool_learning = data.pop("tool_learning", None)
        claim = data.pop("claim", None)

        metadata: dict[str, str] = {
            f"{PHOENIX_METADATA_PREFIX}schema_version": str(data.pop("schema_version")),
            f"{PHOENIX_METADATA_PREFIX}memory_class": str(data.pop("memory_class")),
            f"{PHOENIX_METADATA_PREFIX}confidence": format(float(data.pop("confidence")), ".6g"),
            f"{PHOENIX_METADATA_PREFIX}authority": str(data.pop("authority")),
            f"{PHOENIX_METADATA_PREFIX}outcome": str(data.pop("outcome")),
            f"{PHOENIX_METADATA_PREFIX}verification": str(data.pop("verification")),
            f"{PHOENIX_METADATA_PREFIX}reversibility": str(data.pop("reversibility")),
        }

        related_files = data.pop("related_files", [])
        if related_files:
            metadata[f"{PHOENIX_METADATA_PREFIX}related_files"] = json.dumps(
                related_files, separators=(",", ":"), ensure_ascii=False
            )

        for key, value in data.items():
            if value is not None:
                metadata[f"{PHOENIX_METADATA_PREFIX}{key}"] = str(value)

        if cortex:
            evidence_ids = cortex.pop("evidence_ids", [])
            for key, value in cortex.items():
                if value is None:
                    continue
                if key == "confidence":
                    metadata[f"{PHOENIX_METADATA_PREFIX}cortex_{key}"] = format(
                        float(value), ".6g"
                    )
                else:
                    metadata[f"{PHOENIX_METADATA_PREFIX}cortex_{key}"] = str(value)
            if evidence_ids:
                metadata[f"{PHOENIX_METADATA_PREFIX}cortex_evidence_ids"] = json.dumps(
                    evidence_ids, separators=(",", ":"), ensure_ascii=False
                )

        if tool_learning:
            evidence_ids = tool_learning.pop("evidence_ids", [])
            for key, value in tool_learning.items():
                if value is not None:
                    metadata[f"{PHOENIX_METADATA_PREFIX}tool_learning_{key}"] = str(value)
            if evidence_ids:
                metadata[f"{PHOENIX_METADATA_PREFIX}tool_learning_evidence_ids"] = json.dumps(
                    evidence_ids, separators=(",", ":"), ensure_ascii=False
                )

        if claim:
            supports_ids = claim.pop("supports_ids", [])
            contradicts_ids = claim.pop("contradicts_ids", [])
            supersedes_ids = claim.pop("supersedes_ids", [])
            for key, value in claim.items():
                if value is not None:
                    metadata[f"{PHOENIX_METADATA_PREFIX}claim_{key}"] = str(value)
            for key, values in (
                ("supports_ids", supports_ids),
                ("contradicts_ids", contradicts_ids),
                ("supersedes_ids", supersedes_ids),
            ):
                if values:
                    metadata[f"{PHOENIX_METADATA_PREFIX}claim_{key}"] = json.dumps(
                        values, separators=(",", ":"), ensure_ascii=False
                    )

        if provenance:
            for key, value in provenance.items():
                if value is not None:
                    metadata[f"{PHOENIX_METADATA_PREFIX}prov_{key}"] = str(value)

        return metadata


def is_phoenix_metadata(metadata: dict[str, str] | None) -> bool:
    if not metadata:
        return False
    return metadata.get(f"{PHOENIX_METADATA_PREFIX}schema_version") == PHOENIX_METADATA_SCHEMA_VERSION


def _safe_float(value: str | None, default: float | None) -> float | None:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if not 0.0 <= parsed <= 1.0:
        return default
    return parsed


def _safe_json_string_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def _safe_enum(enum_type, value: str | None, default):
    if value is None:
        return default
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default


def _safe_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 1 else default


def _parse_cortex_record(metadata: dict[str, str]) -> PhoenixCortexRecord | None:
    prefix = f"{PHOENIX_METADATA_PREFIX}cortex_"
    if not any(key.startswith(prefix) for key in metadata):
        return None

    if metadata.get(f"{prefix}schema_version") != PHOENIX_CORTEX_SCHEMA_VERSION:
        return None

    record_kind_raw = metadata.get(f"{prefix}record_kind")
    record_id = metadata.get(f"{prefix}record_id")
    if not record_kind_raw or not record_id:
        return None

    try:
        record_kind = PhoenixCortexRecordKind(record_kind_raw)
    except ValueError:
        return None

    try:
        return PhoenixCortexRecord(
            record_kind=record_kind,
            record_id=record_id,
            topic=metadata.get(f"{prefix}topic"),
            state=_safe_enum(
                PhoenixCortexRecordState,
                metadata.get(f"{prefix}state"),
                PhoenixCortexRecordState.UNKNOWN,
            ),
            confidence=_safe_float(metadata.get(f"{prefix}confidence"), None),
            observed_at=metadata.get(f"{prefix}observed_at"),
            parent_id=metadata.get(f"{prefix}parent_id"),
            evidence_ids=_safe_json_string_list(metadata.get(f"{prefix}evidence_ids")),
            source_kind=metadata.get(f"{prefix}source_kind"),
        )
    except Exception:
        # Cortex metadata is advisory. Malformed Cortex fields must never break
        # ordinary Phoenix memory recall.
        return None


def _parse_tool_learning_record(
    metadata: dict[str, str],
) -> PhoenixToolLearningRecord | None:
    prefix = f"{PHOENIX_METADATA_PREFIX}tool_learning_"
    if not any(key.startswith(prefix) for key in metadata):
        return None

    if metadata.get(f"{prefix}schema_version") != PHOENIX_TOOL_LEARNING_SCHEMA_VERSION:
        return None

    record_kind_raw = metadata.get(f"{prefix}record_kind")
    record_id = metadata.get(f"{prefix}record_id")
    if not record_kind_raw or not record_id:
        return None

    try:
        record_kind = PhoenixToolLearningKind(record_kind_raw)
    except ValueError:
        return None

    try:
        return PhoenixToolLearningRecord(
            record_kind=record_kind,
            record_id=record_id,
            tool_name=metadata.get(f"{prefix}tool_name"),
            operation=metadata.get(f"{prefix}operation"),
            attempt=_safe_positive_int(metadata.get(f"{prefix}attempt"), 1),
            parent_id=metadata.get(f"{prefix}parent_id"),
            previous_attempt_id=metadata.get(f"{prefix}previous_attempt_id"),
            failure_signature=metadata.get(f"{prefix}failure_signature"),
            error_class=metadata.get(f"{prefix}error_class"),
            error_code=metadata.get(f"{prefix}error_code"),
            repair_summary=metadata.get(f"{prefix}repair_summary"),
            success_pattern=metadata.get(f"{prefix}success_pattern"),
            evidence_ids=_safe_json_string_list(metadata.get(f"{prefix}evidence_ids")),
            observed_at=metadata.get(f"{prefix}observed_at"),
        )
    except Exception:
        # Tool-learning metadata is advisory. Malformed extension fields must
        # never break ordinary Phoenix memory recall.
        return None


def _parse_claim_lineage(metadata: dict[str, str]) -> PhoenixClaimLineage | None:
    prefix = f"{PHOENIX_METADATA_PREFIX}claim_"
    if not any(key.startswith(prefix) for key in metadata):
        return None

    if metadata.get(f"{prefix}schema_version") != PHOENIX_CLAIM_SCHEMA_VERSION:
        return None

    claim_key = metadata.get(f"{prefix}claim_key")
    if not claim_key:
        return None

    try:
        return PhoenixClaimLineage(
            claim_key=claim_key,
            state=_safe_enum(
                PhoenixClaimState,
                metadata.get(f"{prefix}state"),
                PhoenixClaimState.UNKNOWN,
            ),
            value=metadata.get(f"{prefix}value"),
            value_hash=metadata.get(f"{prefix}value_hash"),
            supports_ids=_safe_json_string_list(metadata.get(f"{prefix}supports_ids")),
            contradicts_ids=_safe_json_string_list(
                metadata.get(f"{prefix}contradicts_ids")
            ),
            supersedes_ids=_safe_json_string_list(
                metadata.get(f"{prefix}supersedes_ids")
            ),
            resolution_state=_safe_enum(
                PhoenixClaimResolutionState,
                metadata.get(f"{prefix}resolution_state"),
                PhoenixClaimResolutionState.UNRESOLVED,
            ),
            resolution_basis=metadata.get(f"{prefix}resolution_basis"),
            observed_at=metadata.get(f"{prefix}observed_at"),
        )
    except Exception:
        # Claim lineage is advisory. Malformed contradiction/provenance fields
        # must never break ordinary Phoenix memory recall.
        return None


def parse_phoenix_metadata(metadata: dict[str, str] | None) -> PhoenixMemoryMetadata | None:
    """Parse Phoenix metadata without allowing remembered authority to escalate.

    Legacy/non-Cortex Phoenix metadata remains valid. Malformed Cortex fields
    fail soft: the base Phoenix metadata is returned with cortex=None.
    """

    if not is_phoenix_metadata(metadata):
        return None

    assert metadata is not None

    provenance_data = {
        key.removeprefix(f"{PHOENIX_METADATA_PREFIX}prov_"): value
        for key, value in metadata.items()
        if key.startswith(f"{PHOENIX_METADATA_PREFIX}prov_")
    }
    provenance: PhoenixProvenance | None = None
    if provenance_data:
        try:
            provenance = PhoenixProvenance(**provenance_data)
        except Exception:
            provenance = None

    cortex = _parse_cortex_record(metadata)
    tool_learning = _parse_tool_learning_record(metadata)
    claim = _parse_claim_lineage(metadata)
    if cortex is not None and tool_learning is not None:
        # Conflicting native envelopes fail soft instead of allowing either
        # extension to reinterpret the base memory.
        cortex = None
        tool_learning = None

    memory_class = _safe_enum(
        PhoenixMemoryClass,
        metadata.get(f"{PHOENIX_METADATA_PREFIX}memory_class"),
        PhoenixMemoryClass.CONVERSATION,
    )
    if cortex is not None:
        memory_class = PhoenixMemoryClass.CORTEX_EVIDENCE
    elif tool_learning is not None:
        memory_class = TOOL_LEARNING_MEMORY_CLASS[tool_learning.record_kind]

    related_files = _safe_json_string_list(
        metadata.get(f"{PHOENIX_METADATA_PREFIX}related_files")
    )

    try:
        return PhoenixMemoryMetadata(
            source=metadata.get(f"{PHOENIX_METADATA_PREFIX}source"),
            workspace=metadata.get(f"{PHOENIX_METADATA_PREFIX}workspace"),
            project=metadata.get(f"{PHOENIX_METADATA_PREFIX}project"),
            task_id=metadata.get(f"{PHOENIX_METADATA_PREFIX}task_id"),
            session_id=metadata.get(f"{PHOENIX_METADATA_PREFIX}session_id"),
            tool=metadata.get(f"{PHOENIX_METADATA_PREFIX}tool"),
            memory_class=memory_class,
            confidence=_safe_float(
                metadata.get(f"{PHOENIX_METADATA_PREFIX}confidence"), 0.5
            )
            or 0.0,
            # Never trust recalled authority. Even a forged or legacy value is
            # normalized back to the only allowed memory authority.
            authority="context_only",
            outcome=_safe_enum(
                PhoenixOutcome,
                metadata.get(f"{PHOENIX_METADATA_PREFIX}outcome"),
                PhoenixOutcome.UNKNOWN,
            ),
            verification=_safe_enum(
                PhoenixVerification,
                metadata.get(f"{PHOENIX_METADATA_PREFIX}verification"),
                PhoenixVerification.UNVERIFIED,
            ),
            reversibility=_safe_enum(
                PhoenixReversibility,
                metadata.get(f"{PHOENIX_METADATA_PREFIX}reversibility"),
                PhoenixReversibility.UNKNOWN,
            ),
            related_files=related_files,
            related_process=metadata.get(f"{PHOENIX_METADATA_PREFIX}related_process"),
            cortex_topic=metadata.get(f"{PHOENIX_METADATA_PREFIX}cortex_topic"),
            cortex=cortex,
            tool_learning=tool_learning,
            claim=claim,
            provenance=provenance,
        )
    except Exception:
        return None
