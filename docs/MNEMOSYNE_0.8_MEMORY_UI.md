# Mnemosyne 0.8 — Memory UI / Visibility

Status: design baseline for 0.8a  
Branch: `mnemosyne-0.8-memory-ui`

## Purpose

Mnemosyne 0.8 makes Phoenix memory understandable inside Phoenix itself.

The goal is not to add new memory semantics. It is to expose the semantics already implemented in 0.3–0.7 in a safe, readable UI so the operator can inspect where a memory came from, why it ranked where it did, whether it is current or stale, whether it contradicts another record, and which bank/workspace it belongs to.

The invariant remains:

> Memory is context, never authority.

No UI state, remembered approval, score, claim resolution, or retention state may grant execution authority.

## Primary UI goals

1. Show current Mnemosyne connection/status.
2. Show active global + workspace bank identity without leaking unnecessary full paths.
3. Show memory class, source, project/workspace, verification, confidence, provenance, and authority.
4. Show retention score, retention state, component factors, and penalties.
5. Show claim lineage and contradiction/supersession relationships.
6. Show Cortex and tool-learning native fields when present.
7. Show recall ranking: semantic score, retention score, composite score, and whether retention affected ordering.
8. Preserve legacy memories that do not contain newer metadata.
9. Make malformed/partial metadata visibly fail-soft rather than crashing the UI.
10. Keep destructive controls out of 0.8.

## 0.8 UI surfaces

### Memory status card

Compact status surface for the Phoenix sidebar / memory section:

- provider: Mnemosyne
- API status
- candidate version
- active base bank
- active workspace bank
- global/workspace routing status
- last successful recall / retain timestamp
- memory authority badge: `context_only`

### Memory list

Each memory row/card may expose:

- text preview
- memory class
- source
- bank origin: global / workspace
- retention state badge
- retention score
- verification badge
- claim state badge when applicable
- current / stale / disputed / superseded state
- timestamp
- project/workspace label

The default list must remain readable; detailed metadata belongs in the inspector.

### Memory inspector

Selecting a memory opens a detailed inspector with sections:

- Identity
- Source / provenance
- Routing / bank
- Classification
- Verification / outcome
- Retention + score factors
- Claim lineage
- Cortex record
- Tool-learning record
- Related files/process
- Raw Phoenix metadata
- Safety / authority

### Contradiction view

For memories sharing a claim key, show:

- current claim
- stale / historical claims
- contradictions
- supports
- supersedes
- resolution state
- resolution basis

Historical evidence remains visible.

### Score explanation

For scored records:

```text
Retention score: 0.976
State: hot
Verification: 1.000
Confidence: 0.980
Recency: 1.000
Corroboration: 1.000
Utility: 0.800
Environment match: 1.000
Stale penalty: 0.000
Contradiction penalty: 0.000
```

For unscored legacy records:

```text
Retention score: not available
Legacy/unscored record
```

### Recall-rank explanation

When the memory is shown in a recall result:

```text
Composite: 0.882
Semantic: 0.841
Retention: 0.976
Retention used: yes
```

## Data contract

Phoenix UI should receive a normalized view model rather than directly depending on raw Hindsight JSON.

Proposed TypeScript shape:

```ts
type MnemosyneMemoryView = {
  recordId?: string
  text: string
  bank?: {
    id?: string
    scope?: 'global' | 'workspace' | 'unknown'
    workspaceLabel?: string
  }
  source?: {
    type?: string
    project?: string
    workspace?: string
    taskId?: string
    sessionId?: string
    tool?: string
  }
  classification?: {
    memoryClass?: string
    confidence?: number
    verification?: string
    outcome?: string
    reversibility?: string
  }
  provenance?: {
    sourceType?: string
    sourcePath?: string
    observedAt?: string
    verificationCommand?: string
    verificationResult?: string
    toolOutputHash?: string
    sha256?: string
  }
  retention?: {
    score?: number
    state?: 'hot' | 'warm' | 'cold' | 'archive_candidate' | 'protected' | 'unknown'
    scoreVersion?: string
    verificationStrength?: number
    recency?: number
    corroboration?: number
    utility?: number
    environmentMatch?: number
    stalenessPenalty?: number
    contradictionPenalty?: number
    scoredAt?: string
    protectedReason?: string
  }
  claim?: {
    key?: string
    state?: string
    value?: string
    valueHash?: string
    supportsIds?: string[]
    contradictsIds?: string[]
    supersedesIds?: string[]
    resolutionState?: string
    resolutionBasis?: string
    observedAt?: string
    freshness?: 'current' | 'stale' | 'disputed' | 'historical' | 'unknown'
    supersededBy?: string[]
  }
  cortex?: Record<string, unknown>
  toolLearning?: Record<string, unknown>
  recallRank?: {
    semanticScore?: number
    retentionScore?: number
    compositeScore?: number
    usedRetention?: boolean
  }
  authority: 'context_only'
  rawMetadata?: Record<string, string>
}
```

## Normalization rules

- UI consumes normalized camelCase fields.
- Legacy `pv_claim_claim_key` remains readable as an alias for canonical `pv_claim_key`.
- Unknown enums display `unknown`; they do not crash the UI.
- Missing retention metadata displays legacy/unscored state.
- Missing claim metadata simply hides claim sections.
- Malformed extension metadata hides only the malformed extension section.
- Raw metadata remains read-only.
- Full workspace paths should be omitted from compact cards when a safer label is available.
- Authority is always rendered as `context_only` regardless of recalled raw value.

## Visual priority

High-priority badges:

- protected
- disputed
- stale
- superseded
- failed verification
- context_only

Normal badges:

- hot / warm / cold
- current
- verified
- global / workspace

Avoid red/alert styling for ordinary cold/archive_candidate memories; those are lifecycle states, not errors.

## No destructive actions in 0.8

The UI must not expose:

- delete memory
- prune
- archive now
- force score
- force supersession
- modify raw metadata
- change authority

Those behaviors require later explicit policy and safety gates.

## Gate plan

### 0.8a — UI architecture + normalized data contract
Define and test the Phoenix-side memory view model / normalizer. No visible UI changes yet.

### 0.8b — Memory status + list shell
Add the Mnemosyne status card and memory-list surface using the normalized contract.

### 0.8c — Memory inspector
Add detailed read-only inspector for provenance, routing, classification, Cortex, tool-learning, and raw metadata.

### 0.8d — Filters + badges
Add safe filters for bank/scope, class, retention state, verification, claim state, and current/stale/disputed.

### 0.8e — Contradiction + score visibility
Add claim-lineage relationship display, score breakdown, penalties, and recall-rank explanation.

### 0.8f — Live UI + restart regression
Validate real 0.6/0.7 test records, legacy records, workspace/global records, malformed metadata, restart survival, and compatibility behavior.

## 0.8a acceptance criteria

0.8a passes only if the normalizer:

- parses the current Phoenix/Mnemosyne metadata shapes;
- preserves global/workspace bank origin;
- exposes retention score/state/components;
- exposes claim lineage + freshness;
- exposes Cortex and tool-learning envelopes;
- exposes recall-rank fields;
- supports legacy unscored memories;
- supports legacy claim-key alias;
- fails soft on malformed optional sections;
- never trusts recalled authority;
- emits `authority: context_only`;
- has deterministic unit coverage.

## Operational policy

0.8 is read-only visibility work. It must not delete, prune, migrate, archive, alter scores, resolve claims, change authority, or switch production defaults.
