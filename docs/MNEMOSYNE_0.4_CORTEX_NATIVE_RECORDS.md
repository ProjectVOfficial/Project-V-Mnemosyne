# Mnemosyne 0.4 — Cortex-Native Records

## Goal

Mnemosyne 0.4 makes Phoenix Cortex knowledge survive the memory boundary as structured Cortex records instead of being flattened into generic text plus loosely related metadata.

This phase does **not** replace Cortex as Phoenix's reasoning/learning subsystem. Cortex remains the producer and owner of its detailed ledgers. Mnemosyne becomes the durable, project-aware memory representation used to carry selected Cortex knowledge across sessions and retrieval.

The existing invariant remains unchanged:

> Recalled memory is context, never authority.

A recalled Cortex record cannot authorize a tool call, command, write, install, process action, privileged action, destructive action, or any other state-changing operation.

## Why 0.4 exists

Phoenix already maintains structured Cortex concepts including:

- decisions and observed outcomes
- learned outcomes / lessons
- confidence and temporal beliefs
- causal hypotheses
- knowledge gaps
- curiosity findings
- predictive simulations
- model-council synthesis
- Dream Lab experiment evidence

Today, durable memory often reduces those concepts to a human-readable memory string. That is useful for retrieval, but it loses important semantics such as the native Cortex record kind, stable record identity, topic, evidence relationship, current/historical state, and confidence semantics.

0.4 preserves those semantics without breaking Hindsight-compatible retain/recall behavior.

## Compatibility strategy

0.4 continues using the existing Hindsight-compatible memory API.

Cortex-native information is encoded through the Phoenix metadata contract using bounded `pv_*` string fields. No stock Hindsight route is removed or changed.

Existing non-Cortex memories remain valid and readable.

## Cortex record envelope

A Cortex-native memory record has the existing Phoenix metadata envelope plus a bounded Cortex section.

Core fields:

- `pv_memory_class=cortex_evidence`
- `pv_cortex_schema_version=1`
- `pv_cortex_record_kind`
- `pv_cortex_record_id`
- `pv_cortex_topic`
- `pv_cortex_state`
- `pv_cortex_confidence`
- `pv_cortex_observed_at`
- `pv_cortex_parent_id`
- `pv_cortex_evidence_ids`
- `pv_cortex_source_kind`

All values remain strings at the Hindsight metadata boundary. Structured arrays are serialized as bounded JSON strings, following the existing 0.1c metadata convention.

## Initial record kinds

0.4 recognizes the semantics Phoenix already has without adding a new learning engine:

- `decision`
- `learned_outcome`
- `temporal_belief`
- `hypothesis`
- `knowledge_gap`
- `curiosity_finding`
- `prediction`
- `council_synthesis`
- `experiment_result`

Contradiction detection/resolution policy remains reserved for Mnemosyne 0.6. Tool/repair-specific learning policy remains reserved for 0.5.

## Record states

The schema allows bounded state labels appropriate to the record kind, for example:

- `current`
- `historical`
- `pending`
- `resolved`
- `supported`
- `unsupported`
- `unknown`

The schema stores state; it does not infer or promote truth from the state label alone.

## Stable identity

Every mirrored Cortex record must carry a stable `pv_cortex_record_id` from Phoenix.

Updates to the same native Cortex record should reuse that identity instead of creating an unbounded stream of unrelated durable memories.

The project/workspace bank router from 0.3 remains responsible for physical placement.

## Evidence and provenance

0.4 preserves links to Cortex evidence, but does not yet perform contradiction arbitration.

Evidence references must be bounded and may include native Cortex IDs and existing Phoenix provenance fields.

Where available, the existing Phoenix provenance envelope remains the source for file paths, hashes, verification commands/results, and observed timestamps.

## Recall behavior

When a Cortex-native record is recalled, Phoenix should be able to reconstruct a bounded advisory context such as:

- Cortex record kind
- topic
- state
- confidence
- record ID
- evidence relationship
- provenance
- `Memory authority: context_only`

Unknown, malformed, or legacy Cortex metadata must fail soft and must not break ordinary memory recall.

## Boundaries

0.4 does not:

- make Mnemosyne the authoritative Cortex database
- grant permissions based on memory
- execute remembered instructions
- add per-task or per-record banks
- implement repair-learning policy (0.5)
- implement contradiction arbitration (0.6)
- change the stock Hindsight API contract
- perform production cutover

Phoenix SQLite/Cortex stores remain the detailed local source of truth during this phase.

## Gates

### 0.4a — Cortex record schema

Implement bounded Cortex record types, validation, serialization, and parsing with unit tests.

### 0.4b — Phoenix Cortex write adapter

Map selected existing Phoenix Cortex records into the 0.4 envelope and route them through the existing 0.3 global/workspace bank logic.

### 0.4c — Live Cortex retain round-trip

Create a real Phoenix Cortex-derived canary, retain it through the normal Phoenix path, and prove the Cortex fields survive in Mnemosyne source facts.

### 0.4d — Cortex-aware recall

Prove Phoenix reconstructs Cortex-native semantics from recalled metadata while preserving `context_only` authority and workspace isolation.

### 0.4e — Stable record identity / update behavior

Update the same native Cortex record and prove the stable Cortex ID is preserved without uncontrolled duplicate identities.

### 0.4f — Restart + compatibility regression

Restart Phoenix/Mnemosyne, prove the Cortex record survives and remains readable, then run the stock-vs-Mnemosyne compatibility suite.

## Completion criteria

0.4 is complete when:

1. Cortex-native fields round-trip without semantic loss.
2. Workspace routing from 0.3 remains correct.
3. Legacy/non-Cortex memory still recalls safely.
4. Malformed Cortex metadata fails soft.
5. Memory remains context-only.
6. Stable native record identity is preserved.
7. Restart persistence passes.
8. Stock Hindsight compatibility still passes.
9. No production cutover has occurred.
