#!/usr/bin/env python3
"""Live Retain -> Recall round-trip test for Phoenix-native Mnemosyne metadata."""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from hindsight_api.phoenix_metadata import (
    PhoenixMemoryClass,
    PhoenixMemoryMetadata,
    PhoenixOutcome,
    PhoenixProvenance,
    PhoenixReversibility,
    PhoenixVerification,
)


def http_json(base_url: str, method: str, path: str, body: dict | None = None, timeout: float = 90.0):
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(base_url.rstrip("/") + path, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"detail": raw}
        return exc.code, payload


def fail(message: str) -> int:
    print(f"FAIL  {message}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-url", default="http://127.0.0.1:8889")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--keep-bank", action="store_true")
    args = parser.parse_args()

    run_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    bank_id = f"phoenix-metadata-{run_id}"
    token = f"MNEMOSYNE-METADATA-{uuid.uuid4().hex[:12].upper()}"
    document_id = f"phoenix-metadata-roundtrip-{token}"

    schema = PhoenixMemoryMetadata(
        source="react",
        workspace="D:/PROJECTS/Phoenix-Desktop",
        project="Phoenix",
        task_id=f"task-{token[-6:]}",
        session_id=f"session-{token[-6:]}",
        tool="terminal",
        memory_class=PhoenixMemoryClass.REPAIR_ATTEMPT,
        confidence=0.97,
        outcome=PhoenixOutcome.SUCCESS,
        verification=PhoenixVerification.TEST_VERIFIED,
        reversibility=PhoenixReversibility.REVERSIBLE,
        related_files=["src/main/intelligenceCore.ts", "package.json"],
        related_process="Phoenix Desktop",
        cortex_topic="memory-continuity",
        provenance=PhoenixProvenance(
            source_type="tool_outcome",
            source_path="src/main/intelligenceCore.ts",
            line_start=1,
            line_end=1,
            observed_at=datetime.now(timezone.utc).isoformat(),
            verification_command="npm run typecheck",
            verification_result="PASS",
        ),
    )
    metadata = schema.to_hindsight_metadata()

    print("")
    print("Mnemosyne 0.1c Phoenix metadata Retain -> Recall round trip")
    print(f"Candidate : {args.candidate_url}")
    print(f"Bank      : {bank_id}")
    print("")

    try:
        status, payload = http_json(args.candidate_url, "GET", "/version", timeout=min(args.timeout, 10.0))
        if status != 200:
            return fail(f"/version HTTP {status}: {payload}")
        print(f"PASS  candidate online              API {payload.get('api_version', '?')}")

        retain_body = {
            "items": [
                {
                    "content": (
                        f"Phoenix repair validation token {token}. "
                        "A TypeScript repair completed successfully and npm run typecheck verified the result."
                    ),
                    "context": "Project V Mnemosyne 0.1c Phoenix metadata round-trip validation",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "document_id": document_id,
                    "metadata": metadata,
                    "tags": ["phoenix", "mnemosyne", "metadata-roundtrip"],
                }
            ],
            "async": False,
        }

        status, payload = http_json(
            args.candidate_url,
            "POST",
            f"/v1/default/banks/{quote(bank_id, safe='')}/memories",
            retain_body,
            timeout=args.timeout,
        )
        if not 200 <= status < 300:
            return fail(f"retain HTTP {status}: {payload}")
        print(f"PASS  retain                         HTTP {status}")

        recall_body = {
            "query": f"Phoenix repair validation token {token}",
            "types": ["world", "experience", "observation"],
            "budget": "low",
            "max_tokens": 1200,
            "trace": False,
        }
        status, payload = http_json(
            args.candidate_url,
            "POST",
            f"/v1/default/banks/{quote(bank_id, safe='')}/memories/recall",
            recall_body,
            timeout=args.timeout,
        )
        if not 200 <= status < 300:
            return fail(f"recall HTTP {status}: {payload}")

        results = payload.get("results", []) if isinstance(payload, dict) else []
        matching = [
            item for item in results
            if isinstance(item, dict) and token.lower() in str(item.get("text", "")).lower()
        ]
        if not matching:
            return fail("recall returned no fact containing the unique canary")
        print("PASS  recall                         canary found")

        recalled_metadata = matching[0].get("metadata")
        if not isinstance(recalled_metadata, dict):
            return fail("recalled fact did not contain a metadata object")

        required = {
            "pv_schema_version": "1",
            "pv_source": "react",
            "pv_project": "Phoenix",
            "pv_memory_class": "repair_attempt",
            "pv_authority": "context_only",
            "pv_outcome": "success",
            "pv_verification": "test_verified",
            "pv_reversibility": "reversible",
            "pv_prov_verification_command": "npm run typecheck",
            "pv_prov_verification_result": "PASS",
        }
        mismatches = {
            key: {"expected": expected, "actual": recalled_metadata.get(key)}
            for key, expected in required.items()
            if recalled_metadata.get(key) != expected
        }
        if mismatches:
            return fail("metadata mismatch: " + json.dumps(mismatches, ensure_ascii=False))

        if recalled_metadata.get("pv_authority") != "context_only":
            return fail("recalled metadata attempted to carry execution authority")

        print("PASS  Phoenix metadata               survived Retain -> Recall")
        print("PASS  provenance                     verification evidence survived")
        print("PASS  memory authority               context_only")
        print("RESULT: PASS")
        return 0

    except (URLError, TimeoutError, OSError) as exc:
        return fail(f"candidate unavailable: {exc}")
    finally:
        if not args.keep_bank:
            try:
                status, _ = http_json(
                    args.candidate_url,
                    "DELETE",
                    f"/v1/default/banks/{quote(bank_id, safe='')}",
                    timeout=min(args.timeout, 30.0),
                )
                print(f"PASS  cleanup                        HTTP {status}" if 200 <= status < 300 else f"WARN  cleanup HTTP {status}")
            except Exception as exc:
                print(f"WARN  cleanup failed: {exc}")


if __name__ == "__main__":
    sys.exit(main())
