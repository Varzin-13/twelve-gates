"""
audit_schedule.py
=================
Research utility for inspecting coordinator/auditor schedules over Z_12.

This file does NOT recommend a constitutional rule. It exposes combinatorial
properties of the current fixed +6 rule and a broader affine design space so
coverage, repetitions, and self-audit can be measured before any normative choice.
"""
from math import gcd

N = 12
COORDINATOR_STEP = 5
UNITS_MOD_12 = tuple(a for a in range(N) if gcd(a, N) == 1)


def affine(a, b, t, n=N):
    if gcd(a, n) != 1:
        raise ValueError(f"a={a} is not a unit modulo {n}")
    return (a * t + b) % n


def coordinator(t):
    return affine(COORDINATOR_STEP, 0, t)


def cycle_with_offset(offset):
    if offset % N == 0:
        raise ValueError("offset 0 creates self-audit")
    return [
        {
            "cycle": 0,
            "period": t,
            "coordinator": coordinator(t),
            "auditor": (coordinator(t) + offset) % N,
            "offset": offset % N,
        }
        for t in range(N)
    ]


def offset_supercycle(offsets=tuple(range(1, N))):
    rows = []
    for c, offset in enumerate(offsets):
        if offset % N == 0:
            raise ValueError("offset 0 creates self-audit")
        for t in range(N):
            p = coordinator(t)
            rows.append({
                "cycle": c,
                "period": t,
                "coordinator": p,
                "auditor": (p + offset) % N,
                "offset": offset % N,
            })
    return rows


def affine_cycle(auditor_a, auditor_b):
    return [
        {
            "cycle": 0,
            "period": t,
            "coordinator": coordinator(t),
            "auditor": affine(auditor_a, auditor_b, t),
            "auditor_a": auditor_a,
            "auditor_b": auditor_b,
        }
        for t in range(N)
    ]


def all_affine_permutations():
    return [(a, b) for a in UNITS_MOD_12 for b in range(N)]


def collision_free_affine_auditors():
    out = []
    for a, b in all_affine_permutations():
        rows = affine_cycle(a, b)
        if all(r["coordinator"] != r["auditor"] for r in rows):
            out.append((a, b))
    return out


def coverage_stats(rows):
    ordered_pairs = [(r["coordinator"], r["auditor"]) for r in rows]
    unique_pairs = set(ordered_pairs)
    self_audits = sum(p == a for p, a in ordered_pairs)
    coordinator_counts = {i: 0 for i in range(N)}
    auditor_counts = {i: 0 for i in range(N)}
    for p, a in ordered_pairs:
        coordinator_counts[p] += 1
        auditor_counts[a] += 1
    return {
        "rows": len(rows),
        "unique_ordered_pairs": len(unique_pairs),
        "possible_nonself_ordered_pairs": N * (N - 1),
        "coverage_fraction": len(unique_pairs) / (N * (N - 1)),
        "self_audits": self_audits,
        "duplicate_pairs": len(ordered_pairs) - len(unique_pairs),
        "coordinator_counts": coordinator_counts,
        "auditor_counts": auditor_counts,
    }


def main():
    current = coverage_stats(cycle_with_offset(6))
    complete = coverage_stats(offset_supercycle())
    print("Current fixed +6 cycle:")
    print(current)
    print("\nComplete non-self offset benchmark (offsets 1..11):")
    print(complete)
    print(f"\nUnits mod 12: {UNITS_MOD_12}; affine permutations: {len(all_affine_permutations())}")
    print(f"Collision-free affine auditor schedules: {len(collision_free_affine_auditors())}")


if __name__ == "__main__":
    main()
