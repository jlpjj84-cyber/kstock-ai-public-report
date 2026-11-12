#!/usr/bin/env python3
"""Mirror ONLY already-public KStock performance reports from public Sites.

Unauthenticated HTTPS read. No access to trading/private repositories.
Any fetch, JSON validation, or leak check failure aborts deployment.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "https://kstock-ai-public-report.keenskunk257.chatgpt.site"
MAX_BYTES = 3_000_000

# Guard against accidentally publishing operational secrets and per-order data.
BLOCKED_KEYS = {
    "api_key", "app_key", "app_secret", "client_secret", "secret",
    "password", "access_token", "refresh_token", "bearer_token",
    "authorization", "private_key", "credentials", "account_number",
    "account_no", "kiwoom_app_key", "kiwoom_app_secret",
    "telegram_bot_token", "telegram_chat_id", "order_no", "order_number",
    "order_id", "raw_archive", "positions", "holdings",
}
BLOCKED_PATTERNS = (
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{15,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def get_public(name: str, retries: int = 3) -> bytes:
    if name not in ("report.txt", "report.json"):
        raise ValueError("Unknown report resource")
    url = SOURCE + "/" + name
    error = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "KStock-ReadOnly-Public-Mirror/1.0",
                              "Accept": "application/json,text/plain,*/*",
                              "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(request, timeout=25) as resp:
                if resp.status != 200:
                    raise ValueError(f"{name} HTTP {resp.status}")
                if not resp.geturl().startswith(SOURCE + "/"):
                    raise ValueError("Unexpected redirect away from public source")
                data = resp.read(MAX_BYTES + 1)
            if not data or len(data) > MAX_BYTES:
                raise ValueError("Empty or oversized report")
            return data
        except Exception as exc:
            error = exc
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Public source fetch failed for {name}: {type(error).__name__}: {error}")


def scan_keys(obj: object, prefix: str = "$") -> None:
    if isinstance(obj, dict):
        for key, val in obj.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in BLOCKED_KEYS:
                raise ValueError(f"Sensitive field blocked: {prefix}.{key}")
            scan_keys(val, f"{prefix}.{key}")
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            scan_keys(val, f"{prefix}[{i}]")


def validate(txt: bytes, js: bytes) -> tuple[str, object]:
    report = txt.decode("utf-8-sig")
    if "KStock" not in report or "자료 기준일" not in report:
        raise ValueError("Public text report missing expected markers")
    if report.lstrip().lower().startswith(("<!doctype", "<html")):
        raise ValueError("Text endpoint returned an HTML page")
    parsed = json.loads(js.decode("utf-8-sig"))
    if not isinstance(parsed, dict) or not parsed:
        raise ValueError("Public JSON endpoint is not a nonempty JSON object")
    scan_keys(parsed)
    for body in (report, json.dumps(parsed, ensure_ascii=False)):
        for p in BLOCKED_PATTERNS:
            if p.search(body):
                raise ValueError("Secret-looking material detected")
    return report, parsed


def page() -> str:
    return """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KStock AI 공개 성능 리포트 — 읽기 전용 미러</title>
<style>
:root{color-scheme:dark;font-family:system-ui,"Malgun Gothic",sans-serif;background:#0f1726;color:#e8eef9}
body{margin:0}main{max-width:950px;margin:40px auto;padding:0 20px}
h1{font-size:clamp(1.5rem,5vw,2.4rem)}p{line-height:1.65;color:#b8c8df}
a{color:#9dceff}nav{display:flex;gap:14px;flex-wrap:wrap;margin:24px 0}
nav a{border:1px solid #45607f;padding:10px 14px;border-radius:8px;text-decoration:none}
pre{background:#17243a;border:1px solid #33475f;border-radius:12px;padding:20px;
  white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;max-height:75vh;overflow:auto}
</style></head><body><main>
<h1>KStock AI 공개 성능 리포트</h1>
<p>공개 성능 요약만 제공하는 읽기 전용 GitHub Pages 미러입니다. 매매 기능이 없으며
개별 주문, 보유내역, 인증정보, 비공개 아카이브를 제공하지 않습니다.</p>
<nav><a href="./report.txt">텍스트 보고서</a><a href="./report.json">JSON 보고서</a>
<a href="https://kstock-ai-public-report.keenskunk257.chatgpt.site/">원본 공개 Sites</a></nav>
<p id="status">보고서를 불러오는 중…</p><pre id="report">로딩 중</pre>
<script>
(async()=>{
 const status=document.getElementById("status");
 const box=document.getElementById("report");
 try{
  const response=await fetch("./report.txt",{cache:"no-cache"});
  if(!response.ok)throw new Error("HTTP "+response.status);
  box.textContent=await response.text();
  status.textContent="공개 보고서 불러오기 완료";
 }catch(err){
  status.textContent="보고서 로드 실패";
  box.textContent=String(err);
 }
})();
</script></main></body></html>
"""


def main(out: Path) -> None:
    raw_text = get_public("report.txt")
    raw_json = get_public("report.json")
    text, obj = validate(raw_text, raw_json)
    # No output files exist unless BOTH public sources validate.
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.txt").write_text(text, encoding="utf-8")
    (out / "report.json").write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "index.html").write_text(page(), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Validated public mirror {datetime.now(timezone.utc).isoformat()}: "
          f"txt={len(raw_text)} bytes, json={len(raw_json)} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("site"))
    args = parser.parse_args()
    try:
        main(args.output)
    except Exception as exc:
        print(f"PUBLIC MIRROR ABORTED (no deployment): {exc}", file=sys.stderr)
        sys.exit(1)
