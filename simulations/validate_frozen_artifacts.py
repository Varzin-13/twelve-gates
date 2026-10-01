#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
manifest_path = root / "simulations" / "results" / "FROZEN_ARTIFACT_MANIFEST.json"
data = json.loads(manifest_path.read_text(encoding="utf-8"))

assert data["schema"] == "twelve-gates/frozen-artifact-manifest/v1"
items = data["artifacts"]
paths = [x["path"] for x in items]
assert len(paths) == len(set(paths)), "duplicate frozen artifact path"

failures = []
for item in items:
    path = root / item["path"]
    if not path.exists():
        failures.append(f"MISSING {item['path']}")
        continue
    actual = subprocess.check_output(
        ["git", "hash-object", str(path)],
        cwd=root,
        text=True,
    ).strip()
    expected = item["git_blob_sha"]
    if actual != expected:
        failures.append(
            f"HASH_MISMATCH {item['path']} expected={expected} actual={actual}"
        )

if failures:
    print("FROZEN_ARTIFACT_MANIFEST_FAIL")
    for failure in failures:
        print(failure)
    raise SystemExit(1)

print(f"FROZEN_ARTIFACT_MANIFEST_PASS artifacts={len(items)}")
