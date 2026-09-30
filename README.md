# Project V // Mnemosyne

**Phoenix Memory Core**

Project V // Mnemosyne is a downstream fork of [Vectorize Hindsight](https://github.com/vectorize-io/hindsight), adapted for **Project V // Phoenix**.

The project begins with Hindsight's existing agent-memory architecture and retain / recall / reflect APIs, then adds Phoenix-specific memory semantics, Cortex continuity, repair learning, provenance, project-aware routing, retention policies, and portable/local-storage integration.

> **Current stage:** 0.1 planning / compatibility baseline  
> **Upstream:** `vectorize-io/hindsight`  
> **Phoenix production memory:** stock Hindsight remains authoritative until Mnemosyne passes side-by-side validation  
> **License:** inherited upstream MIT license applies to the covered upstream-derived code; see [LICENSE](LICENSE)

---

## Why Mnemosyne exists

Phoenix already uses Hindsight successfully as a local experience-memory sidecar.

Rather than replace a mature memory engine from scratch, Project V is taking a **compatibility-first fork** approach:

1. preserve Hindsight's proven memory engine;
2. keep Phoenix's existing Hindsight integration working;
3. add Phoenix-native metadata and memory behavior;
4. validate Mnemosyne beside stock Hindsight;
5. migrate only after recall/reflect parity and memory-safety checks pass.

The goal is not merely to remember conversations.

The long-term goal is for Phoenix to remember:

- what happened;
- what she tried;
- what failed;
- what succeeded;
- what evidence verified the outcome;
- which project/task the event belonged to;
- how confident the memory should be;
- whether newer evidence contradicts it;
- and, critically, that remembered context **never grants execution authority**.

---

## Compatibility first

The first Mnemosyne milestone must remain compatible with Phoenix's existing memory contract.

Initial compatibility targets include:

- `retain`
- `recall`
- `reflect`
- memory-bank handling
- the current `phoenix-core` bank
- Phoenix Hindsight health checks
- Phoenix-managed local lifecycle controls
- backup/export behavior
- local Ollama-based operation where configured

Phoenix should initially be able to switch between stock Hindsight and Mnemosyne without requiring a rewrite of the Intelligence Core.

---

## Planned Phoenix extensions

### Phoenix-native memory metadata

Mnemosyne will progressively add structured metadata such as:

- source
- workspace
- project
- task ID
- session ID
- tool
- memory class
- confidence
- authority
- outcome
- verification
- reversibility
- related files
- related process
- Cortex topic

### Memory classes

Planned Phoenix-specific memory classes include:

- conversation
- user preference
- project fact
- architecture decision
- tool result
- repair attempt
- failure
- successful pattern
- protocol event
- Cortex evidence
- Watchtower context
- security event
- experiment result

### Cortex-native continuity

Mnemosyne is intended to preserve structured Cortex concepts such as:

- beliefs
- evidence
- confidence
- contradictions
- knowledge gaps
- predictions
- outcomes
- lessons learned

rather than flattening all of them into ordinary conversational text.

### Tool outcome and repair learning

Phoenix should be able to retain compact operational records describing:

- the task;
- the action taken;
- the tool used;
- the verification command;
- the result;
- the lesson learned.

This is intended to improve future ReAct and autonomous-repair behavior by prioritizing approaches that were actually verified.

### Provenance and contradiction handling

Important memories should be able to retain provenance such as:

- source type
- source path
- line/range
- timestamp
- hash
- tool output
- verification result

New evidence should not silently erase older evidence when both remain useful. Mnemosyne should preserve time/source context so Phoenix can reason about superseded or conflicting facts.

### Project-aware memory routing

Mnemosyne may eventually support project-scoped banks such as:

- `phoenix-core`
- `phoenix-project-watchtower`
- `phoenix-project-gatekeeper`
- `phoenix-project-blacklight`
- `phoenix-project-process-lab`
- `phoenix-experiments`

The existing `phoenix-core` bank will not be destructively split during the early phases.

### Retention and scoring

Future memory retention may classify records as:

- ephemeral
- session
- time-limited
- project
- permanent

with scoring based on usefulness, durability, confidence, novelty, redundancy, and sensitivity.

---

## Safety rule: memory is context, not authority

This rule is fundamental to Phoenix and remains fundamental to Mnemosyne.

A recalled memory can inform reasoning, but it does **not** authorize:

- terminal commands;
- file writes;
- Registry changes;
- process control;
- destructive operations;
- elevated actions;
- protocol execution;
- any other permission-controlled tool.

A memory that says an action was previously approved is historical context, not current approval.

---

## Migration policy

There will be no destructive first migration.

The planned transition is:

1. back up the current Hindsight `phoenix-core` bank;
2. run Mnemosyne side-by-side with stock Hindsight;
3. migrate/import a copy;
4. compare memory counts;
5. run known recall tests;
6. run reflect tests;
7. test Cortex continuity;
8. test failure and repair-memory retrieval;
9. validate backup/restore;
10. switch Phoenix only after parity or improvement is demonstrated.

Stock Hindsight remains the rollback path until the new memory core is validated.

---

## Upstream relationship

Mnemosyne is derived from Hindsight and is **not** presented as the original Hindsight project.

Project V intends to keep an upstream relationship so relevant Hindsight fixes and improvements can be evaluated and selectively merged.

Upstream project:

https://github.com/vectorize-io/hindsight

Original upstream copyright and license notices remain applicable to upstream-derived material.

Project V modifications and additions will be identified as downstream Project V work.

See [PROJECT_V_NOTICE.md](PROJECT_V_NOTICE.md).

---

## Roadmap

See [docs/PROJECT_V_ROADMAP.md](docs/PROJECT_V_ROADMAP.md) for the staged 0.1 → 1.0 plan.

---

## Phoenix integration status

Phoenix currently uses the existing Hindsight integration and the `phoenix-core` bank.

**Do not point production Phoenix at Mnemosyne yet.**

The first development objective is API compatibility and side-by-side validation, not immediate replacement.

---

**Project V Official**  
**Project V // Mnemosyne — Phoenix Memory Core**
