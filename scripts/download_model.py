#!/usr/bin/env python3
"""Download one pinned Hugging Face snapshot with bounded curl attempts."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "models/qwen3.5-4b-4bit.json").read_text())
REPO = MANIFEST["repo"]
REVISION = MANIFEST["revision"]
FILES = {f["name"]: (f["bytes"], f["sha256"]) for f in MANIFEST["files"]}
DEST = Path(os.environ.get("JEV_MODEL_DIR", str(ROOT / "model" / MANIFEST["directory"])))
STATUS = ROOT / "results" / "download_status.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_status(items, failure=None):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps({
        "repo": REPO, "revision": REVISION, "files": items,
        "failure": failure,
    }, ensure_ascii=False, indent=2) + "\n")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    items = []
    for name, (expected_size, expected_sha) in FILES.items():
        path = DEST / name
        partial = DEST / (name + ".part")
        url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{name}?download=true"
        if path.exists() and path.stat().st_size == expected_size and (
            expected_sha is None or sha256(path) == expected_sha
        ):
            items.append({"name": name, "bytes": expected_size, "status": "verified"})
            save_status(items)
            continue
        if path.exists():
            failure = {"name": name, "url": url, "reason": "existing final file did not verify"}
            save_status(items, failure)
            print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
            return 1
        for attempt in (1, 2):
            cmd = ["curl", "--fail", "--location", "--silent", "--show-error",
                   "--retry", "0", "--connect-timeout", "15",
                   "--max-time", "1800" if expected_size > 100_000_000 else "120",
                   "--speed-time", "60", "--speed-limit", "10240",
                   "--continue-at", "-", "--output", str(partial),
                   "--write-out", "%{http_code}", url]
            run = subprocess.run(cmd, text=True, capture_output=True)
            code = run.stdout.strip()[-3:]
            if run.returncode == 0:
                break
            transient = run.returncode in {6, 7, 18, 28, 35, 52, 55, 56} or code in {
                "429", "500", "502", "503", "504"
            }
            if attempt == 2 or not transient:
                failure = {"name": name, "url": url, "curl_exit": run.returncode,
                           "http_status": code, "partial_bytes": partial.stat().st_size if partial.exists() else 0,
                           "stderr_tail": run.stderr[-500:].strip(), "attempts": attempt}
                save_status(items, failure)
                print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
                return 1
            print(f"Transient transfer error for {name}; one resume attempt", flush=True)
        actual_size = partial.stat().st_size
        actual_sha = sha256(partial) if expected_sha else None
        if actual_size != expected_size or (expected_sha and actual_sha != expected_sha):
            failure = {"name": name, "url": url, "reason": "size or SHA-256 mismatch",
                       "partial_bytes": actual_size, "expected_bytes": expected_size,
                       "actual_sha256": actual_sha, "expected_sha256": expected_sha}
            save_status(items, failure)
            print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
            return 1
        partial.rename(path)
        items.append({"name": name, "bytes": actual_size, "sha256": actual_sha,
                      "status": "verified"})
        save_status(items)
        print(f"Verified {name}: {actual_size} bytes", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
