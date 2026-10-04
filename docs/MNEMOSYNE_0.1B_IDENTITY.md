# Mnemosyne 0.1b — Phoenix-Native Identity + Integration Readiness

Status: **in development**

The 0.1 API compatibility baseline passed side-by-side against stock Hindsight.
0.1b begins the first Phoenix-native layer while deliberately preserving the
Hindsight-compatible public contract already proven by the baseline test.

## Goal

Phoenix must be able to distinguish a Mnemosyne runtime from stock Hindsight
without changing its existing Hindsight Retain / Recall / Reflect integration.

## Design rule

0.1b is additive.

It does **not** rename or remove:

- `GET /version`
- `POST /v1/default/banks/{bank_id}/memories`
- `POST /v1/default/banks/{bank_id}/memories/recall`
- `POST /v1/default/banks/{bank_id}/reflect`

The stock compatibility surface remains authoritative.

## New identity surface

When the Mnemosyne development launcher is used, it enables the built-in
`MnemosyneIdentityExtension`.

New endpoints:

- `GET /ext/mnemosyne/status`
- `GET /.well-known/project-v-mnemosyne`

The payload identifies:

- product: Project V // Mnemosyne
- role: Phoenix Memory Core
- Mnemosyne version
- underlying Hindsight API compatibility version
- compatibility claims for Retain / Recall / Reflect
- Phoenix contract version
- development/runtime mode
- production-cutover authorization state
- the safety invariant that memory is context, not authority

## Production boundary

`production_cutover_authorized` is hard-coded false during 0.1b.

Stock Hindsight remains Phoenix's production memory runtime. The new identity
surface exists so Phoenix can later detect and validate a candidate before any
endpoint switch or migration is allowed.

## 0.1b validation

1. Start the Mnemosyne candidate with `scripts/start-mnemosyne-dev.ps1`.
2. Confirm stock `GET /version` still reports the same 0.10.2-compatible shape.
3. Confirm `GET /.well-known/project-v-mnemosyne` reports Mnemosyne identity.
4. Confirm `GET /ext/mnemosyne/status` reports the same identity.
5. Re-run `scripts/test-phoenix-compat.ps1 -SkipReflect`.
6. Require the previous Retain / Recall / cleanup / parity gates to continue passing.

Only then should Phoenix Desktop receive candidate-detection UI or endpoint
selection logic.
