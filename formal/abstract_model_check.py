#!/usr/bin/env python3
"""Finite-state checks for software/logical invariants only.

This is not evidence of political effectiveness, legitimacy, or real-world stability.
"""
from collections import deque

N = 12
STEP = 5
OFFSET = 6


def check_rotation():
    rows = [((STEP * t) % N, ((STEP * t) + OFFSET) % N) for t in range(N)]
    assert len({p for p, _ in rows}) == N
    assert all(p != a for p, a in rows)
    return {"periods": len(rows), "coordinator_coverage": N, "self_audits": 0}


def check_emergency():
    # state = (active, ticks_remaining, extension_count)
    start = (False, 0, 0)
    q = deque([start])
    seen = {start}
    edges = 0
    while q:
        active, rem, ext = q.popleft()
        nxt = set()
        if not active:
            nxt |= {(False, 0, ext), (True, 2, 0)}
        elif rem > 1:
            nxt.add((True, rem - 1, ext))
        else:
            # At expiry the system either deactivates or records a new extension.
            nxt |= {(False, 0, ext), (True, 2, min(ext + 1, 3))}
        for state in nxt:
            edges += 1
            if state not in seen:
                seen.add(state)
                q.append(state)
    assert all((not a) or r > 0 for a, r, _ in seen)
    return {"reachable_states": len(seen), "edges_checked": edges}


def check_budget(depth=2, total=120):
    # integerized shares; move one unit from one gate to another.
    start = (10,) * N
    frontier = {start}
    seen = {start}
    transitions = 0
    for _ in range(depth):
        new = set()
        for state in frontier:
            assert sum(state) == total
            assert all(x >= 0 for x in state)
            for i in range(N):
                if state[i] == 0:
                    continue
                for j in range(N):
                    if i == j:
                        continue
                    s = list(state)
                    s[i] -= 1
                    s[j] += 1
                    ns = tuple(s)
                    transitions += 1
                    assert sum(ns) == total
                    assert all(x >= 0 for x in ns)
                    if ns not in seen:
                        seen.add(ns)
                        new.add(ns)
        frontier = new
    return {
        "depth": depth,
        "reachable_states": len(seen),
        "transitions_checked": transitions,
        "resource_total": total,
    }


def check_gate_zero_case_lifecycle():
    edges = {
        "submitted": {"scope_checked"},
        "scope_checked": {"out_of_scope", "evidence_checked"},
        "out_of_scope": set(),
        "evidence_checked": {"approved", "rejected"},
        "approved": set(),
        "rejected": {"appeal_pending"},
        "appeal_pending": {"upheld", "reversed"},
        "upheld": set(),
        "reversed": set(),
    }
    terminal = {"out_of_scope", "approved", "upheld", "reversed"}
    for state, nxt in edges.items():
        if not nxt:
            assert state in terminal
    # All nonterminal states can reach a terminal state.
    def reaches_terminal(start):
        stack=[start]; seen=set()
        while stack:
            x=stack.pop()
            if x in terminal:
                return True
            if x in seen:
                continue
            seen.add(x)
            stack.extend(edges[x])
        return False
    assert all(reaches_terminal(s) for s in edges)
    return {
        "states": len(edges),
        "edges_checked": sum(len(v) for v in edges.values()),
        "terminal_states": sorted(terminal),
    }


def main():
    report = {
        "claim_boundary": "software/logical finite-state checks only",
        "rotation": check_rotation(),
        "emergency": check_emergency(),
        "budget": check_budget(),
        "gate_zero_case_lifecycle": check_gate_zero_case_lifecycle(),
    }
    print(report)


if __name__ == "__main__":
    main()
