#!/usr/bin/env python3
"""Phoenix ↔ Mnemosyne 0.1 live API compatibility smoke test.

Uses disposable banks only. By default it tests one candidate endpoint. Pass
--stock-url to run the same contract against stock Hindsight and print a parity
summary.

This test intentionally exercises only the public HTTP contract Phoenix already
depends on. It does not import Hindsight/Mnemosyne internals.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


MODEL_LIMITED_PATTERNS = (
    "requires a tool-calling model",
    "produced no usable tool call",
    "tool_choice=",
)

REQUIRED_VERSION_FEATURE_KEYS = {
    "observations",
    "mcp",
    "worker",
    "bank_config_api",
    "bank_llm_health",
    "file_upload_api",
    "document_export_api",
    "document_import_api",
    "audit_log",
    "llm_trace",
    "store_document_text",
}


@dataclass
class Check:
    name: str
    status: str
    detail: str = ""


@dataclass
class TargetResult:
    label: str
    url: str
    bank_id: str
    checks: list[Check]
    api_version: str = ""
    features: dict[str, Any] | None = None

    @property
    def hard_pass(self) -> bool:
        return all(c.status in {"PASS", "MODEL-LIMITED"} for c in self.checks)


def _http_json(
    base_url: str,
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> tuple[int, Any]:
    url = base_url.rstrip("/") + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
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


def _detail(payload: Any) -> str:
    if isinstance(payload, dict):
        value = payload.get("detail") or payload.get("error") or payload.get("message")
        if value:
            return str(value)
    return json.dumps(payload, ensure_ascii=False)[:1000]


def _contains_token(payload: Any, token: str) -> bool:
    needle = token.lower()
    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and needle in str(item.get("text", "")).lower():
                    return True
    return needle in json.dumps(payload, ensure_ascii=False).lower()


def run_target(
    label: str,
    base_url: str,
    bank_id: str,
    token: str,
    *,
    timeout: float,
    skip_reflect: bool,
    keep_bank: bool,
) -> TargetResult:
    checks: list[Check] = []
    result = TargetResult(label=label, url=base_url.rstrip("/"), bank_id=bank_id, checks=checks)

    # 1. Version / features
    try:
        status, payload = _http_json(base_url, "GET", "/version", timeout=min(timeout, 10.0))
        if status != 200 or not isinstance(payload, dict):
            checks.append(Check("version", "FAIL", f"HTTP {status}: {_detail(payload)}"))
            return result
        api_version = str(payload.get("api_version") or "")
        features = payload.get("features")
        if not api_version or not isinstance(features, dict):
            checks.append(Check("version", "FAIL", "Missing api_version or features object."))
            return result
        missing = sorted(REQUIRED_VERSION_FEATURE_KEYS.difference(features.keys()))
        if missing:
            checks.append(Check("version", "FAIL", f"Missing feature keys: {', '.join(missing)}"))
            return result
        result.api_version = api_version
        result.features = features
        checks.append(Check("version", "PASS", f"api_version={api_version}"))
    except (URLError, TimeoutError, OSError) as exc:
        checks.append(Check("version", "FAIL", f"Endpoint unavailable: {exc}"))
        return result

    # 2. Retain a disposable canary.
    timestamp = datetime.now(timezone.utc).isoformat()
    retain_body = {
        "items": [
            {
                "content": f"Phoenix Mnemosyne compatibility canary {token}",
                "context": "Project V Mnemosyne 0.1 Phoenix API compatibility test",
                "timestamp": timestamp,
                "document_id": f"phoenix-mnemosyne-compat-{token}",
                "tags": ["phoenix", "mnemosyne", "compatibility-test"],
            }
        ],
        "async": False,
    }
    status, payload = _http_json(
        base_url,
        "POST",
        f"/v1/default/banks/{quote(bank_id, safe='')}/memories",
        body=retain_body,
        timeout=timeout,
    )
    if not 200 <= status < 300:
        checks.append(Check("retain", "FAIL", f"HTTP {status}: {_detail(payload)}"))
        return _cleanup_and_return(result, timeout=timeout, keep_bank=keep_bank)
    checks.append(Check("retain", "PASS", f"HTTP {status}"))

    # 3. Verify the test bank is visible.
    status, payload = _http_json(base_url, "GET", "/v1/default/banks?limit=500&offset=0", timeout=timeout)
    banks = payload.get("banks") if isinstance(payload, dict) else None
    visible = isinstance(banks, list) and any(
        isinstance(item, dict) and str(item.get("bank_id")) == bank_id for item in banks
    )
    checks.append(
        Check(
            "bank-visible",
            "PASS" if status == 200 and visible else "FAIL",
            f"HTTP {status}; bank={'present' if visible else 'missing'}",
        )
    )

    # 4. Recall must return the canary.
    recall_body = {
        "query": f"Phoenix Mnemosyne compatibility canary {token}",
        "types": ["world", "experience", "observation"],
        "budget": "low",
        "max_tokens": 800,
        "trace": False,
    }
    status, payload = _http_json(
        base_url,
        "POST",
        f"/v1/default/banks/{quote(bank_id, safe='')}/memories/recall",
        body=recall_body,
        timeout=timeout,
    )
    recalled = 200 <= status < 300 and _contains_token(payload, token)
    checks.append(
        Check(
            "recall",
            "PASS" if recalled else "FAIL",
            f"HTTP {status}; canary={'found' if recalled else 'not found'}"
            + ("" if recalled else f"; {_detail(payload)}"),
        )
    )

    # 5. Reflect is required at the API-contract level but may be model-limited.
    if skip_reflect:
        checks.append(Check("reflect", "MODEL-LIMITED", "Skipped by operator; Retain/Recall remain hard gates."))
    elif recalled:
        reflect_body = {
            "query": f"Repeat the unique validation token exactly: {token}",
            "context": f"Phoenix Mnemosyne compatibility canary {token}",
            "budget": "low",
            "max_tokens": 800,
        }
        status, payload = _http_json(
            base_url,
            "POST",
            f"/v1/default/banks/{quote(bank_id, safe='')}/reflect",
            body=reflect_body,
            timeout=max(timeout, 120.0),
        )
        text = str(payload.get("text") or "") if isinstance(payload, dict) else ""
        if 200 <= status < 300 and token.lower() in text.lower():
            checks.append(Check("reflect", "PASS", f"HTTP {status}; canary returned"))
        else:
            detail = _detail(payload)
            model_limited = any(pattern in detail.lower() for pattern in MODEL_LIMITED_PATTERNS)
            checks.append(
                Check(
                    "reflect",
                    "MODEL-LIMITED" if model_limited else "FAIL",
                    f"HTTP {status}: {detail}",
                )
            )
    else:
        checks.append(Check("reflect", "FAIL", "Recall failed; Reflect not attempted."))

    return _cleanup_and_return(result, timeout=timeout, keep_bank=keep_bank)


def _cleanup_and_return(result: TargetResult, *, timeout: float, keep_bank: bool) -> TargetResult:
    if keep_bank:
        result.checks.append(Check("cleanup", "PASS", "Skipped (--keep-bank)."))
        return result
    try:
        status, payload = _http_json(
            result.url,
            "DELETE",
            f"/v1/default/banks/{quote(result.bank_id, safe='')}",
            timeout=timeout,
        )
        result.checks.append(
            Check(
                "cleanup",
                "PASS" if 200 <= status < 300 else "FAIL",
                f"HTTP {status}" if 200 <= status < 300 else f"HTTP {status}: {_detail(payload)}",
            )
        )
    except Exception as exc:  # cleanup should be visible but never hide earlier results
        result.checks.append(Check("cleanup", "FAIL", str(exc)))
    return result


def print_result(result: TargetResult) -> None:
    print(f"\n== {result.label} ==")
    print(f"URL:  {result.url}")
    print(f"Bank: {result.bank_id}")
    for check in result.checks:
        print(f"{check.status:13} {check.name:14} {check.detail}")
    print(f"RESULT: {'PASS' if result.hard_pass else 'FAIL'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-url", default="http://127.0.0.1:8889")
    parser.add_argument("--stock-url", default="")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--skip-reflect", action="store_true")
    parser.add_argument("--keep-bank", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    run_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    token = f"MNEMOSYNE-COMPAT-{uuid.uuid4().hex[:12].upper()}"

    results: list[TargetResult] = []
    if args.stock_url:
        results.append(
            run_target(
                "stock-hindsight",
                args.stock_url,
                f"phoenix-compat-stock-{run_id}",
                token,
                timeout=args.timeout,
                skip_reflect=args.skip_reflect,
                keep_bank=args.keep_bank,
            )
        )

    results.append(
        run_target(
            "mnemosyne-candidate",
            args.candidate_url,
            f"phoenix-compat-mnemosyne-{run_id}",
            token,
            timeout=args.timeout,
            skip_reflect=args.skip_reflect,
            keep_bank=args.keep_bank,
        )
    )

    for result in results:
        print_result(result)

    parity: dict[str, Any] | None = None
    if len(results) == 2:
        stock, candidate = results
        parity = {
            "stock_pass": stock.hard_pass,
            "candidate_pass": candidate.hard_pass,
            "api_version_equal": stock.api_version == candidate.api_version,
            "feature_keys_equal": set((stock.features or {}).keys()) == set((candidate.features or {}).keys()),
        }
        print("\n== Side-by-side parity ==")
        for key, value in parity.items():
            print(f"{'PASS' if value else 'FAIL':13} {key}")

    if args.json_output:
        print(
            "\n"
            + json.dumps(
                {
                    "token": token,
                    "results": [
                        {
                            **asdict(result),
                            "hard_pass": result.hard_pass,
                        }
                        for result in results
                    ],
                    "parity": parity,
                },
                indent=2,
            )
        )

    if not all(result.hard_pass for result in results):
        return 1
    if parity and not all(parity.values()):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
