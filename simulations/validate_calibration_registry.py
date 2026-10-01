#!/usr/bin/env python3
import json
from pathlib import Path

path = Path(__file__).with_name("calibration_registry.json")
data = json.loads(path.read_text(encoding="utf-8"))

assert data["schema"] == "twelve-gates/calibration-registry/v1"
params = data["parameters"]
assert len(params) == 21
ids = [p["id"] for p in params]
assert len(ids) == len(set(ids))
assert all(p["label"] in {"DOCUMENT","DESIGN","EMPIRICAL","ARBITRARY"} for p in params)

for p in params:
    for key in ("id","label","value","source","empirical_accepted",
                "empirical_source","mapping_method","uncertainty"):
        assert key in p, (p.get("id"), key)
    if p["empirical_accepted"]:
        assert p["label"] == "EMPIRICAL"
        assert p["empirical_source"]
        assert p["mapping_method"]
        assert p["uncertainty"] is not None

accepted = sum(bool(p["empirical_accepted"]) for p in params)
print(f"CALIBRATION_REGISTRY_PASS parameters={len(params)} accepted={accepted}")
if accepted == 0:
    print("No empirical calibration mapping is accepted yet; this is intentional.")
