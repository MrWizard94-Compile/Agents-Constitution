# Quality assurance map

**Status:** Non-binding design aid. Binding requirements remain in `AGENTS.md`,
`SOP.md`, and the one-home `law/*` files. Reviewed 2026-10-12.

The goal is the highest quality feasibly achievable for the authorized work,
not a fictional guarantee of universal perfection. This is **not** permission
to slack, skip, shorten, or weaken a required check. Define the intended use,
risks, applicable industry rules, acceptance evidence, and known limits before
claiming excellence. A small change needs a focused profile; a safety-critical
or public release needs a substantially stronger one. If an applicable check
cannot be completed, name the blocker and risk and withhold the completion
claim. The Section 0 gate still decides whether a completion claim is allowed.

| Dimension | A useful falsification question | Constitutional home |
|---|---|---|
| Purpose-fit and craft | If presentation and volume are stripped away, does each material part still serve the brief and real intended use, without invented detail or generic filler? Has the delivered form been examined? | `CONST-CRAFT-001`; `CONST-COMPLETE-001` |
| Functional fit and completeness | Does the real user flow satisfy each agreed outcome, including failure and recovery? | `CONST-COMPLETE-001`; `TEST-BEHAVIOR-001`; `MIG-VERIFY-001` |
| Stack and factual correctness | Do the imports, symbols, versions, contracts, and actual runtime match the implementation's claims? | `ENG-STACK-001`; `ENG-RESEARCH-001`; `ENG-FW-001` |
| Test integrity | Would the suite still fail if the defect were reintroduced, or has a skip, fixture, mock, assertion, or CI gate concealed it? | `TEST-QUALITY-001`; `TEST-REGRESSION-001` |
| Security, privacy, and permission | Can untrusted content, excess privilege, secrets, or a dependency cross the intended boundary? | `SEC-INPUT-001`; `SEC-PRIV-001`; `SEC-SECRET-001`; `SEC-SUPPLY-001` |
| Usability and accessibility | Can representative people complete the intended task with the input, display, language, and assistive modes they need? | `TEST-DOMAIN-001`; `DOC-SYNC-001`; project acceptance criteria |
| Reliability and operations | Does the system recover from faults, interruption, restart, and unavailable shared services without data loss or false success? | `OBS-FAIL-001`; `LIFE-TOOL-001`; `REL-UPGRADE-001` |
| Technical resourcefulness | Was an authorized workaround built and checked against the original outcome, rather than merely suggested, silently reduced, endlessly retried or made to bypass a boundary? | `CONST-RESOURCEFUL-001`; `SEC-PRIV-001`; `TEST-BEHAVIOR-001` |
| Performance and resources | Does a realistic constrained workload meet explicit time, memory, energy, and cost budgets without sacrificing correctness? | `PERF-REASON-001`; `PERF-BUDGET-001` |
| Provenance and reproducibility | Can the delivered artifact be traced to the intended source, dependencies, build environment, and approval? | `ENG-REPRO-001`; `DEP-REPRO-001`; `REL-DETERM-001`; `GOV-SSOT-001` |
| Runtime consumer closure | Does the actual shipped consumer load the verified bytes and exercise the proposed hook, conversion, or cache through normal lifecycle and failure paths? | `ENG-FW-001`; `TEST-DOMAIN-001`; `LOW-RISK-001`; `PERF-HOT-001` |
| Scope and human control | Was each dependent action gated by its prerequisite, and were material architecture or public-contract changes reviewed? | `CONST-AUTH-001`; `SEC-AUTHZ-001`; `CTX-ASSUME-001` |
| Evidence and handoff | Are findings reproduced, status claims limited to observed stages, and resumption possible after context or service loss? | `REV-PACK-002`; `CTX-SELF-001`; `CONST-DONE-001` |

Choose domain-specific standards in addition to this map. For example, a web
interface may require WCAG conformance evidence; a web service can use OWASP
ASVS security requirements; a software release can use source/build
provenance expectations; a regulated or physical product must use its own
applicable rules and real-world acceptance. Do not claim certification or
conformance because a checklist mentions a standard. Record version, scope,
test method, and result for every actual conformance claim.

## Research basis and limits

- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) describes a
  product-quality model for requirements and evaluation. This map is an
  adaptation, not a reproduction or certification of that standard.
- [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
  identifies confident false content, including output that diverges from a
  prompt, as a generative-AI risk; this motivates independent verification of
  generated claims and brief fidelity.
- [NIST SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) provides a
  secure-development framework; the Constitution applies its risk-reduction
  logic to agent-authored work without asserting NIST endorsement.
- [OWASP LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
  analyzes excess functionality, permissions, and autonomy; its threat model
  supports scoped actions and explicit high-impact authorization.
- [OWASP ASVS](https://owasp.org/projects/asvs) supplies testable security
  requirements for web applications; it is domain guidance, not a universal
  checklist for every project.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) defines testable web
  accessibility criteria. Passing automated checks alone is not a complete
  accessibility assessment.
- [SLSA build verification](https://slsa.dev/spec/v1.2/verifying-artifacts)
  explains that provenance helps only when verified against expectations;
  a recorded source hash is evidence of identity, not proof of quality.

The specific rule wording and quality-profile workflow are WPAI engineering
decisions informed by these sources and observed project failures. No cited
standard guarantees an error-free result, and this map must not be used to
inflate a partial validation into a completed delivery.
