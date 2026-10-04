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

from pydantic import BaseModel, ConfigDict, Field, field_validator


PHOENIX_METADATA_SCHEMA_VERSION = "1"
PHOENIX_METADATA_PREFIX = "pv_"


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

    def to_hindsight_metadata(self) -> dict[str, str]:
        """Serialize to Hindsight's existing dict[str, str] metadata contract."""

        data = self.model_dump(mode="json")
        provenance = data.pop("provenance", None)

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

        if provenance:
            for key, value in provenance.items():
                if value is not None:
                    metadata[f"{PHOENIX_METADATA_PREFIX}prov_{key}"] = str(value)

        return metadata


def is_phoenix_metadata(metadata: dict[str, str] | None) -> bool:
    if not metadata:
        return False
    return metadata.get(f"{PHOENIX_METADATA_PREFIX}schema_version") == PHOENIX_METADATA_SCHEMA_VERSION
