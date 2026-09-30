--------------------------- MODULE TwelveGates ---------------------------
EXTENDS Naturals, Integers, FiniteSets

CONSTANTS Gates
ASSUME Gates = 0..11

VARIABLES t, emergency, expiry, extensionCount, resources, gzState

vars == <<t, emergency, expiry, extensionCount, resources, gzState>>

Coordinator == (5 * t) % 12
Auditor == (Coordinator + 6) % 12

TypeOK ==
  /\ t \in Nat
  /\ emergency \in BOOLEAN
  /\ expiry \in Nat
  /\ extensionCount \in Nat
  /\ resources \in [Gates -> Nat]
  /\ gzState \in {"submitted","scope_checked","out_of_scope","evidence_checked",
                    "approved","rejected","appeal_pending","upheld","reversed"}

NoSelfAudit == Coordinator # Auditor
ResourceConservation == Sum({resources[g] : g \in Gates}) = 120
EmergencyHasExpiry == emergency => expiry > 0

Init ==
  /\ t = 0
  /\ emergency = FALSE
  /\ expiry = 0
  /\ extensionCount = 0
  /\ resources = [g \in Gates |-> 10]
  /\ gzState = "submitted"

Tick ==
  /\ t' = t + 1
  /\ UNCHANGED <<emergency, expiry, extensionCount, resources, gzState>>

ActivateEmergency ==
  /\ ~emergency
  /\ emergency' = TRUE
  /\ expiry' = 2
  /\ extensionCount' = 0
  /\ UNCHANGED <<t, resources, gzState>>

EmergencyStep ==
  /\ emergency
  /\ expiry > 1
  /\ expiry' = expiry - 1
  /\ UNCHANGED <<t, emergency, extensionCount, resources, gzState>>

ExpireEmergency ==
  /\ emergency
  /\ expiry = 1
  /\ emergency' = FALSE
  /\ expiry' = 0
  /\ UNCHANGED <<t, extensionCount, resources, gzState>>

ExtendEmergency ==
  /\ emergency
  /\ expiry = 1
  /\ emergency' = TRUE
  /\ expiry' = 2
  /\ extensionCount' = extensionCount + 1
  /\ UNCHANGED <<t, resources, gzState>>

GateZeroStep ==
  \/ /\ gzState = "submitted"
     /\ gzState' = "scope_checked"
     /\ UNCHANGED <<t, emergency, expiry, extensionCount, resources>>
  \/ /\ gzState = "scope_checked"
     /\ gzState' \in {"out_of_scope","evidence_checked"}
     /\ UNCHANGED <<t, emergency, expiry, extensionCount, resources>>
  \/ /\ gzState = "evidence_checked"
     /\ gzState' \in {"approved","rejected"}
     /\ UNCHANGED <<t, emergency, expiry, extensionCount, resources>>
  \/ /\ gzState = "rejected"
     /\ gzState' = "appeal_pending"
     /\ UNCHANGED <<t, emergency, expiry, extensionCount, resources>>
  \/ /\ gzState = "appeal_pending"
     /\ gzState' \in {"upheld","reversed"}
     /\ UNCHANGED <<t, emergency, expiry, extensionCount, resources>>

Next == Tick \/ ActivateEmergency \/ EmergencyStep \/ ExpireEmergency \/ ExtendEmergency \/ GateZeroStep

Spec == Init /\ [][Next]_vars

=============================================================================
