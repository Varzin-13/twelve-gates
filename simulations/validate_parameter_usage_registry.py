#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

path = Path(__file__).with_name("parameter_usage_registry.json")
data = json.loads(path.read_text(encoding="utf-8"))

assert data["schema"] == "twelve-gates/parameter-usage-registry/v1"
statuses = set(data["statuses"])
assert statuses == {
    "ACTIVE",
    "PARTIAL",
    "DIAGNOSTIC_ONLY",
    "INERT_MAIN_ABM",
    "INTERFACE_ONLY",
}

entries = data["entries"]
paths = [e["path"] for e in entries]
assert len(paths) == len(set(paths)), "duplicate parameter/interface path"
assert all(e["status"] in statuses for e in entries)
assert all(isinstance(e.get("evidence"), str) and e["evidence"].strip() for e in entries)

counts = Counter(e["status"] for e in entries)
assert counts["ACTIVE"] > 0
assert counts["INERT_MAIN_ABM"] > 0
assert counts["INTERFACE_ONLY"] >= 2

print("PARAMETER_USAGE_REGISTRY_PASS")
print(json.dumps(dict(sorted(counts.items())), ensure_ascii=False))
