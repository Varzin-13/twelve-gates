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


def reciprocal_dyads(rows):
    pairs = {(r["coordinator"], r["auditor"]) for r in rows}
    return len({
        frozenset((i, j))
        for i, j in pairs
        if (j, i) in pairs
    })


def collision_free_affine_catalog():
    catalog = []
    for a, b in collision_free_affine_auditors():
        rows = affine_cycle(a, b)
        catalog.append({
            "a": a,
            "b": b,
            "pairs": frozenset((r["coordinator"], r["auditor"]) for r in rows),
            "reciprocal_dyads": reciprocal_dyads(rows),
        })
    return catalog


def minimum_reciprocal_exact_cover():
    """Exhaustively search the collision-free affine family.

    Finds an exact cover of all 132 non-self ordered pairs using 11 affine
    schedules while minimizing the total number of within-cycle reciprocal
    dyads. The result is explicitly limited to this finite affine family.
    """
    universe = frozenset(
        (i, j) for i in range(N) for j in range(N) if i != j
    )
    catalog = collision_free_affine_catalog()
    pair_to_candidates = {p: [] for p in universe}
    for idx, item in enumerate(catalog):
        for pair in item["pairs"]:
            pair_to_candidates[pair].append(idx)

    best_cost = float("inf")
    best = None

    def search(covered, chosen, cost):
        nonlocal best_cost, best
        if cost >= best_cost:
            return
        if covered == universe:
            if len(chosen) == N - 1:
                best_cost = cost
                best = list(chosen)
            return
        if len(chosen) >= N - 1:
            return
        remaining = len(universe - covered)
        if remaining > (N - 1 - len(chosen)) * N:
            return

        uncovered = universe - covered
        target = min(
            uncovered,
            key=lambda p: sum(
                1 for idx in pair_to_candidates[p]
                if catalog[idx]["pairs"].isdisjoint(covered)
            ),
        )
        options = [
            idx for idx in pair_to_candidates[target]
            if catalog[idx]["pairs"].isdisjoint(covered)
        ]
        options.sort(key=lambda idx: catalog[idx]["reciprocal_dyads"])
        for idx in options:
            item = catalog[idx]
            search(
                covered | item["pairs"],
                chosen + [idx],
                cost + item["reciprocal_dyads"],
            )

    search(frozenset(), [], 0)
    solution = [] if best is None else [
        {
            "a": catalog[idx]["a"],
            "b": catalog[idx]["b"],
            "reciprocal_dyads": catalog[idx]["reciprocal_dyads"],
        }
        for idx in best
    ]
    return {
        "family": "collision-free Aff(Z12)",
        "exact_cover_cycles": N - 1,
        "minimum_total_reciprocal_dyads": None if best is None else int(best_cost),
        "solution": solution,
    }


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
        "reciprocal_dyads": reciprocal_dyads(rows),
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
    catalog = collision_free_affine_catalog()
    reciprocal_free = sum(1 for item in catalog if item["reciprocal_dyads"] == 0)
    print(f"\nUnits mod 12: {UNITS_MOD_12}; affine permutations: {len(all_affine_permutations())}")
    print(f"Collision-free affine auditor schedules: {len(catalog)}")
    print(f"Collision-free AND reciprocal-free affine schedules: {reciprocal_free}")
    print("Affine exact-cover reciprocal lower bound:")
    print(minimum_reciprocal_exact_cover())


if __name__ == "__main__":
    main()
