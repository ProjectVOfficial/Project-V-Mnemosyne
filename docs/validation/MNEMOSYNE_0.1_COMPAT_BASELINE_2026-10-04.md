# Mnemosyne 0.1 — Phoenix API Compatibility Baseline Validation

Date: 2026-10-04

Status: **PASS (baseline hard gates)**

## Environment

- Stock Hindsight: `http://127.0.0.1:8888`
- Mnemosyne candidate: `http://127.0.0.1:8889`
- API version reported by both: `0.10.2`
- Ollama: `0.32.14`
- Candidate model: `qwen3:14b`
- Candidate database: isolated `pg0://project-v-mnemosyne-01`
- Test harness: `scripts/phoenix_compat_smoke.py`
- Windows wrapper: `scripts/test-phoenix-compat.ps1 -SkipReflect`

## Stock Hindsight result

- version: PASS
- retain: PASS
- bank-visible: PASS
- recall: PASS
- reflect: MODEL-LIMITED / skipped for this baseline run
- cleanup: PASS
- overall: PASS

## Mnemosyne candidate result

- version: PASS
- retain: PASS
- bank-visible: PASS
- recall: PASS
- reflect: MODEL-LIMITED / skipped for this baseline run
- cleanup: PASS
- overall: PASS

## Side-by-side parity

- stock_pass: PASS
- candidate_pass: PASS
- api_version_equal: PASS
- feature_keys_equal: PASS

## Notes

A prior live candidate run demonstrated that Mnemosyne's Reflect endpoint was reachable and eventually completed with `qwen3:14b`, although Reflect was slow and the model showed the known tool-calling limitation. Phoenix already has a Recall + local-synthesis fallback for this condition.

The official baseline parity run above intentionally skipped Reflect so the 0.1 hard compatibility gate could focus on the public API surfaces Phoenix must have for safe side-by-side operation: version/capabilities, Retain, Recall, bank visibility, and cleanup.

## Conclusion

Mnemosyne currently preserves Phoenix's required Hindsight-compatible hard-gate surface for the tested baseline. Stock Hindsight remains the production runtime and rollback path. No production `phoenix-core` migration or cutover is authorized by this result.

Next work should continue on the Mnemosyne branch while maintaining this compatibility contract.
