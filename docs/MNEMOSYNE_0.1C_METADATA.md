# Mnemosyne 0.1c — Phoenix-Native Memory Metadata + Provenance

Status: **started**

0.1b proved that Mnemosyne can identify itself to Phoenix without regressing the
Hindsight-compatible API. 0.1c begins the first Phoenix-native memory semantics.

## Compatibility strategy

The existing Hindsight API remains unchanged.

Phoenix-native semantics are encoded into Hindsight's existing
`metadata: dict[str, str]` field using the reserved `pv_` namespace. This
means stock Retain / Recall clients continue to work, and recalled facts can
carry Phoenix metadata without requiring a breaking request or response shape.

## Initial schema

The first schema supports:

- schema version
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
- verification state
- reversibility
- related files
- related process
- Cortex topic
- provenance

### Memory classes

Initial classes:

- conversation
- user preference
- project fact
- architecture decision
- tool result
- repair attempt
- failure
- success pattern
- protocol event
- Cortex evidence
- Watchtower context
- security event
- experiment result

### Provenance

Initial provenance fields:

- source type
- source path
- line start / end
- SHA-256
- observed timestamp
- verification command
- verification result
- tool-output hash

## Safety invariant

`authority` is deliberately restricted to:

`context_only`

A memory cannot serialize an approval, permission, or authority grant. Previous
approval remains historical context and must still pass Phoenix's live permission
and confirmation paths before an action executes.

## Implementation

`hindsight_api.phoenix_metadata.PhoenixMemoryMetadata` validates the
Phoenix-native schema and serializes it into the existing Hindsight string
metadata map.

Example output:

```json
{
  "pv_schema_version": "1",
  "pv_project": "Phoenix",
  "pv_memory_class": "repair_attempt",
  "pv_confidence": "0.92",
  "pv_authority": "context_only",
  "pv_outcome": "success",
  "pv_verification": "test_verified",
  "pv_prov_verification_command": "npm run typecheck",
  "pv_prov_verification_result": "PASS"
}
```

## 0.1c first gate

1. Unit tests for metadata normalization pass.
2. Existing 0.1 Hindsight compatibility test still passes.
3. Phoenix metadata survives a real Retain → Recall round trip in a disposable
   Mnemosyne bank.
4. No metadata value can grant execution authority.

The round-trip test is the next implementation slice.
