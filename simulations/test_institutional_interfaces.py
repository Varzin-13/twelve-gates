#!/usr/bin/env python3
from institutional_interfaces import (
    GateZeroInterface,
    GateZeroState,
    InvalidTransition,
    Mirror13Interface,
    NegativeCompetenceError,
)

PASS = []
FAIL = []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"{'✅' if cond else '❌'} {name}")


def test_gate_zero_out_of_scope_terminal():
    gz = GateZeroInterface({"criterion_a"})
    gz.submit("c1", "unknown")
    gz.check_scope("c1")
    case = gz.route_scope("c1")
    check("Gate Zero: criterion خارج از frozen set باید OUT_OF_SCOPE شود",
          case.state == GateZeroState.OUT_OF_SCOPE and gz.is_terminal("c1"))


def test_gate_zero_rejection_appeal():
    gz = GateZeroInterface({"criterion_a"})
    gz.submit("c2", "criterion_a")
    gz.check_scope("c2")
    gz.route_scope("c2")
    case = gz.decide("c2", approved=False)
    check("Gate Zero: رد اولیه نباید terminal باشد",
          case.state == GateZeroState.REJECTED and not gz.is_terminal("c2"))
    gz.appeal("c2")
    case = gz.resolve_appeal("c2", reverse=True)
    check("Gate Zero: appeal باید به terminal روشن برسد",
          case.state == GateZeroState.REVERSED and gz.is_terminal("c2"))


def test_gate_zero_invalid_transition_refused():
    gz = GateZeroInterface({"criterion_a"})
    gz.submit("c3", "criterion_a")
    refused = False
    try:
        gz.appeal("c3")
    except InvalidTransition:
        refused = True
    check("Gate Zero: transition نامعتبر باید صریحاً رد شود", refused)


def test_mirror13_negative_competence():
    m = Mirror13Interface()
    allowed = m.request_action("coordinate", {"case": "x"})
    check("Mirror-13: action هماهنگی مجاز باید log شود",
          allowed["action"] == "coordinate" and len(m.action_log) == 1)

    forbidden = False
    try:
        m.request_action("allocate_budget", {"amount": 1})
    except NegativeCompetenceError:
        forbidden = True
    check("Mirror-13: تخصیص بودجه باید توسط interface ممنوع شود", forbidden)

    unknown = False
    try:
        m.request_action("invent_new_power")
    except NegativeCompetenceError:
        unknown = True
    check("Mirror-13: اختیار خارج از frozen interface باید ممنوع شود", unknown)


if __name__ == "__main__":
    test_gate_zero_out_of_scope_terminal()
    test_gate_zero_rejection_appeal()
    test_gate_zero_invalid_transition_refused()
    test_mirror13_negative_competence()

    print(f"\n{len(PASS)} موفق، {len(FAIL)} ناموفق از {len(PASS)+len(FAIL)} تست interface")
    if FAIL:
        for name in FAIL:
            print(" -", name)
        raise SystemExit(1)
