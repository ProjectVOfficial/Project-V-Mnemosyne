#!/usr/bin/env python3
"""Validate a real Phoenix Desktop write against Mnemosyne 0.2.

Phoenix must first be pointed at the candidate URL and a disposable bank, then
save a durable memory containing the unique token. This test proves that the
memory was produced by Phoenix and arrived with the pv_ metadata contract intact.
"""

from __future__ import annotations

import argparse
import json
import sys
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
    parser.add_argument("--bank-id", default="phoenix-mnemosyne-02b-test")
    parser.add_argument("--token", default="MNEMOSYNE-0.2B-PHOENIX-WRITE-TEST")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--keep-bank", action="store_true")
    args = parser.parse_args()

    print("")
    print("Mnemosyne 0.2b live Phoenix write validation")
    print(f"Candidate : {args.candidate_url}")
    print(f"Bank      : {args.bank_id}")
    print(f"Token     : {args.token}")
    print("")

    try:
        status, identity = http_json(
            args.candidate_url, "GET", "/.well-known/project-v-mnemosyne", timeout=min(args.timeout, 10.0)
        )
        if status != 200:
            return fail(f"Mnemosyne identity HTTP {status}: {identity}")
        if str(identity.get("mnemosyne_version") or "") != "0.2":
            return fail(f"Expected Mnemosyne 0.2 identity, got {identity.get('mnemosyne_version')!r}")
        print("PASS  candidate identity             Mnemosyne 0.2")

        recall_body = {
            "query": args.token,
            "types": ["world", "experience", "observation"],
            "budget": "low",
            "max_tokens": 1600,
            "trace": False,
        }
        status, payload = http_json(
            args.candidate_url,
            "POST",
            f"/v1/default/banks/{quote(args.bank_id, safe='')}/memories/recall",
            recall_body,
            timeout=args.timeout,
        )
        if not 200 <= status < 300:
            return fail(f"recall HTTP {status}: {payload}")

        results = payload.get("results", []) if isinstance(payload, dict) else []
        matches = [
            item for item in results
            if isinstance(item, dict) and args.token.lower() in str(item.get("text", "")).lower()
        ]
        if not matches:
            return fail("Phoenix write token was not recalled from the configured disposable bank.")
        print("PASS  Phoenix write recalled          canary found")

        selected = None
        for item in matches:
            md = item.get("metadata")
            if isinstance(md, dict) and md.get("pv_schema_version") == "1":
                selected = item
                break
        if selected is None:
            return fail("Canary was recalled, but no matching fact carried Phoenix pv_ metadata.")

        metadata = selected.get("metadata") or {}
        required = {
            "pv_schema_version": "1",
            "pv_authority": "context_only",
        }
        mismatches = {
            key: {"expected": expected, "actual": metadata.get(key)}
            for key, expected in required.items()
            if metadata.get(key) != expected
        }
        if mismatches:
            return fail("metadata mismatch: " + json.dumps(mismatches, ensure_ascii=False))

        if not str(metadata.get("pv_source") or "").strip():
            return fail("pv_source was not populated by Phoenix.")
        if not str(metadata.get("pv_memory_class") or "").strip():
            return fail("pv_memory_class was not populated by Phoenix.")
        if "pv_confidence" not in metadata:
            return fail("pv_confidence was not populated by Phoenix.")

        print(f"PASS  metadata schema                pv_ v{metadata.get('pv_schema_version')}")
        print(f"PASS  memory class                   {metadata.get('pv_memory_class')}")
        print(f"PASS  source                         {metadata.get('pv_source')}")
        print(f"PASS  confidence                     {metadata.get('pv_confidence')}")
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
                    f"/v1/default/banks/{quote(args.bank_id, safe='')}",
                    timeout=min(args.timeout, 30.0),
                )
                if 200 <= status < 300:
                    print(f"PASS  cleanup                        HTTP {status}")
                else:
                    print(f"WARN  cleanup                        HTTP {status}")
            except Exception as exc:
                print(f"WARN  cleanup failed: {exc}")


if __name__ == "__main__":
    sys.exit(main())
