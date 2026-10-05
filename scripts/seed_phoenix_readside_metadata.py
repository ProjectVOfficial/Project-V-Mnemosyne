#!/usr/bin/env python3
"""Seed/clean a disposable Mnemosyne bank for Phoenix 0.2c read-side testing."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


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
    parser.add_argument("--bank-id", default="phoenix-mnemosyne-02c-read-test")
    parser.add_argument("--token", default="MNEMOSYNE-0.2C-READ-SIDE-TEST")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    bank_path = f"/v1/default/banks/{quote(args.bank_id, safe='')}"

    if args.cleanup:
        try:
            status, payload = http_json(args.candidate_url, "DELETE", bank_path, timeout=30.0)
            if 200 <= status < 300:
                print(f"PASS  cleanup                        HTTP {status}")
                return 0
            return fail(f"cleanup HTTP {status}: {payload}")
        except (URLError, TimeoutError, OSError) as exc:
            return fail(f"candidate unavailable: {exc}")

    print("")
    print("Mnemosyne 0.2c Phoenix read-side seed")
    print(f"Candidate : {args.candidate_url}")
    print(f"Bank      : {args.bank_id}")
    print(f"Token     : {args.token}")
    print("")

    try:
        status, identity = http_json(
            args.candidate_url, "GET", "/.well-known/project-v-mnemosyne", timeout=10.0
        )
        if status != 200:
            return fail(f"identity HTTP {status}: {identity}")
        if str(identity.get("mnemosyne_version") or "") != "0.2":
            return fail(f"Expected Mnemosyne 0.2 identity, got {identity.get('mnemosyne_version')!r}")
        print("PASS  candidate identity             Mnemosyne 0.2")

        now = datetime.now(timezone.utc).isoformat()
        metadata = {
            "pv_schema_version": "1",
            "pv_source": "react",
            "pv_workspace": "D:/PROJECTS/Phoenix-Desktop",
            "pv_project": "Phoenix",
            "pv_task_id": "mnemosyne-02c-live",
            "pv_session_id": "mnemosyne-02c-live",
            "pv_tool": "terminal",
            "pv_memory_class": "repair_attempt",
            "pv_confidence": "0.97",
            "pv_authority": "context_only",
            "pv_outcome": "success",
            "pv_verification": "test_verified",
            "pv_reversibility": "reversible",
            "pv_related_files": json.dumps(["src/main/index.ts", "src/main/mnemosyneMetadata.ts"]),
            "pv_related_process": "Phoenix Desktop",
            "pv_cortex_topic": "memory-continuity",
            "pv_prov_source_type": "tool_outcome",
            "pv_prov_source_path": "src/main/mnemosyneMetadata.ts",
            "pv_prov_observed_at": now,
            "pv_prov_verification_command": "npm run typecheck",
            "pv_prov_verification_result": "PASS",
        }

        retain_body = {
            "items": [{
                "content": (
                    f"{args.token}. Phoenix read-side validation memory. "
                    "The Mnemosyne 0.2c read-side patch passed npm run typecheck."
                ),
                "context": "Project V Mnemosyne 0.2c read-side metadata validation",
                "timestamp": now,
                "document_id": "phoenix-mnemosyne-02c-read-test",
                "metadata": metadata,
                "tags": ["phoenix", "mnemosyne", "0.2c", "read-side"],
            }],
            "async": False,
        }

        status, payload = http_json(
            args.candidate_url, "POST", f"{bank_path}/memories", retain_body, timeout=90.0
        )
        if not 200 <= status < 300:
            return fail(f"retain HTTP {status}: {payload}")
        print(f"PASS  seeded candidate bank          HTTP {status}")
        print("READY Phoenix should temporarily use:")
        print(f"      endpoint = {args.candidate_url}")
        print(f"      bank     = {args.bank_id}")
        print(f"      query    = {args.token}")
        return 0

    except (URLError, TimeoutError, OSError) as exc:
        return fail(f"candidate unavailable: {exc}")


if __name__ == "__main__":
    sys.exit(main())
