# Rule registry and historical mapping

**Status:** Binding index. A rule's detailed text has exactly one canonical
home. A reference here is not a second rule definition. IDs are never reused.

## Active homes

| Rule IDs | Canonical home |
|---|---|
| `CONST-AUTH-001`, `CONST-COMPLETE-001`, `CONST-CRAFT-001`, `CONST-DEP-001`, `CONST-DONE-001`, `CONST-GATE-001` | `AGENTS.md` |
| `GOV-SSOT-001`, `GOV-FREEZE-001`, `GOV-EVOLVE-001`, `GOV-RATCHET-001`, `GOV-CHANGE-001`, `GOV-MIRROR-001`, `GOV-ARCHIVE-001` | `governance/EVOLUTION.md` |
| `ENG-WARN-001`, `ENG-STACK-001`, `ENG-RESEARCH-001`, `ENG-CODE-001`, `ENG-FW-001`, `ENG-REPRO-001` | `law/ENGINEERING.md` |
| `TEST-BEHAVIOR-001`, `TEST-QUALITY-001`, `TEST-DOMAIN-001`, `TEST-REGRESSION-001` | `law/ENGINEERING.md` |
| `DOC-SYNC-001`, `DOC-WHY-001`, `DOC-PRIORITY-001`, `DOC-ADR-001`, `DOC-START-001` | `law/ENGINEERING.md` |
| `DEP-PIN-001`, `DEP-MIN-001`, `DEP-AUDIT-001`, `DEP-REPRO-001` | `law/ENGINEERING.md` |
| `PERF-HOT-001`, `PERF-REASON-001`, `PERF-BUDGET-001` | `law/ENGINEERING.md` |
| `SEC-INPUT-001`, `SEC-PRIV-001`, `SEC-SURFACE-001`, `SEC-SECRET-001`, `SEC-LIB-001`, `SEC-SUPPLY-001`, `SEC-AUTHZ-001` | `law/SECURITY.md` |
| `OBS-LOG-001`, `OBS-FAIL-001`, `OBS-PRIV-001`, `OBS-NOVEL-001` | `law/SECURITY.md` |
| `VCS-ATOMIC-001`, `VCS-MSG-001`, `VCS-CLEAN-001`, `VCS-HISTORY-001` | `law/OPERATIONS.md` |
| `REF-PLAN-001`, `REF-GREEN-001`, `REF-SAFE-001` | `law/OPERATIONS.md` |
| `MIG-INV-001`, `MIG-FEEL-001`, `MIG-NOTES-001`, `MIG-VERIFY-001`, `MIG-CLEAN-001` | `law/OPERATIONS.md` |
| `OPS-DEL-001`, `OPS-DEL-002` | `law/OPERATIONS.md` |
| `REL-PACKAGE-001`, `REL-DETERM-001`, `REL-UPGRADE-001`, `REL-HARDEN-001` | `law/OPERATIONS.md` |
| `LIFE-PHASE-001`, `LIFE-NODEAD-001`, `LIFE-TOOL-001` | `law/OPERATIONS.md` |
| `REV-PACK-001`, `REV-PACK-002`, `REV-PACK-003` | `law/COLLABORATION.md` |
| `AI-COORD-001`, `AI-COORD-002`, `AI-COORD-003`, `AI-COORD-004` | `law/COLLABORATION.md` |
| `CTX-SELF-001`, `CTX-GRAPH-001`, `CTX-ASSUME-001`, `CTX-ONBOARD-001` | `law/COLLABORATION.md` |
| `MEM-LIVE-001`, `MEM-SAME-001`, `MEM-FIRST-001`, `MEM-HEALTH-001` | `law/COLLABORATION.md` |
| `RND-INVAR-001`, `RND-CORE-001`, `RND-DOC-001`, `RND-SPIKE-001` | `law/SPECIALIST.md` |
| `IP-INVENTION-001`, `IP-PATENT-001`, `IP-SECRET-001` | `law/SPECIALIST.md` |
| `NET-PROTO-001`, `NET-AUTH-001`, `NET-DOC-001`, `NET-CHATTY-001` | `law/SPECIALIST.md` |
| `LOW-RISK-001`, `LOW-REASON-001`, `LOW-TEMP-001`, `LOW-CACHE-001` | `law/SPECIALIST.md` |
| `HW-RESPECT-001`, `HW-MEM-001`, `HW-ALT-001` | `law/SPECIALIST.md` |
| `COST-TOKEN-001`, `COST-CACHE-001` | `law/SPECIALIST.md` |

Every active ID MUST have exactly one rule heading or protected-rule definition
in its home. New IDs require an update to the relevant law file and this index
in the same reviewed change. Do not use a retired name for new work.

## Retired 5.1 IDs and successors

The old names below remain searchable for interpretation of historical audits.
They are **not** active aliases and do not authorize a second rule definition.

| Retired ID or family | Current interpretation |
|---|---|
| `CONST-ONESHOT-001`, `CONST-CONTRACT-002` | `CONST-COMPLETE-001` and `CONST-DEP-001` |
| `CONST-EMPIRE-001`, `ENG-SCOPE-001` | Scope and loading matrix in `AGENTS.md` |
| `CONST-AUTH-002`, `CONST-CONFLICT-001` | `CONST-AUTH-001` and conflict escalation in `AGENTS.md` |
| `CONST-ONEHOME-001`, `GOV-REG-001`–`004` | This registry's one-home and no-reuse contract |
| `CONST-AMEND-001`, `GOV-LOCK-001`–`005` | `GOV-CHANGE-001`, `GOV-RATCHET-001`, `GOV-ARCHIVE-001` |
| `CONST-CONTRACT-001`, `003`, `005`, `006` | Human–agent contract in `AGENTS.md`; review and history in `law/COLLABORATION.md` |
| `CONST-CONTRACT-004` | Novel problem solving in `law/SPECIALIST.md`, subject to all quality rules |
| `CONST-DONE-002`, `003` | Spike and evidence clauses under `CONST-DONE-001` |
| `SOP-PHASE-001`, `SOP-GATE-001` | Ten-stage `SOP.md` and `CONST-GATE-001` |
| `PERF-TIER-001` | Correctness-before-optimization in `law/ENGINEERING.md` |
| `OPS-DEL-003`, `004` | Evidence-backed reporting in `law/COLLABORATION.md` and this registry |
| `LIFE-BIRTH-001`, `LIFE-PROCESS-001` | Project start and phase language in `law/OPERATIONS.md` |
| `IP-DOC-001` | `DOC-SYNC-001` applied to invention notes |
| `GOV-INT-001`–`006`, `GOV-SYNC-001` | Source validator and `GOV-MIRROR-001` |
| `GOV-OVR-001` | Override contract in `AGENTS.md` and `templates/PROJECT-OVERRIDE.md` |
| `GOV-PORT-001`–`006` | Path-independent identity and `GOV-MIRROR-001` |
| `CONST-WARN-001`, `CONST-TEST-001`, `CONST-DOC-001`, `CONST-SEC-001` | Retired pre-5.1 shorthand; use `ENG-WARN-001`, `TEST-BEHAVIOR-001`, `DOC-SYNC-001`, `SEC-INPUT-001` |

If a retired rule carried behavior not represented by its successor, amend the
successor's canonical home with a testable proposal. Do not reactivate the
old ID or silently discard the requirement.
