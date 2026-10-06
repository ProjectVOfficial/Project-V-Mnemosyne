# Mnemosyne 0.2 — Phoenix Metadata Integration

Status: **started**

The metadata schema and live Retain → Recall preservation gates passed in the
0.1c development slice. 0.2 wires that validated `pv_` schema into Phoenix
Desktop's real memory-producing call sites.

## First implementation slice

Phoenix write-side integration will add `pv_` metadata to:

- durable Phoenix memories mirrored to Hindsight/Mnemosyne;
- bounded tool-outcome experience memories;
- Process Lab experience memories;
- Continuity disposable Retain canaries.

The legacy metadata keys and tags remain in place for backward compatibility.

## Contract advertised by Mnemosyne

`GET /.well-known/project-v-mnemosyne` and
`GET /ext/mnemosyne/status` now advertise:

- `mnemosyne_version = 0.2`
- `compatibility.phoenix_contract = 0.2`
- `phoenix_metadata.schema_version = 1`
- `phoenix_metadata.prefix = pv_`
- `phoenix_metadata.authority = context_only`
- `phoenix_metadata.retain_round_trip_validated = true`

## Safety boundary

Write-side metadata is descriptive only. It cannot authorize a tool or action.
Every Phoenix-produced record sets `pv_authority=context_only`.

## Gates

1. Phoenix TypeScript typecheck.
2. Existing Phoenix behavior remains unchanged with stock Hindsight.
3. Real Phoenix Retain sends `pv_` metadata to Mnemosyne.
4. Recall returns those fields intact.
5. Phoenix read-side integration parses metadata without treating it as authority.
6. Stock-vs-candidate compatibility regression remains PASS.
