# Project V // Mnemosyne Roadmap

## Goal

Create a Phoenix-specific memory core by extending the Hindsight foundation without discarding its mature retrieval, entity, temporal, observation, and storage architecture.

The project follows a compatibility-first approach: preserve the existing Phoenix memory contract, add Phoenix semantics incrementally, and promote only after side-by-side validation.

---

## 0.1 — Fork + API compatibility

**Objective:** prove that the Project V fork can function as a drop-in local Hindsight-compatible runtime.

Planned work:

- preserve retain / recall / reflect behavior
- preserve memory-bank APIs
- preserve `phoenix-core`
- preserve Phoenix health checks
- preserve local managed-runtime lifecycle expectations
- preserve backup/export behavior
- document upstream remote configuration
- establish stock-Hindsight rollback procedure
- create a Phoenix compatibility test set

**Exit gate:** current Phoenix memory tests behave equivalently against stock Hindsight and Mnemosyne.

---

## 0.2 — Phoenix metadata schema

Add structured metadata for:

- source
- workspace
- project
- task/session IDs
- tool
- memory class
- confidence
- authority
- outcome
- verification
- reversibility
- related files/processes
- Cortex topic

**Core invariant:** memory metadata cannot grant execution authority.

---

## 0.3 — Workspace and project bank routing

Add project-aware routing while retaining `phoenix-core`.

Potential banks:

- `phoenix-core`
- `phoenix-project-watchtower`
- `phoenix-project-gatekeeper`
- `phoenix-project-blacklight`
- `phoenix-project-process-lab`
- `phoenix-experiments`

Cross-bank recall should be possible for tasks spanning multiple projects.

No destructive split of the existing production bank.

---

## 0.4 — Cortex-native memory records

Preserve structured Phoenix intelligence concepts including:

- belief
- evidence
- confidence
- contradiction
- knowledge gap
- prediction
- outcome
- lesson

Cortex records should remain queryable without being flattened into generic conversation memory.

---

## 0.5 — Tool outcome + repair learning

Add compact operational memories for:

- task
- attempted action
- tool
- working directory
- verification command
- result
- failure reason
- successful repair
- lesson learned

Use these memories to help future ReAct tasks prefer previously verified approaches and avoid repeated known failures.

---

## 0.6 — Provenance + contradiction engine

Add stronger provenance:

- source type
- source path
- line/range
- timestamp
- content hash
- tool output
- verification result

Support temporally aware contradictions and superseded facts without blindly deleting history.

---

## 0.7 — Retention + scoring policies

Introduce retention classes:

- ephemeral
- session
- time-limited
- project
- permanent

Score candidate memories for:

- future usefulness
- durability
- confidence
- novelty
- redundancy
- sensitivity

Reduce memory pollution while preserving high-value operational knowledge.

---

## 0.8 — Phoenix Memory Core UI

Add Phoenix-native UI surfaces for:

- Overview
- Memories
- Projects
- Lessons
- Contradictions
- Cortex
- Backups
- Diagnostics

Expose health/status without requiring the generic upstream control interface for normal Phoenix operation.

---

## 0.9 — Migration / backup / portable hardening

- import a copy of `phoenix-core`
- validate memory counts
- validate known recall cases
- validate reflect
- validate Cortex continuity
- validate backup/restore
- validate crash/restart behavior
- respect Phoenix-selected local/portable data roots
- verify no hardcoded machine-specific paths

---

## 1.0 — Stable Phoenix Memory Core

Promotion requirements:

- equal or better recall on the Phoenix validation set
- no demonstrated memory loss during migration
- Cortex continuity passes
- repair-learning retrieval passes
- backup/restore passes
- portable/local storage passes
- Phoenix can revert to stock Hindsight if required
- production permission model remains unchanged

Only after these gates pass should Mnemosyne replace stock Hindsight as Phoenix's default memory engine.

---

## Upstream tracking

Keep the original Hindsight repository configured as an upstream remote in development clones.

Regularly evaluate upstream:

- bug fixes
- retrieval improvements
- schema/database migrations
- performance improvements
- security fixes
- provider/runtime compatibility changes

Project V-specific functionality should be isolated where practical to reduce merge friction.
