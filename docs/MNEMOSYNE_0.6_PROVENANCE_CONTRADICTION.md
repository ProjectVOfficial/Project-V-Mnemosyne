# Mnemosyne 0.6 — Provenance + Contradiction Engine

Status: design baseline for 0.6a  
Branch: `mnemosyne-0.6-provenance-contradiction`

## Purpose

Mnemosyne 0.6 adds deterministic provenance lineage, contradiction representation, supersession/staleness handling, and contradiction-aware recall without weakening Phoenix's safety model.

The core invariant remains:

> Memory is context, never authority.

A recalled memory, contradiction resolution, success pattern, supersession relation, or provenance score can never authorize a command, tool call, write, install, process action, registry change, elevated action, destructive action, or any other state-changing operation.

## Design goals

1. Preserve conflicting historical evidence instead of silently deleting or overwriting it.
2. Make claim lineage explicit and machine-readable.
3. Separate **contradiction detection** from **resolution preference**.
4. Prefer deterministic evidence rules over model-only arbitration.
5. Keep old records available as historical context when superseded.
6. Allow newer verified evidence to outrank stale or weaker evidence without erasing it.
7. Preserve 0.1–0.5 compatibility, bank routing, Cortex records, tool-learning records, and `context_only` authority.
8. Keep stock Hindsight API compatibility unchanged.

## Non-goals for 0.6

- No production cutover.
- No destructive migration.
- No automatic deletion of contradictory memories.
- No memory-derived permission.
- No free-form model decision that a contradiction is resolved without bounded evidence.
- No replacement for Cortex ownership of detailed reasoning ledgers.
- No retention pruning policy; that remains 0.7.

## 0.6a — Claim lineage / contradiction schema

Add an optional Phoenix claim-lineage envelope that can coexist with base Phoenix metadata and with either Cortex or tool-learning records.

### Schema version

`pv_claim_schema_version=1`

### Fields

- `pv_claim_key`
  - Stable bounded identity for the proposition being tracked.
  - Maximum 256 characters.
  - May be supplied by Phoenix or derived deterministically from a bounded canonical subject/value representation.
  - Must not contain secrets.

- `pv_claim_state`
  - `current`
  - `historical`
  - `disputed`
  - `superseded`
  - `unknown`

- `pv_claim_value`
  - Optional bounded normalized value or conclusion for deterministic comparison.
  - Maximum 1024 characters.
  - This is descriptive context, never executable content.

- `pv_claim_value_hash`
  - Optional SHA-256 digest of the bounded canonical claim value.
  - Used for deterministic equality checks without requiring full value comparison.

- `pv_claim_supports_ids`
  - Compact JSON array of stable Phoenix record IDs this record supports.
  - Maximum 32 IDs; each ID maximum 256 characters.

- `pv_claim_contradicts_ids`
  - Compact JSON array of stable Phoenix record IDs this record contradicts.
  - Maximum 32 IDs.

- `pv_claim_supersedes_ids`
  - Compact JSON array of stable Phoenix record IDs explicitly superseded by this record.
  - Maximum 32 IDs.

- `pv_claim_resolution_state`
  - `unresolved`
  - `resolved`
  - `not_applicable`

- `pv_claim_resolution_basis`
  - Optional bounded explanation of why a preference was chosen.
  - Maximum 1024 characters.
  - Must refer to evidence characteristics, not permissions.

- `pv_claim_observed_at`
  - Optional source observation timestamp.

### Validation rules

- Claim lineage is optional.
- A malformed claim-lineage envelope fails soft: base Phoenix metadata remains usable.
- Unknown enum values fail soft to safe defaults.
- ID arrays are deduplicated and bounded.
- A record may not supersede itself, contradict itself, or support itself.
- The same target ID must not appear in more than one of support/contradict/supersede for the same record.
- `pv_authority` remains normalized to `context_only` on read.
- Claim lineage does not change the existing Cortex/tool-learning mutual exclusivity rule.

## Deterministic contradiction model

Contradiction is a relationship between records sharing the same claim key whose bounded normalized claim values are incompatible.

The first implementation should avoid broad semantic inference. Preferred detection order:

1. Explicit relationship supplied by Phoenix.
2. Same `claim_key` + different non-empty `claim_value_hash`.
3. Same stable logical record updated in place is an update, not a contradiction.
4. If evidence is insufficient, leave the relationship unresolved instead of guessing.

Model-assisted semantic contradiction detection may be added later only as advisory evidence and must not independently delete, authorize, or silently resolve records.

## Supersession model

Supersession means a newer record is intended to replace an older conclusion for current-context recall while retaining the older record historically.

A record may be treated as superseding another when:

- Phoenix explicitly writes `supersedes_ids`, or
- a deterministic subsystem update has a stable lineage relationship that proves the newer record replaces the older one.

Superseded records remain queryable and are rendered as historical/superseded context.

## Resolution preference

Resolution preference is recall ranking, not truth deletion.

When multiple records conflict, prefer evidence using deterministic signals in this order:

1. Explicitly verified evidence over merely observed or unverified evidence.
2. Evidence matching the current project/workspace/environment over clearly mismatched historical environment.
3. Explicit supersession links over unresolved contradiction.
4. Newer observation time when verification quality is otherwise comparable.
5. Higher bounded confidence when other signals are comparable.
6. Repeated corroborating evidence over a single isolated observation.

If the evidence remains materially tied or ambiguous, mark the claim `disputed` and surface both sides.

No ranking result grants permission to act.

## Provenance requirements

Existing provenance remains the base:

- source type
- source path
- observed time
- verification command
- verification result
- tool output hash

0.6 may additionally compare provenance for conflict ranking, but must not expose plaintext secrets or retain unrestricted command bodies.

## Recall presentation

Contradiction-aware recall should be compact and explicit. Example lines:

```text
Claim: key=<claim-key> · state=disputed · value=<bounded-value>
Claim links: contradicts=<ids> · supports=<ids> · supersedes=<ids>
Claim resolution: unresolved
Provenance: source=... · verify=... · result=...
Memory authority: context_only
```

For a resolved supersession:

```text
Claim: key=<claim-key> · state=current
Claim links: supersedes=<older-id>
Claim resolution: resolved · basis=newer verified evidence
Historical record retained: <older-id>
Memory authority: context_only
```

## Bank behavior

0.3 routing remains authoritative for placement:

- global claim -> base bank
- workspace/project claim -> deterministic derived workspace bank
- task/session remain metadata, not banks

Contradiction-aware recall may merge global + active-workspace records, but bank origin must remain visible and one bank failure must not invalidate results from the other.

## Compatibility requirements

0.6 must preserve:

- Hindsight-compatible retain / recall / banks / delete behavior
- stock-vs-candidate compatibility harness
- 0.2 Phoenix metadata
- 0.3 bank routing
- 0.4 Cortex-native records
- 0.5 tool outcome / repair learning
- fail-soft parsing
- `context_only` authority
- no production cutover

## Gate plan

### 0.6a — Schema
Implement claim-lineage metadata model, serialization, parser, bounds, exclusivity validation, fail-soft behavior, and unit gate.

### 0.6b — Phoenix write-side adapter
Allow durable Phoenix records to attach bounded claim lineage and deterministic claim keys without changing existing record classes or bank routing.

### 0.6c — Live conflicting-fact round trip
Write two controlled records with the same claim key and incompatible values. Verify both survive with explicit contradiction linkage and provenance.

### 0.6d — Supersession / staleness handling
Add deterministic supersession and stale-evidence classification. Historical records remain retained and queryable.

### 0.6e — Contradiction-aware recall
Merge global/workspace evidence, reconstruct claim lineage, rank evidence deterministically, surface disputed/resolved state, and preserve bank origin + context-only authority.

### 0.6f — Restart + compatibility regression
Clean restart Phoenix + Mnemosyne, verify contradiction/supersession state survives, then run stock 0.10.1 vs candidate 0.10.2 compatibility regression with Reflect allowed to remain MODEL-LIMITED when explicitly skipped.

## 0.6a acceptance criteria

0.6a passes only if:

- schema serializes entirely to Hindsight-compatible string metadata;
- parser round-trips all valid fields;
- invalid/malformed claim data fails soft;
- self-relations and duplicate/conflicting relation categories are rejected or normalized safely;
- list bounds are enforced;
- old metadata without claim lineage is unchanged;
- Cortex and tool-learning records continue to parse normally;
- authority is always `context_only`;
- unit gate passes before live testing.

## Operational note

Do not delete any existing test bank or switch Phoenix production memory defaults during 0.6 development. Stock Hindsight remains the rollback baseline until the broader Mnemosyne production cutover gates are complete.
