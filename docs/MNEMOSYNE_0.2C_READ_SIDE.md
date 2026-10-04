# Mnemosyne 0.2c — Phoenix Read-Side Metadata Integration

Status: **started**

0.2a proved Phoenix compiles with Phoenix-native write metadata.
0.2b proved a real Phoenix durable-memory write reaches Mnemosyne with the
`pv_` schema intact.

0.2c makes recalled Mnemosyne/Hindsight facts metadata-aware inside Phoenix.

## Phoenix behavior

The Phoenix-side patch:

- parses `pv_` metadata when present;
- preserves the raw recalled metadata alongside a parsed Phoenix view;
- surfaces memory class, project, tool, outcome, verification, confidence and
  provenance in Phoenix's synthesized memory context;
- leaves older Hindsight memories with no `pv_` metadata fully compatible;
- never turns recalled metadata into permission.

## Authority invariant

The recall parser returns:

`authority = context_only`

regardless of any stored claim.

If a stored memory contains an unexpected `pv_authority` value, Phoenix marks
the claim invalid and still treats the memory only as context.

## 0.2c gates

1. Phoenix `npm run typecheck` passes.
2. Mnemosyne 0.2 candidate is reachable.
3. A Phoenix-authored structured memory is recalled through Phoenix.
4. Phoenix's returned `hindsightResults` preserves raw metadata and a parsed
   `phoenixMetadata` view.
5. Memory context includes useful metadata/provenance labels.
6. Recalled authority remains `context_only`.
7. Legacy Hindsight recall remains compatible.

No endpoint switch or production cutover is authorized by this phase.
