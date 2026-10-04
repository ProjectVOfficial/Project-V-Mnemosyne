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


---

# Post-1.0 — Mnemosyne Memory Mesh

The earlier Phoenix development tracker used `MN-0.x` identifiers for the
**Memory Mesh** work. Those labels are preserved below as historical mesh-stage
IDs; they are separate from the current Mnemosyne core implementation numbers
above.

The core design rule is:

> Phoenix talks to Mnemosyne. Mnemosyne routes to memory providers, caches and
> workers. Physical RAM accelerates recall, but durable stores remain the source
> of truth.

## Mesh architecture

```text
Phoenix / Phoenix workers
          |
          v
Project-V-Mnemosyne
Director / Router / Arbitration
          |
    +-----+-----------------------------+
    |                                   |
    v                                   v
L1 Hot RAM Payload Cache        L2 RAM Pointer / Vector Directory
    |                                   |
    +----------------+------------------+
                     v
           Memory Retrieval Worker
                     |
       +-------------+-------------+------------------+
       |             |             |                  |
       v             v             v                  v
 Selected Local   Hindsight    State/Dossiers     Optional Graph
     Core          Experience   HMLR-inspired      MemoryBear/core
                     |
                     v
             Shared task/continuity
               relay for workers
```

RAM is a **volatile acceleration tier, not permanent truth**. Full durable
memories continue to live in the selected local core and specialist providers.
Mnemosyne keeps a bounded RAM-resident directory and a bounded hot-payload
cache so Phoenix can avoid rescanning entire stores and avoid repeatedly asking
the main LLM to perform routine memory plumbing.

## Historical Memory Mesh stages

### MN-0.1 — Memory Provider Contract

Define normalized capture, recall, temporal recall, get, search, contradict,
reinforce, archive, health and backup contracts so Phoenix can swap providers
without rewrites.

**Exit gate:** phase-specific provider-contract validation passes.

### MN-0.1a — Memory Engine Bake-Off

Benchmark the current SQLite + Hindsight stack against MemOS Local and the iai
Personal Memory Engine on the same Phoenix corpus.

Measure:

- recall quality
- contradiction handling
- temporal recall
- latency
- RAM use
- disk use
- Windows stability
- recovery behavior
- local-model compatibility
- portable-storage compatibility

Production memory does not change during the bake-off.

**Exit gate:** a documented benchmark identifies the preferred local-core
direction.

### MN-0.2 — Unified Recall Router

Classify each memory request and route or fan out to the best provider(s).
Normalize, rank, deduplicate and reconcile results while preserving source
attribution.

### MN-0.2a — RAM Memory Directory + Vector Pointer Index

Maintain a fast RAM-resident directory containing:

- memory ID
- provider/store
- exact record pointer
- memory type
- timestamp
- importance
- keywords
- embeddings

Phoenix receives IDs/pointers first; Mnemosyne fetches only the exact
underlying records needed.

**Exit gate:** correct provider/location resolution without full-store scans.

### MN-0.2b — Hot RAM Payload Cache

Maintain a bounded L1 cache for recently/frequently used full memory payloads.

Fast path:

```text
L1 hot payload hit
        |
        +-- miss --> L2 pointer/vector index
                         |
                         v
                  exact provider fetch
                         |
                         v
                    warm L1 cache
```

**Exit gate:** bounded RAM use with measurable recall-latency improvement.

### MN-0.2c — Dedicated Memory Retrieval Worker

Use a small local retrieval stack for routine memory work:

- embedder
- reranker
- rules / small classifier
- optional tiny LLM only for difficult routing

Phoenix's main model should not spend routine tokens/workload on memory
plumbing.

**Exit gate:** retrieval accuracy is preserved while main-model workload drops.

### MN-0.2d — Adaptive Prefetch + Cache Warming

Preload likely-needed memories from active:

- project
- session
- process
- workspace/task context

Measure cache hit rate, recall latency, provider calls avoided, RAM cost and
tokens saved.

### MN-0.3 — Local Core Selection

Choose MemOS Local, iai Personal Memory Engine, or a Phoenix-native core from
bake-off evidence. If neither external candidate fits cleanly, reuse useful
architecture while retaining Phoenix control.

**Exit gate:** selected core passes Windows, local-first, recovery and portable
storage gates.

### MN-0.4 — Hindsight Experience Adapter

Keep Hindsight initially as a specialist provider for:

- prior attempts
- failures
- tool outcomes
- lessons learned
- episodic/experiential recall

Long-term retention is evidence-based rather than assumed.

### MN-0.5 — HMLR-Inspired State + Dossiers

Add temporal supersession, causal/state dossiers, current-truth
reconstruction, alias/history chains and project-state summaries.

HMLR is primarily an architecture source; it does not need to remain a
permanent service unless testing justifies that cost.

### MN-0.5b — Memory Gardener Worker

Run low-cost background memory maintenance:

- deduplication
- clustering
- dossier maintenance
- stale-state review
- reinforcement/decay
- provider-to-provider promotion
- Hot/Warm/Cold tier maintenance

### MN-0.6 — Reserved

Reserved for the mesh feature that proves necessary during the 0.1–0.5
integration and bake-off work rather than assigning it prematurely.

### MN-0.7 — Shared Memory Service + Task Relay

Borrow the useful Memmy-style pattern so Phoenix workers can share controlled
Mnemosyne memory and structured task-relay packets.

Initial participants:

- Phoenix
- Browser Worker
- Repair Agent
- Model Council
- Dream Lab
- Toolsmith
- future specialized subagents

**Exit gate:** a cross-agent handoff resumes work without manually rebuilding
the original context.

### MN-0.8 — Adaptive Memory Lifecycle

Add:

- Hot/Warm/Cold tiers
- reinforcement
- pin/protect
- dormancy
- archival
- decay
- contradiction history
- prefetch policy
- memory-strength controls

### MN-0.9 — Provider Cleanup + Role Decision

Measure which providers/components actually earn their runtime cost. Keep,
fork, absorb or remove Hindsight, MemoryBear, MemOS, iai-related components
based on observed contribution.

### MN-1.0 — Production Mnemosyne Memory Mesh

Promotion requires the compact mesh to operate as a coherent Phoenix memory
service with:

- stable provider contracts
- measured RAM bounds
- deterministic provider attribution
- fast pointer-based retrieval
- proven hot-cache value
- cross-agent continuity
- lifecycle/retention controls
- backup/recovery
- no loss of Phoenix permission boundaries

## Memory project evaluation matrix

| Project | Planned role | Direct use? | What Phoenix wants | Decision gate |
| --- | --- | --- | --- | --- |
| Hindsight | Experiential / episodic specialist | Yes, initially | Prior attempts, failures, tool outcomes, lessons | Retain only if it adds unique value after Mnemosyne is operating |
| MemOS | Local-core / memory-OS candidate | Evaluate | Unified memory API, scheduler, local plugin, memory cubes, tiering/evolution | Compare head-to-head in MN-0.1a |
| iai Personal Memory Engine | Local-core candidate | Evaluate | Local semantic/personal memory capabilities | Compare head-to-head in MN-0.1a |
| HMLR | State/dossier architecture source | Mostly concepts/code ideas | Temporal supersession, current-state reconstruction, dossiers, causal chains | Absorb useful architecture unless runtime testing justifies a service |
| MemoryBear | Optional graph specialist | Maybe later | Entity relationships, temporal graph, GraphRAG, multi-hop knowledge | Add only if selected core does not meet graph requirements |
| Memmy Agent | Cross-agent continuity architecture source | Mostly concepts | Shared local memory service, namespaces, adapters, task-relay/handoff patterns | Absorb into Mnemosyne shared-memory/task-relay layer |

## Target compact Memory Mesh

| Layer | Component | Role | Default behavior | Optional? |
| --- | --- | --- | --- | --- |
| Director | Project-V-Mnemosyne | Routing, arbitration, provenance, permissions, lifecycle | Always present | No |
| L1 | Hot RAM Payload Cache | Fast payload reuse | Immediate return on hit | No |
| L2 | RAM Pointer / Vector Directory | Find exact record/store quickly | Return IDs/pointers | No |
| Worker | Memory Retrieval Worker | Classification, embedding, reranking, compact packets | Small local stack | No |
| Core | Selected Local Core | Durable local semantic/personal memory | Chosen after bake-off | No |
| Experience | Hindsight | Prior outcomes/episodes | Specialist provider | Yes |
| State | Dossiers / HMLR-inspired logic | Temporal state/current-truth reconstruction | Derived by Mnemosyne | No |
| Graph | MemoryBear or core graph | Deep relationship/GraphRAG | Only if measurable value exists | Yes |
| Continuity | Memmy-inspired relay layer | Shared memory + task handoff for workers | Mnemosyne service | No |

## Physical-RAM design rule

The Memory Mesh deliberately uses the computer's actual system RAM as a fast
working-memory tier:

- **L1 RAM** holds bounded full payloads that are hot/recent/frequently reused.
- **L2 RAM** holds the much larger pointer/vector directory so Mnemosyne can
  identify exact durable records quickly.
- **Prefetch** warms likely-needed entries from the active Phoenix project,
  session, process and task context.
- **Eviction** keeps RAM bounded; cold payloads are discarded from RAM without
  deleting durable memory.
- **Restart behavior:** RAM tiers are rebuilt from durable stores and indexes.
- **Authority:** cached content remains context only; caching never grants
  permission or execution authority.

This gives Phoenix a practical short-term/high-speed memory layer backed by
durable long-term stores instead of trying to use RAM as permanent storage.
