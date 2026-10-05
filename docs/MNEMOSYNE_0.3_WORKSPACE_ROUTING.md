# Mnemosyne 0.3 — Workspace / Project Bank Routing

Status: **development design**

## Goal

Route Phoenix memories into deterministic Mnemosyne banks based on memory scope,
without changing Phoenix's local SQLite source-of-truth model and without allowing
memory to become authority.

Mnemosyne 0.3 is intentionally narrow: it introduces **global + active-workspace
routing**. Task/session identity remains metadata in 0.3 rather than creating an
unbounded bank per task or chat.

## Safety invariant

Memory is context, never authority.

Changing the bank a memory is stored in must not bypass Phoenix permission,
confirmation, guarded-tool, destructive-action, elevation, or current-approval
checks. Recalled historical approval remains historical context only.

## Routing model

### Global memory

Phoenix memories with a global scope route to the configured base bank.

Example:

```text
configured base bank: phoenix-core
global route:         phoenix-core
```

During development we use an isolated test base bank and do not mutate the
production `phoenix-core` bank.

### Workspace / project memory

A memory scoped to a working directory routes to a deterministic workspace bank.

Proposed shape:

```text
<base>-ws-<slug>-<hash>
```

Example:

```text
base:      phoenix-mnemosyne-03-routing-test
workspace: D:\PROJECTS\Phoenix-Desktop
bank:      phoenix-mnemosyne-03-routing-test-ws-phoenix-desktop-<hash>
```

The hash is derived from the normalized workspace path. This keeps routing stable
across restarts while avoiding reliance on a human-readable slug alone.

## Normalization requirements

Workspace normalization must be deterministic:

- trim surrounding whitespace
- normalize slash direction for hashing
- normalize Windows drive-letter case
- remove redundant trailing separators except for a filesystem root
- preserve enough identity so two distinct directories do not collapse to one route
- never use raw memory content in a bank ID

The human-readable slug is cosmetic. The hash is the collision-resistant identity.

## Bank ID constraints

Generated bank IDs must:

- use only Phoenix/Hindsight-safe characters
- remain under the existing bank ID size budget
- be deterministic for the same normalized workspace
- not expose full absolute paths
- fall back safely when a workspace name cannot produce a useful slug

## Write routing

Phoenix's durable local SQLite memory remains the source of truth.

When Hindsight/Mnemosyne mirroring is enabled:

- `scope=global` -> retain into the configured base bank
- `scope=working-directory` with a valid `scopeKey` -> retain into the derived workspace bank
- malformed/missing workspace scope -> fail closed to the base bank rather than inventing a route
- `source=session` remains excluded from Hindsight mirroring under the existing Phoenix rule

Every retained record continues carrying the 0.2 `pv_*` metadata envelope.

## Recall routing

For an active workspace, Phoenix should recall from both:

1. the configured base/global bank
2. the deterministic active-workspace bank

For no active workspace, Phoenix recalls only from the base/global bank.

Results are merged, deduplicated, bounded by Phoenix's existing source limits, and
then passed through the existing 0.2 metadata parser/context-only safety layer.

A workspace recall failure must not make global recall fail, and vice versa. The
response should preserve enough diagnostics to show which routed bank failed.

## Compatibility

The existing single-bank Hindsight adapter contract remains valid.

0.3 should add a routing layer above the adapter rather than changing Mnemosyne's
public Hindsight-compatible HTTP routes. Stock Hindsight should continue to work
for a single configured bank.

## 0.3 implementation gates

### 0.3a — Pure bank resolver

Add a small Phoenix-side resolver with unit-testable behavior:

- base bank normalization
- workspace normalization
- deterministic workspace bank ID
- no-workspace fallback

No live memory behavior changes in this gate.

### 0.3b — Write routing

Route mirrored durable memories to the appropriate base/workspace bank while
preserving the 0.2 metadata envelope.

### 0.3c — Multi-bank recall

Recall from base + active workspace, merge/dedupe results, and preserve
source-bank diagnostics.

### 0.3d — Live isolation validation

Using disposable banks, prove:

- global memory appears only in the base test bank
- workspace A memory appears in workspace A bank
- workspace B memory appears in workspace B bank
- workspace A recall does not accidentally import workspace B-only memory
- global memory remains available alongside the active workspace

### 0.3e — Restart / deterministic routing

Restart Phoenix/Mnemosyne and prove the same workspace resolves to the exact same
bank ID and recalls the same durable data.

### 0.3f — Compatibility regression

Re-run the Phoenix <-> Hindsight/Mnemosyne compatibility suite and confirm 0.3
introduced no public API regression.

## Exit gate

Mnemosyne 0.3 is complete only when workspace routing is deterministic, isolated,
restart-stable, compatible with the 0.2 metadata contract, and does not weaken
Phoenix's current permission model.
