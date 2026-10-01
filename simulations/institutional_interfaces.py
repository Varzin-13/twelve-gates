"""
institutional_interfaces.py
===========================
Executable interface contracts for institutional components that should not be
given invented behavioral probabilities merely to make the ABM look complete.

These classes enforce state transitions and negative competence only.
They do not establish legitimacy, effectiveness, or real-world compliance.
"""
from dataclasses import dataclass, field
from enum import Enum


class InvalidTransition(RuntimeError):
    pass


class NegativeCompetenceError(PermissionError):
    pass


class GateZeroState(str, Enum):
    SUBMITTED = "submitted"
    SCOPE_CHECKED = "scope_checked"
    OUT_OF_SCOPE = "out_of_scope"
    EVIDENCE_CHECKED = "evidence_checked"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPEAL_PENDING = "appeal_pending"
    UPHELD = "upheld"
    REVERSED = "reversed"


GATE_ZERO_TERMINAL = {
    GateZeroState.OUT_OF_SCOPE,
    GateZeroState.APPROVED,
    GateZeroState.UPHELD,
    GateZeroState.REVERSED,
}


@dataclass
class GateZeroCase:
    case_id: str
    criterion: str
    state: GateZeroState = GateZeroState.SUBMITTED
    history: list = field(default_factory=lambda: [GateZeroState.SUBMITTED.value])


class GateZeroInterface:
    """Bounded-competence case lifecycle.

    The caller supplies the frozen allowed-criteria set. This module deliberately
    does not decide which criteria are normatively legitimate.
    """

    def __init__(self, allowed_criteria):
        self.allowed_criteria = frozenset(allowed_criteria)
        self.cases = {}

    def submit(self, case_id, criterion):
        if case_id in self.cases:
            raise ValueError(f"duplicate case_id: {case_id}")
        case = GateZeroCase(str(case_id), str(criterion))
        self.cases[case.case_id] = case
        return case

    def _case(self, case_id):
        try:
            return self.cases[str(case_id)]
        except KeyError as exc:
            raise KeyError(f"unknown case_id: {case_id}") from exc

    @staticmethod
    def _advance(case, expected, new_state):
        if case.state != expected:
            raise InvalidTransition(
                f"{case.case_id}: expected {expected.value}, found {case.state.value}"
            )
        case.state = new_state
        case.history.append(new_state.value)
        return case

    def check_scope(self, case_id):
        case = self._case(case_id)
        return self._advance(case, GateZeroState.SUBMITTED, GateZeroState.SCOPE_CHECKED)

    def route_scope(self, case_id):
        case = self._case(case_id)
        if case.state != GateZeroState.SCOPE_CHECKED:
            raise InvalidTransition(
                f"{case.case_id}: route_scope requires scope_checked"
            )
        target = (
            GateZeroState.EVIDENCE_CHECKED
            if case.criterion in self.allowed_criteria
            else GateZeroState.OUT_OF_SCOPE
        )
        case.state = target
        case.history.append(target.value)
        return case

    def decide(self, case_id, approved):
        case = self._case(case_id)
        target = GateZeroState.APPROVED if bool(approved) else GateZeroState.REJECTED
        return self._advance(case, GateZeroState.EVIDENCE_CHECKED, target)

    def appeal(self, case_id):
        case = self._case(case_id)
        return self._advance(case, GateZeroState.REJECTED, GateZeroState.APPEAL_PENDING)

    def resolve_appeal(self, case_id, reverse):
        case = self._case(case_id)
        target = GateZeroState.REVERSED if bool(reverse) else GateZeroState.UPHELD
        return self._advance(case, GateZeroState.APPEAL_PENDING, target)

    def is_terminal(self, case_id):
        return self._case(case_id).state in GATE_ZERO_TERMINAL


class Mirror13Interface:
    """Negative-competence contract for a coordination/review function."""

    ALLOWED_ACTIONS = frozenset({
        "receive_items",
        "construct_allowed_agenda",
        "coordinate",
        "recommend",
        "log_response",
    })

    FORBIDDEN_BINDING_ACTIONS = frozenset({
        "allocate_budget",
        "bind_law",
        "appoint_official",
        "change_gate_resource",
        "extend_own_term",
    })

    def __init__(self):
        self.action_log = []

    def request_action(self, action, payload=None):
        action = str(action)
        if action in self.FORBIDDEN_BINDING_ACTIONS:
            raise NegativeCompetenceError(
                f"Mirror-13 negative competence forbids action: {action}"
            )
        if action not in self.ALLOWED_ACTIONS:
            raise NegativeCompetenceError(
                f"Mirror-13 action is outside the frozen interface: {action}"
            )
        event = {"action": action, "payload": payload}
        self.action_log.append(event)
        return event
