"""
twelve_gates_model.py
======================
پیاده‌سازی کامل مدل عامل‌محور «دوازده گیت»، طبق spec دقیق ارائه‌شده توسط AI طراح
(کلاس‌ها، ۱۱ استیج، فرمول‌های چرخش و ائتلاف، PLACEHOLDERهای نهادی).
بدون وابستگی به پکیج mesa (در دسترس نبود) — منطق StagedActivation دستی پیاده شده.

برچسب طبق اصل صفر: 🔵 چشم‌انداز/طراحی → این اجرا آن را به 🟡 فرضیه ارتقا می‌دهد
(کد واقعی + اجرای واقعی)، ولی هرگز به 🟢 نمی‌رساند چون کالیبراسیون واقعی وجود ندارد.
"""
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass, field
import json

N_GATES = 12
ROTATION_STEP = 5          # gcd(5,12)=1 — بند ۴.۲ سند
OBSERVER_OFFSET = 6

# ---------------- common.py معادل ----------------

class CoordRole(Enum):
    NONE = auto(); COORDINATOR = auto(); AUDITOR = auto()

class ReportKind(Enum):
    ROUTINE = auto(); CRITICAL = auto()

class ReportStatus(Enum):
    PENDING = auto(); VERIFIED = auto(); CONTESTED = auto()

class ProposalStatus(Enum):
    DRAFT = auto(); VOTED_PASS = auto(); VOTED_FAIL = auto(); IMPLEMENTED = auto(); STALLED = auto()

class EmergencyState(Enum):
    INACTIVE = auto(); ACTIVE = auto(); EXTENSION_PENDING = auto()

class ArmedBlocPath(Enum):
    INTERNAL_SPLIT = auto(); SECURITY_BARGAIN = auto(); DIRECT_CONFRONTATION = auto(); UNDECIDED = auto()

@dataclass
class Report:
    tick: int; author_id: int; kind: ReportKind; truthful: bool
    status: ReportStatus = ReportStatus.PENDING
    verifiers: list = field(default_factory=list)
    disputers: list = field(default_factory=list)

@dataclass
class Proposal:
    tick: int; proposer_id: int; coalition_id: "int|None"
    domain_targets: list; resource_delta: dict
    status: ProposalStatus = ProposalStatus.DRAFT
    votes: dict = field(default_factory=dict)
    dissent_statements: list = field(default_factory=list)

@dataclass
class Coalition:
    coalition_id: int; members: frozenset; formed_tick: int
    dissolved_tick: "int|None" = None
    passed_decisions_streak: int = 0
    covert_exchange_exposed: bool = False


# ---------------- GateAgent ----------------

class GateAgent:
    def __init__(self, uid, model, domain, cfg, rng):
        self.uid = uid; self.model = model; self.domain = domain; self.rng = rng
        self.resource_share = cfg["resource_share"]
        self.exec_power = cfg["exec_power"]
        self.coord_role = CoordRole.NONE
        self.trust = dict(cfg["trust_row"])
        self.policy_affinity = dict(cfg["affinity_row"])
        self.coalition_id = None
        self.coalition_propensity = 0.0
        self.info_reliability = cfg["info_reliability"]
        self.audit_exposure = cfg["audit_exposure"]
        self.crisis_load = cfg["initial_crisis_load"]
        self.legitimacy_internal = cfg["legitimacy_internal"]
        self.capture_pressure = 0.0
        self.external_exposure = cfg["external_exposure"]
        self.personnel_overlap_risk = dict(cfg["overlap_row"])
        self.decision_backlog = 0
        self.memory_dependence = cfg["memory_dependence"]
        self.critical_report_threshold = cfg["critical_report_threshold"]
        self.verification_accuracy = cfg["verification_accuracy"]
        self._pending_reports = []

    def rotate_roles_stage(self):
        P, A = self.model.current_P(), self.model.current_A()
        self.coord_role = (CoordRole.COORDINATOR if self.uid == P else
                            CoordRole.AUDITOR if self.uid == A else CoordRole.NONE)
        # اثر فقط روی coord_role — exec_power/resource_share دست‌نخورده (بند ۳.۵)

    def shock_update_stage(self):
        shock = self.model.external.current_shock_for(self.uid)
        self.crisis_load = min(1.0, self.crisis_load + shock.get("crisis_delta", 0.0))
        self.external_exposure = min(1.0, self.external_exposure + shock.get("exposure_delta", 0.0))

    def local_assessment_stage(self):
        mean_trust = np.mean(list(self.trust.values())) if self.trust else 0.5
        w = self.model.cfg["coalitions"]["weights"]
        self.coalition_propensity = float(np.clip(
            0.5 * (1 - self.resource_share * 12) + 0.5 * mean_trust, 0, 1))
        cluster = self.model.cfg["coalitions"]["cartel"]["material_cluster"]
        cluster_affinity = np.mean([self.policy_affinity.get(j, 0.3) for j in cluster if j != self.uid]) if cluster else 0.3
        overlap = np.mean(list(self.personnel_overlap_risk.values())) if self.personnel_overlap_risk else 0.2
        self.capture_pressure = float(np.clip(
            0.4 * self.resource_share * 12 + 0.4 * cluster_affinity + 0.2 * overlap, 0, 1))

    def report_submission_stage(self):
        is_critical = self.crisis_load > self.critical_report_threshold
        truthful = self.rng.random() < self.info_reliability
        rep = Report(self.model.tick, self.uid,
                     ReportKind.CRITICAL if is_critical else ReportKind.ROUTINE, truthful)
        self.model.trust_ledger.record_report(rep)
        if is_critical:
            self.model.pending_critical_reports.append(rep)

    def cross_verification_stage(self):
        for rep in self.model.pending_critical_reports:
            if rep.author_id == self.uid:
                continue
            acc = self.verification_accuracy
            if self.model.current_A() == self.uid:
                acc = min(1.0, acc + 0.15)  # audit_bonus بند ۴.۱
            correct_call = self.rng.random() < acc
            believes_truthful = rep.truthful if correct_call else (not rep.truthful)
            if believes_truthful:
                rep.verifiers.append(self.uid)
            else:
                rep.disputers.append(self.uid)
            self._own_calls = getattr(self, "_own_calls", {})
            self._own_calls[id(rep)] = believes_truthful  # قضاوت خودِ این گیت، برای رفع باگ اعتماد

    def proposal_generation_stage(self):
        if self.decision_backlog > 0 or self.crisis_load > 0.5:
            cap = self.model.cfg["budget"]["annual_delta_cap"] / 52
            delta = float(np.clip(self.rng.normal(0, cap / 2), -cap, cap))
            prop = Proposal(self.model.tick, self.uid, self.coalition_id,
                             [self.uid], {self.uid: delta})
            self.model.active_proposals.append(prop)

    def coalition_negotiation_stage(self):
        w = self.model.cfg["coalitions"]["weights"]
        for other in self.model.gates:
            if other.uid == self.uid:
                continue
            complementarity = 1 - abs(self.resource_share - other.resource_share) * 6
            score = (w["w1_affinity"] * self.policy_affinity.get(other.uid, 0.3) +
                     w["w2_trust"] * self.trust.get(other.uid, 0.5) +
                     w["w3_complementarity"] * complementarity -
                     w["w4_audit_exposure"] * self.audit_exposure -
                     w["w5_overlap_penalty"] * self.personnel_overlap_risk.get(other.uid, 0.2))
            self.model.coalition_registry.propose_pair(self.uid, other.uid, score)

    def voting_stage(self):
        for prop in self.model.active_proposals:
            if prop.status != ProposalStatus.DRAFT:
                continue
            support = self.rng.random() < (0.4 + 0.4 * self.trust.get(prop.proposer_id, 0.5))
            prop.votes[self.uid] = support
            dissent = (not support) and self.rng.random() > self.audit_exposure  # اثر خاموش‌کننده ۳.۳
            if not support and self.rng.random() < (1 - self.model.cfg["trust_dynamics"]["dissent_chilling_beta"] * self.audit_exposure):
                self.model.trust_ledger.record_dissent(self.model.tick, self.uid, id(prop))

    def implementation_stage(self):
        my_props = [p for p in self.model.active_proposals if self.uid in p.resource_delta]
        for p in my_props:
            if p.status == ProposalStatus.DRAFT and len(p.votes) >= N_GATES:
                yes = sum(1 for v in p.votes.values() if v)
                p.status = ProposalStatus.VOTED_PASS if yes >= 7 else ProposalStatus.VOTED_FAIL
            if p.status == ProposalStatus.VOTED_PASS:
                self.resource_share = float(np.clip(self.resource_share + p.resource_delta.get(self.uid, 0), 0.02, 0.3))
                p.status = ProposalStatus.IMPLEMENTED
                self.decision_backlog = max(0, self.decision_backlog - 1)

    def audit_and_record_stage(self):
        if self.model.current_A() == self.uid:
            for coal in self.model.coalition_registry.active_coalitions.values():
                if self.model.current_P() in coal.members:
                    prob = self.model.cfg["trust_dynamics"]["audit_detection_prob"] * self.audit_exposure
                    if self.rng.random() < prob:
                        coal.covert_exchange_exposed = True

    def trust_legitimacy_update_stage(self):
        lr = self.model.cfg["trust_dynamics"]["trust_learning_rate"]
        own_calls = getattr(self, "_own_calls", {})
        for rep in self.model.pending_critical_reports:
            if rep.author_id == self.uid:
                continue
            my_call = own_calls.get(id(rep))
            if my_call is None:
                continue
            correct = (my_call == rep.truthful)  # آیا خودِ این گیت درست تشخیص داد؟
            delta = lr if correct else -lr
            self.trust[rep.author_id] = float(np.clip(self.trust.get(rep.author_id, 0.5) + delta, 0, 1))
        self._own_calls = {}  # پاک‌سازی برای تیک بعد
        self.legitimacy_internal = float(np.clip(np.mean(list(self.trust.values())), 0, 1)) if self.trust else self.legitimacy_internal


class BureaucracyAgent:
    def __init__(self, model, cfg):
        self.model = model
        self.institutional_memory_stock = cfg["memory_stock"]
        self.politicization_risk = cfg["politicization_risk"]
        self.service_continuity = cfg["service_continuity"]
        self.archive_integrity = cfg["archive_integrity"]
        self.geo_redundancy = cfg["geo_redundancy"]
        self.redundancy_floor = cfg["redundancy_floor"]

    def shock_update_stage(self):
        shock = self.model.external.current_shock_for(-1)
        if shock.get("disaster", False) and self.geo_redundancy < self.redundancy_floor:
            self.archive_integrity *= 0.7
            self.service_continuity *= 0.7

    def implementation_stage(self):
        pass  # ضریب تداوم در محاسبات latency مدل استفاده می‌شود

    def trust_legitimacy_update_stage(self):
        self.politicization_risk = float(np.clip(
            self.politicization_risk + 0.001 * self.institutional_memory_stock, 0, 1))


class ArmedBlocAgent:
    def __init__(self, uid, model, cfg, rng):
        self.uid = uid; self.model = model; self.rng = rng
        self.field_control = cfg["field_control"]
        self.negotiation_readiness = cfg["negotiation_readiness"]
        self.conflict_risk = cfg["conflict_risk"]
        self.external_dependency = cfg["external_dependency"]
        self.organizational_cohesion = cfg["organizational_cohesion"]
        self.path = ArmedBlocPath.UNDECIDED

    def local_assessment_stage(self):
        if self.path != ArmedBlocPath.UNDECIDED:
            return
        if self.organizational_cohesion < 0.35 and self.rng.random() < 0.3:
            self.path = ArmedBlocPath.INTERNAL_SPLIT
        elif self.conflict_risk > 0.65 and self.rng.random() < 0.3:
            self.path = ArmedBlocPath.DIRECT_CONFRONTATION
        elif self.negotiation_readiness > 0.55 and self.rng.random() < 0.25:
            self.path = ArmedBlocPath.SECURITY_BARGAIN


class CivilSocietyAgent:
    def __init__(self, model, cfg):
        self.model = model
        self.mobilization_capacity = cfg["mobilization_capacity"]
        self.oversight_strength = cfg["oversight_strength"]
        self.media_visibility = cfg["media_visibility"]
        self.union_density_proxy = cfg["union_density_proxy"]
        self.public_legitimacy_signal = cfg["public_legitimacy_signal"]

    def trust_legitimacy_update_stage(self):
        mean_leg = np.mean([g.legitimacy_internal for g in self.model.gates])
        self.public_legitimacy_signal = float(np.clip(
            0.7 * self.public_legitimacy_signal + 0.3 * mean_leg, 0, 1))


# ---------------- Subsystems ----------------

class Mirror13Subsystem:
    def __init__(self, enabled, coordination_gain):
        self.enabled = enabled; self.coordination_gain = coordination_gain
    def coordination_friction(self):
        return 0.2 if self.enabled else 0.2 + (1 - self.coordination_gain)
    def informal_power_index(self):
        return self.coordination_gain * 0.3 if self.enabled else 0.0


class GateZeroProcess:
    def __init__(self, cfg):
        self.cfg = cfg
        self.appeal_log = []
    def entropy_source_manipulability(self):
        return self.cfg["entropy_manipulability"]  # metric، نه راه‌حل (بند ۳.۱)


class EmergencyCourtProcess:
    def __init__(self, cfg):
        self.independence = 1.0 if cfg["independence_mode"] == "ideal" else 1.0
        self.mode = cfg["independence_mode"]; self.erosion_rate = cfg["erosion_rate"]
    def approve_extension(self, consecutive_extensions, rng):
        if self.mode == "erodible":
            self.independence = max(0.1, self.independence - self.erosion_rate)
        return rng.random() < self.independence


class TrustLedger:
    def __init__(self):
        self.reports = []; self.dissents = []
    def record_report(self, rep): self.reports.append(rep)
    def record_dissent(self, tick, agent_id, proposal_ref): self.dissents.append((tick, agent_id))
    def integrity(self): return 0.95  # اثرپذیر از bureaucracy.archive_integrity در نسخه‌ی کامل‌تر


class CoalitionRegistry:
    def __init__(self, cfg):
        self.cfg = cfg; self.pair_scores = {}; self.active_coalitions = {}; self._next_id = 0
        self._history = []

    def propose_pair(self, i, j, score):
        self.pair_scores[frozenset((i, j))] = score

    def form_coalitions(self, tick):
        theta = self.cfg["theta_pair"]
        strong_pairs = [k for k, v in self.pair_scores.items() if v > theta]
        # ادغام ساده‌ی جفت‌های هم‌پوشان به ائتلاف‌های بزرگ‌تر (union-find ساده)
        parent = {}
        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                x = parent[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
        for pair in strong_pairs:
            a, b = tuple(pair)
            union(a, b)
        groups = {}
        for node in parent:
            groups.setdefault(find(node), set()).add(node)
        for members in groups.values():
            if len(members) < 2:
                continue
            key = frozenset(members)
            if key not in self.active_coalitions:
                self.active_coalitions[key] = Coalition(self._next_id, key, tick)
                self._next_id += 1

    def dissolve_check(self, tick, gates_by_id):
        floor = self.cfg["trust_dissolve_floor"]
        to_drop = []
        for key, coal in self.active_coalitions.items():
            mean_trust = np.mean([gates_by_id[i].trust.get(j, 0.5)
                                   for i in coal.members for j in coal.members if i != j] or [0.5])
            if mean_trust < floor or coal.covert_exchange_exposed:
                coal.dissolved_tick = tick
                to_drop.append(key)
            else:
                coal.passed_decisions_streak += 1
        for k in to_drop:
            self._history.append(self.active_coalitions.pop(k))

    def cartel_active(self, gates_by_id):
        cart = self.cfg["cartel"]
        for coal in self.active_coalitions.values():
            if coal.passed_decisions_streak < cart["K_min_duration_ticks"]:
                continue
            power_sum = sum(gates_by_id[i].exec_power for i in coal.members)
            has_cluster = any(i in cart["material_cluster"] for i in coal.members)
            if power_sum > cart["theta_power_sum"] and has_cluster and not coal.covert_exchange_exposed:
                return True
        return False

    def n_active(self): return len(self.active_coalitions)
    def mean_duration(self):
        durs = [ (c.dissolved_tick or 0) - c.formed_tick for c in self._history ]
        return float(np.mean(durs)) if durs else 0.0


class ExternalScenarioDriver:
    def __init__(self, timeline):
        self.timeline = {ev["tick"]: ev for ev in timeline}
    def current_shock_for(self, gate_id):
        return {}  # baseline: بدون شوک (طبق کانفیگ داده‌شده)
    def apply(self, tick):
        pass


# ---------------- مدل اصلی ----------------

STAGES = ["rotate_roles_stage", "shock_update_stage", "local_assessment_stage",
          "report_submission_stage", "cross_verification_stage",
          "proposal_generation_stage", "coalition_negotiation_stage",
          "voting_stage", "implementation_stage", "audit_and_record_stage",
          "trust_legitimacy_update_stage"]


class PreconditionError(Exception): pass


class TwelveGatesModel:
    def __init__(self, cfg, seed=None):
        self.cfg = cfg
        self.rng = np.random.default_rng(seed)
        self._validate_preconditions()
        self.tick = 0
        self.trust_ledger = TrustLedger()
        self.mirror13 = Mirror13Subsystem(cfg["mirror13"]["enabled"], cfg["mirror13"]["coordination_gain"])
        self.gate_zero = GateZeroProcess(cfg["gate_zero"])
        self.emergency_court = EmergencyCourtProcess(cfg["emergency_court"])
        self.coalition_registry = CoalitionRegistry(cfg["coalitions"])
        self.external = ExternalScenarioDriver(cfg["external_timeline"])
        self.emergency_state = EmergencyState.INACTIVE
        self.emergency_ticks_remaining = 0
        self.emergency_total_ticks = 0
        self.active_proposals = []
        self.pending_critical_reports = []
        self._build_agents()

    def _validate_preconditions(self):
        cap = self.cfg["preconditions"]["coordination_capacity"]
        mn = self.cfg["preconditions"]["min_coordination_capacity"]
        if cap < mn:
            raise PreconditionError(
                f"مدل برای پس از توافق اولیه معتبر است (بند ۱۰.۶.۷)؛ "
                f"coordination_capacity={cap} < min={mn}")

    def _build_agents(self):
        self.gates = []
        self.gates_by_id = {}
        for g in self.cfg["gates"]:
            ga = GateAgent(g["gate_id"], self, g["domain"], g, self.rng)
            self.gates.append(ga); self.gates_by_id[g["gate_id"]] = ga
        self.bureaucracy = BureaucracyAgent(self, self.cfg["bureaucracy"])
        self.armed_blocs = [ArmedBlocAgent(i, self, b, self.rng)
                             for i, b in enumerate(self.cfg.get("armed_blocs", []))]
        self.civil_society = CivilSocietyAgent(self, self.cfg["civil_society"])

    def rotation_index(self):
        return self.tick // self.cfg["time"]["rotation_period_ticks"]
    def current_P(self):
        return (ROTATION_STEP * self.rotation_index()) % N_GATES
    def current_A(self):
        return (self.current_P() + OBSERVER_OFFSET) % N_GATES

    def process_emergency(self):
        requesters = [g for g in self.gates if g.crisis_load > 0.75]
        if self.emergency_state == EmergencyState.INACTIVE and requesters:
            self.emergency_state = EmergencyState.ACTIVE
            self.emergency_ticks_remaining = self.cfg["time"]["emergency_fuse_ticks"]
        elif self.emergency_state == EmergencyState.ACTIVE:
            self.emergency_ticks_remaining -= 1
            self.emergency_total_ticks += 1
            if self.emergency_ticks_remaining <= 0:
                still_crisis = any(g.crisis_load > 0.6 for g in self.gates)
                if still_crisis:
                    non_involved_yes = self.rng.random() < 0.55  # سناریویی: نرخ رأی موافق تمدید
                    court_ok = self.emergency_court.approve_extension(1, self.rng)
                    if non_involved_yes and court_ok:
                        self.emergency_ticks_remaining = self.cfg["time"]["emergency_fuse_ticks"]
                    else:
                        self.emergency_state = EmergencyState.INACTIVE
                else:
                    self.emergency_state = EmergencyState.INACTIVE

    def step(self):
        self.external.apply(self.tick)
        self.pending_critical_reports = []
        self.active_proposals = [p for p in self.active_proposals if p.status == ProposalStatus.DRAFT]
        for stage in STAGES:
            for g in self.gates:
                getattr(g, stage)()
            if hasattr(self.bureaucracy, stage):
                getattr(self.bureaucracy, stage)()
            if hasattr(self.civil_society, stage):
                getattr(self.civil_society, stage)()
            for ab in self.armed_blocs:
                if hasattr(ab, stage):
                    getattr(ab, stage)()
        self.process_emergency()
        for rep in self.pending_critical_reports:
            rep.status = ReportStatus.VERIFIED if len(rep.verifiers) >= 2 else ReportStatus.CONTESTED
        self.coalition_registry.form_coalitions(self.tick)
        self.coalition_registry.dissolve_check(self.tick, self.gates_by_id)
        self.tick += 1

    def cartel_capture_active(self):
        return self.coalition_registry.cartel_active(self.gates_by_id)

    def run(self, max_ticks):
        cartel_ever = False
        for _ in range(max_ticks):
            self.step()
            if self.cartel_capture_active():
                cartel_ever = True
        return {
            "cartel_capture_ever": cartel_ever,
            "emergency_time_share": self.emergency_total_ticks / max(self.tick, 1),
            "n_active_coalitions_end": self.coalition_registry.n_active(),
            "coalition_mean_duration": self.coalition_registry.mean_duration(),
            "mean_legitimacy_end": float(np.mean([g.legitimacy_internal for g in self.gates])),
            "mean_capture_pressure_end": float(np.mean([g.capture_pressure for g in self.gates])),
            "bureaucracy_politicization_end": self.bureaucracy.politicization_risk,
            "public_legitimacy_signal_end": self.civil_society.public_legitimacy_signal,
        }
