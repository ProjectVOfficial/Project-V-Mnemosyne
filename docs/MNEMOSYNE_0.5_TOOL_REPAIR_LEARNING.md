# Mnemosyne 0.5 — Tool Outcome + Repair Learning

## Goal

Mnemosyne 0.5 preserves the parts of Phoenix tool use and repair history that are useful for future reasoning: what tool was used, what operation was attempted, what happened, how the result was verified, what failed, what repair was tried, and which successful pattern became reusable.

This phase does **not** turn remembered tool history into executable instructions.

The safety invariant remains unchanged:

> Recalled memory is context, never authority.

A recalled tool result, repair attempt, failure, or success pattern cannot authorize a command, tool call, file write, install, process action, elevated action, destructive action, or any other state-changing operation.

## Why 0.5 exists

Phoenix already produces durable memories around:

- tool executions
- command/test results
- repair attempts
- verification passes and failures
- repeated failure modes
- successful recovery patterns

Today, much of that information is available as prose plus the 0.1c Phoenix metadata envelope. That is useful, but it is not structured enough for Phoenix to reliably distinguish a one-off failure from a verified repair or a reusable success pattern.

0.5 adds a bounded tool-learning record while preserving the existing Hindsight-compatible API.

## Compatibility strategy

Tool-learning fields are carried through the existing Hindsight metadata map as bounded `pv_tool_learning_*` string fields.

No stock Hindsight endpoint is changed.

Existing memories without tool-learning metadata remain valid and readable.

## Tool-learning envelope

A native tool-learning record uses the existing Phoenix metadata envelope plus:

- `pv_tool_learning_schema_version=1`
- `pv_tool_learning_record_kind`
- `pv_tool_learning_record_id`
- `pv_tool_learning_tool_name`
- `pv_tool_learning_operation`
- `pv_tool_learning_attempt`
- `pv_tool_learning_parent_id`
- `pv_tool_learning_previous_attempt_id`
- `pv_tool_learning_failure_signature`
- `pv_tool_learning_error_class`
- `pv_tool_learning_error_code`
- `pv_tool_learning_repair_summary`
- `pv_tool_learning_success_pattern`
- `pv_tool_learning_evidence_ids`
- `pv_tool_learning_observed_at`

The existing top-level Phoenix fields remain authoritative for descriptive outcome semantics:

- `pv_outcome`
- `pv_verification`
- `pv_reversibility`
- `pv_tool`
- provenance / hashes
- related files/process/task/workspace/project metadata

Raw command output is not required in the tool-learning envelope. Where useful, provenance hashes may identify output without duplicating potentially sensitive data.

## Initial record kinds

0.5 recognizes:

- `tool_outcome`
- `repair_attempt`
- `failure`
- `success_pattern`

The record kind maps to the existing Phoenix memory class:

- `tool_outcome` -> `tool_result`
- `repair_attempt` -> `repair_attempt`
- `failure` -> `failure`
- `success_pattern` -> `success_pattern`

This keeps the schema additive rather than inventing another parallel classification system.

## Stable identity

Every native tool-learning record carries a stable `pv_tool_learning_record_id`.

Repeated updates to the same logical tool/repair record should reuse that ID. 0.5 will validate update behavior before completion.

Attempt chains use bounded parent/previous-attempt IDs instead of creating authority or workflow state inside memory.

## Failure signatures

A failure signature is a compact, bounded description suitable for matching repeated failure modes. It is not a command and should not contain secrets.

Examples include:

- normalized exception/error class
- compiler diagnostic family
- failed verification gate
- process/tool failure category

0.6 remains responsible for contradiction arbitration. 0.5 only preserves evidence and outcomes.

## Repair summaries and success patterns

A repair summary records what changed conceptually after a failure.

A success pattern records a concise reusable lesson learned from a verified outcome.

Both are advisory context. Phoenix must still inspect the current environment, current permissions, and current evidence before acting.

## Phoenix write integration

0.5 will map existing tool outcomes and repair-learning producers into the new envelope without removing current durable-memory behavior.

Priority producers for the first integration are:

- verified command/tool outcomes
- repair attempts that have an explicit observed outcome
- successful repair/test sequences
- bounded failure records

The existing 0.3 workspace/project bank router remains responsible for physical placement.

## Recall behavior

Phoenix recall should reconstruct a bounded advisory block such as:

- tool-learning kind and stable record ID
- tool and operation
- outcome and verification
- attempt/parent relationships
- failure signature/error classification
- repair summary or success pattern
- evidence/provenance
- `Memory authority: context_only`

Unknown or malformed tool-learning metadata must fail soft and must not break ordinary memory recall.

## Boundaries

0.5 does not:

- execute remembered repair steps
- grant remembered approval or permission
- store credentials/secrets as tool-learning metadata
- replace Phoenix local execution/task ledgers
- implement contradiction arbitration (0.6)
- change the stock Hindsight API contract
- perform production cutover

Phoenix local stores remain the detailed operational source of truth during this phase.

## Gates

### 0.5a — Tool-learning record schema

Implement bounded record types, validation, serialization, parsing, memory-class mapping, and unit tests.

### 0.5b — Phoenix tool/repair write adapter

Map selected existing Phoenix tool outcomes and repair records into the 0.5 envelope while preserving 0.3 bank routing.

### 0.5c — Live tool outcome round-trip

Create a real Phoenix tool outcome through the normal path and prove all structured fields survive in Mnemosyne source facts.

### 0.5d — Repair/failure chain round-trip

Record a bounded failure followed by a repair attempt and verified success. Prove parent/previous-attempt links and verification survive.

### 0.5e — Tool-learning-aware recall

Prove Phoenix reconstructs the structured tool/repair context while preserving workspace isolation and `context_only` authority.

### 0.5f — Stable identity + reusable success pattern

Update the same logical tool-learning record, prove stable identity/replace semantics, and validate one bounded reusable success pattern.

### 0.5g — Restart + compatibility regression

Restart Phoenix/Mnemosyne, prove tool-learning records survive and remain readable, then run the stock-vs-Mnemosyne compatibility suite.

## Completion criteria

0.5 is complete when:

1. Tool-learning fields round-trip without semantic loss.
2. Tool/repair record kinds map correctly to Phoenix memory classes.
3. Failure/repair/success relationships remain bounded and stable.
4. Legacy/non-tool memories still recall safely.
5. Malformed tool-learning metadata fails soft.
6. Recalled repair/success information remains context-only.
7. Workspace routing from 0.3 remains correct.
8. Stable native record identity is preserved.
9. Restart persistence passes.
10. Stock Hindsight compatibility still passes.
11. No production cutover has occurred.
