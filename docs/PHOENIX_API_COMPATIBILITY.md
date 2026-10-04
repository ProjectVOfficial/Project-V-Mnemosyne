# Phoenix ↔ Mnemosyne 0.1 API Compatibility Contract

Status: **0.1 development contract**

Mnemosyne 0.1 is compatibility-first. Phoenix must be able to point its existing
Hindsight integration at a Mnemosyne process without rewriting Intelligence Core
memory calls or weakening Phoenix's permission model.

## Production rule

Stock Hindsight remains Phoenix's production memory runtime until this contract
passes side-by-side validation. Mnemosyne 0.1 must use isolated test banks and
must not mutate the production `phoenix-core` bank during development.

## Baseline

The fork currently carries Hindsight API package version **0.10.2**.

For 0.1, the public Hindsight-compatible surface stays Hindsight-compatible.
Branding work must not break request or response shapes Phoenix already consumes.

## Required Phoenix surface

### Health / capability probe

- `GET /version`
- HTTP 200
- response contains string `api_version`
- response contains object `features`
- existing Hindsight feature keys remain available

Phoenix uses the version/capability probe as part of managed-runtime and
Continuity health checks.

### Bank compatibility

Phoenix's existing default bank remains:

- `phoenix-core`

Mnemosyne must continue accepting arbitrary isolated bank IDs through the same
bank routes. The 0.1 test harness uses disposable compatibility-test banks; it
never needs the production `phoenix-core` bank.

Required bank operations for validation:

- `GET /v1/default/banks`
- `DELETE /v1/default/banks/{bank_id}` for cleanup of disposable test banks

### Retain

- `POST /v1/default/banks/{bank_id}/memories`
- request body remains compatible with Hindsight `RetainRequest`
- Phoenix-required fields/behaviors include:
  - `items[].content`
  - optional `context`
  - optional `timestamp`
  - optional `document_id`
  - optional `tags`
  - synchronous retain (`async=false`) remains supported

A successful retain is a hard 0.1 gate.

### Recall

- `POST /v1/default/banks/{bank_id}/memories/recall`
- request remains compatible with:
  - `query`
  - optional `types`
  - `budget`
  - `max_tokens`
  - optional tags/filtering
- response continues exposing `results[]`
- each recalled fact used by Phoenix continues exposing text via `results[].text`

A canary retained by the test must be recallable from the same disposable bank.
Recall parity is a hard 0.1 gate.

### Reflect

- `POST /v1/default/banks/{bank_id}/reflect`
- request remains compatible with:
  - `query`
  - legacy-compatible optional `context`
  - `budget`
  - `max_tokens`
- response continues exposing synthesized markdown in `text`

Phoenix already has a Recall + local synthesis fallback when the configured
Hindsight worker model cannot satisfy Reflect's tool-calling contract. Therefore:

- API/schema breakage or unrelated Reflect failures: **FAIL**
- known worker-model tool-calling limitation with Retain + Recall passing:
  **MODEL-LIMITED / ACCEPTABLE FOR 0.1**

## Safety invariant

Memory is context, not authority.

Nothing in Mnemosyne 0.1 may cause recalled content, metadata, prior approvals,
or prior successful actions to bypass Phoenix's current permission,
confirmation, or guarded-tool paths.

## Side-by-side validation sequence

1. Start stock Hindsight on one loopback port.
2. Start Mnemosyne candidate on a different loopback port and isolated data root.
3. Run `scripts/phoenix_compat_smoke.py` against both endpoints.
4. Compare:
   - version/capability probe
   - Retain acceptance
   - Recall canary recovery
   - Reflect contract classification
   - bank visibility / cleanup
5. Confirm the stock production runtime and `phoenix-core` bank were untouched.
6. Only after repeated PASS results should Phoenix be given a selectable
   Mnemosyne endpoint for non-production testing.

## 0.1 exit gate

Mnemosyne 0.1 exits only when Phoenix's current memory compatibility tests behave
equivalently against stock Hindsight and Mnemosyne, with no demonstrated loss of
the required public contract and with stock Hindsight retained as rollback.
