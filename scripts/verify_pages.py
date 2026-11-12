#!/usr/bin/env python3
"""Check externally served GitHub Pages URLs after deployment (no credentials)."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ["PAGES_URL"].rstrip("/")
EXPECTED_HOST = "jlpjj84-cyber.github.io"


def fetch_url(url: str) -> bytes:
    last_error = None
    for attempt in range(12):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "KStockPublicPagesPostDeployVerifier/1.0",
                         "Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status != 200:
                    raise ValueError(f"HTTP {response.status}")
                if len(response.read(0)) != 0:
                    raise ValueError("Unexpected read failure")
                data = response.read(3_000_001)
                if not data or len(data) > 3_000_000:
                    raise ValueError("Empty or excessive response size")
                return data
        except (urllib.error.URLError, ValueError, OSError) as exc:
            last_error = exc
            if attempt < 11:
                time.sleep(5)
    raise RuntimeError(f"Public GET failed for {url}: {last_error}")


def main() -> None:
    if not BASE.startswith(f"https://{EXPECTED_HOST}/kstock-ai-public-report"):
        raise ValueError(f"Unexpected GitHub Pages deployment URL: {BASE}")
    site = Path("_site")
    for name in ("", "report.txt", "report.json"):
        url = f"{BASE}/{name}" if name else f"{BASE}/"
        data = fetch_url(url)
        if name == "report.json":
            doc = json.loads(data.decode("utf-8-sig"))
            expected = json.loads((site / "report.json").read_text("utf-8"))
            if doc != expected:
                raise ValueError("Published JSON differs from validated deployment artifact")
        elif name == "report.txt":
            expected = (site / "report.txt").read_text(encoding="utf-8")
            if data.decode("utf-8-sig") != expected:
                raise ValueError("Published text differs from validated deployment artifact")
        elif b"KStock AI" not in data:
            raise ValueError("Missing KStock title in published HTML")
        print(f"EXTERNAL HTTP 200 {url} ({len(data)} bytes)")
    print("GitHub Pages external GET: all three URLs verified.")


if __name__ == "__main__":
    main()
