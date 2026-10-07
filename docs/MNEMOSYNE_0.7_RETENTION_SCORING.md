# Mnemosyne 0.7 — Retention + Scoring

Status: design baseline for 0.7a  
Branch: `mnemosyne-0.7-retention-scoring`

## Purpose

Mnemosyne 0.7 adds deterministic memory scoring and bounded retention state so Phoenix can prefer useful, verified, current evidence without deleting history or allowing recalled memory to become authority.

The core invariant remains:

> Memory is context, never authority.

Scoring changes retrieval preference only. It never grants permission to execute, write, install, modify processes, elevate privileges, or perform destructive actions.

## Design goals

1. Give each Phoenix-native memory a deterministic bounded score.
2. Prefer verified, current, corroborated, relevant evidence over stale or weak evidence.
3. Preserve contradiction/supersession semantics from 0.6.
4. Distinguish retrieval priority from retention state.
5. Never silently delete memories during 0.7.
6. Preserve pinned/protected records.
7. Keep scoring explainable: every score must expose its component breakdown.
8. Preserve Hindsight API compatibility and existing Phoenix metadata.
9. Keep bank routing unchanged.

## Non-goals

- No automatic destructive deletion.
- No production cutover.
- No model-only hidden score.
- No secret-bearing score inputs.
- No memory-derived authorization.
- No compaction/migration rewrite of existing banks.
- No long-term archival transport; 0.9 remains responsible for migration/backup/portable behavior.

## 0.7 score model

All component values are bounded to `[0,1]`.

### Positive components

- `verification_strength`
  - strongest signal
  - test/operator/command verified > observed > self-reported > unverified

- `confidence`
  - Phoenix-native confidence already stored in metadata

- `recency`
  - deterministic time decay from observed time
  - bounded floor so older verified facts do not disappear from retrieval

- `corroboration`
  - repeated independent supporting evidence raises score
  - duplicate copies of the same stable record do not count as independent corroboration

- `utility`
  - bounded record usefulness signal
  - may begin with conservative defaults and later learn from successful recall/use

- `environment_match`
  - active workspace/project/environment match
  - mismatched historical environments are down-ranked, not deleted

### Penalties / modifiers

- `staleness_penalty`
  - explicit 0.6 supersession/stale status lowers current-recall priority

- `unresolved_contradiction_penalty`
  - disputed unresolved claims receive a bounded penalty
  - both sides remain visible when materially relevant

- `failure_penalty`
  - failed tool outcomes are not globally suppressed; penalty applies only when ranking them as reusable success evidence

- `pinned_floor`
  - pinned/protected memory cannot fall below a minimum retrieval floor

## Initial deterministic weighting

The first implementation should use explicit weights, not model judgment:

- verification strength: 0.30
- confidence: 0.20
- recency: 0.15
- corroboration: 0.15
- utility: 0.10
- environment match: 0.10

Penalties are applied after the positive weighted score and the result is clamped to `[0,1]`.

Initial penalties:

- explicit stale/superseded: -0.25
- unresolved disputed claim: -0.10
- environment mismatch: represented through the environment component rather than an extra penalty

These constants are versioned and must be test-covered so future tuning is intentional.

## Retention state

Retention state is separate from score:

- `hot`
  - frequently/currently useful memory; normal priority

- `warm`
  - useful but less active

- `cold`
  - low-priority historical context still retained

- `archive_candidate`
  - eligible for future compaction/archive review, but NOT deleted in 0.7

- `protected`
  - pinned, constitutional, safety-critical, or explicitly protected memory

No state in 0.7 causes deletion.

## Proposed metadata

`pv_retention_schema_version=1`

- `pv_retention_score`
- `pv_retention_state`
- `pv_retention_score_version`
- `pv_retention_verification_strength`
- `pv_retention_recency`
- `pv_retention_corroboration`
- `pv_retention_utility`
- `pv_retention_environment_match`
- `pv_retention_staleness_penalty`
- `pv_retention_contradiction_penalty`
- `pv_retention_scored_at`
- `pv_retention_protected_reason`

All serialized values remain Hindsight-compatible strings.

## Score explainability

Recall/debug output should be able to show:

```text
Memory score: 0.86 · state=hot · version=1
Score factors: verification=1.00 · confidence=0.98 · recency=0.91 · corroboration=0.70 · utility=0.60 · environment=1.00
Score penalties: stale=0.00 · contradiction=0.00
Memory authority: context_only
```

A stale historical record may still appear:

```text
Memory score: 0.49 · state=cold · version=1
Score penalties: stale=0.25 · contradiction=0.00
Historical evidence retained.
Memory authority: context_only
```

## Interaction with 0.6 contradiction engine

0.6 claim resolution remains authoritative for current/stale/disputed classification.

0.7 may use those classifications as score inputs but must not reinterpret or erase contradiction history.

Examples:

- current resolved claim: normal scoring
- stale superseded claim: apply bounded stale penalty
- unresolved disputed claim: apply contradiction penalty and preserve both sides
- historical record: may rank lower, remains queryable

## Retention policy safeguards

- No deletion in 0.7.
- No score can change `pv_authority=context_only`.
- Pinned/protected records receive a minimum floor and cannot become archive candidates.
- Constitutional/safety records are protected regardless of age.
- Tool failure memories remain available for repair learning even when low-ranked for success-pattern reuse.
- Stable IDs remain stable; rescoring updates metadata/state, not logical identity.

## Gate plan

### 0.7a — Score/retention schema
Add bounded score metadata, retention enums, versioned weights/constants, serialization, parsing, fail-soft behavior, and unit tests.

### 0.7b — Deterministic scoring engine
Implement verification/confidence/recency/corroboration/utility/environment components plus stale/contradiction modifiers.

### 0.7c — Live score round trip
Write controlled memories with different verification/confidence/age/claim state and prove stored score metadata + ordering.

### 0.7d — Retention-state classifier
Map score/protection/currentness to hot/warm/cold/archive_candidate/protected without deletion.

### 0.7e — Score-aware recall
Integrate deterministic score into Phoenix recall ordering while preserving contradiction-aware recall, bank origin, and explainability.

### 0.7f — Restart + compatibility regression
Restart Phoenix + Mnemosyne, prove scores/retention state survive, then run stock Hindsight 0.10.1 vs Mnemosyne candidate 0.10.2 compatibility regression.

## 0.7a acceptance criteria

0.7a passes only if:

- all score fields are bounded;
- score version is explicit;
- retention state is validated;
- all metadata serializes to `dict[str,str]`;
- malformed retention metadata fails soft;
- legacy memories without retention metadata parse unchanged;
- claim/Cortex/tool-learning metadata continue to parse;
- protected state cannot be downgraded by malformed recalled metadata;
- authority is always normalized to `context_only`;
- unit gate passes before live scoring behavior is enabled.

## Operational policy

0.7 must not delete, prune, compact, migrate, or switch production defaults. Stock Hindsight remains the rollback baseline until the broader Mnemosyne production-cutover gates are complete.
