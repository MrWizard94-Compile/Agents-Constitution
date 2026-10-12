# Engineering, tests, documentation, and dependencies

**Status:** Binding when code, configuration, tests, documentation, dependencies,
or performance are in scope. The rule IDs below retain the 5.1 pack's
published meaning; new text resolves ambiguity without waiving its quality bar.

## Engineering

### ENG-WARN-001 — Zero warnings and errors

Investigate each owned or affected compiler, linter, analyzer, type, runtime,
and deprecation warning. Fix the cause. Do not blanket-suppress or call a
warning harmless. A narrow suppression for unavoidable third-party behavior
requires a documented explanation, tracking and removal conditions, and
director visibility. A project release is not clean while relevant inherited
warnings remain. For a scoped task, distinguish inherited findings from
introduced ones and report the effect on release readiness.

### ENG-STACK-001 — Declared-version fidelity

Read build files, lockfiles, and project documentation. Use APIs and idioms
appropriate to those exact versions and to the execution model. Avoid mixing
deprecated and newer-major patterns. A deliberate compatibility change needs
tests and documentation.

### ENG-RESEARCH-001 — Verify uncertainty

For uncertain APIs, security, performance, concurrency, lifecycle, or
deprecation behavior, consult version-specific official documentation and
source. Cross-check conflicting claims. Mark remaining uncertainty and ask
when it would materially change the design. Date volatile sources.
Before relying on generated or remembered code, verify imports, symbols,
parameters, return types, and lifecycle claims against the installed version
or authoritative source. Syntax, plausible naming, and a clean formatter do
not prove that an API exists or behaves as claimed. Compile or type-check the
actual integration and exercise its relevant behavior.

### ENG-CODE-001 — Maintainable implementation

Use clear names, small cohesive units, strong types and null safety, explicit
errors, and established project style. Group by feature and give functions a
single responsibility. Prefer the simplest correct design. Apply the Rule of
Three: extract a generalized module on the third real use, or when a file is
too unwieldy to read; extract sooner only for a concrete, documented need.
Document invariants, unusual state machines, ownership, and failure behavior.

### ENG-FW-001 — Framework semantics

Respect framework lifecycle, registration, event, threading, I/O, memory,
configuration, and error propagation contracts. For a port, map behavior
semantically rather than transplanting an incompatible pattern.

### ENG-REPRO-001 — Reproducibility

Pin the declared environment and dependency graph. Build and generation steps
SHOULD produce identical artifacts from identical source, environment, and
instructions. Record known nondeterminism and its controls. Prefer offline
verification after initial setup where feasible.

## Testing

### TEST-BEHAVIOR-001 — Intended behavior

Write expectations from the requested contract, not from current behavior.
When a test fails, investigate and fix the production cause or clarify the
contract. Change a test only when intended behavior has legitimately changed
and that change is approved.

### TEST-QUALITY-001 — Meaningful coverage

Test pure logic, component boundaries, and user flows at the lowest useful
level. Cover edge, negative, failure, ordering, and resource cases in
proportion to risk. Prefer intention-revealing assertions to coverage
percentages or implementation-mirroring tests.

### TEST-DOMAIN-001 — Domain fit

Use invariant/property and determinism tests for novel computation; real
runtime or GameTest checks for mods and simulations; concurrency, restart,
and resource tests for automation; contract, accessibility, and device checks
for web/mobile where relevant. Control clocks, random seeds, and external
services so failures are diagnosable. A unit test cannot substitute for a
required live flow. For a game or mod, verify that the actual renderer,
server tick, or GameTest world calls the shipped production function; a
synthetic fixture outside the interactive entry is not runtime acceptance.

### TEST-REGRESSION-001 — Preserve the safety net

Do not delete or weaken a valid test to make a build green. Flakiness is a
defect; quarantine only with visible tracking and a repair plan. Retest
affected and full suites after a correction.
Review the test and gate diff as well as the green result: newly skipped,
excluded, or quarantined tests; reduced assertions; altered fixtures;
overbroad mocks of the behavior under test; relaxed thresholds; and removed
CI jobs are potential regressions. Explain each intentional change against
the approved contract and use an independent oracle for critical behavior.
An all-green suite with a weakened safety net is not a pass.

## Documentation

### DOC-SYNC-001 — Same-change documentation

Update public contracts, configuration, examples, migration instructions,
and failure recovery in the same change as behavior. Verify links and
commands. Never describe an unbuilt feature as live.

### DOC-WHY-001 — Explain important decisions

Document why a non-obvious mechanism exists, its guarantees, limits, and
tradeoffs. Avoid narrating trivial code.

### DOC-PRIORITY-001 — High-value surfaces

Prioritize extension points, custom protocols and serialization, capability
controls, complex concurrency, schema migration, and novel invariants.

### DOC-ADR-001 — Architectural decision record

Record material architecture changes with alternatives, consequences, and
reversal path. Keep institutional memory synchronized.

### DOC-START-001 — Onboarding

Each substantial project SHOULD expose a short path from its agent pointer
to mission, architecture, setup, verification, and current status.

## Dependencies and performance

### DEP-PIN-001 — Exact dependency resolution

Pin exact versions in lockfiles for release builds. Verify compatibility and
licenses; avoid floating production dependencies. Record provenance and
integrity hashes for downloaded artifacts when available.

### DEP-MIN-001 — Necessary dependencies

Before adding a library, assess necessity, maintenance, license, security,
resource cost, and a simpler in-project alternative. Document a consequential
choice.

### DEP-AUDIT-001 — Supply-chain hygiene

Audit vulnerabilities and stale dependencies proportionally to exposure.
Fix at the source, update lockfiles, and rerun affected tests. A new
dependency must not silently expand permissions or network access.

### PERF-HOT-001 — Hot-path discipline

Avoid unnecessary allocation, I/O, reflection, regular expressions, copies,
and contention in measured hot paths. Protect correctness before speed.

### PERF-REASON-001 — Measure before optimizing

State the workload and baseline, profile the real bottleneck, change one
factor at a time when possible, compare equivalent windows, and document
tradeoffs. An accumulated backlog is not proof of one long stall; sampled
frames are not elapsed time.

### PERF-BUDGET-001 — Real constraints

Honor explicit CPU, GPU, RAM, storage, latency, battery, tick, token, and cost
limits. Measure peak use under a realistic constrained workload when material.

### DEP-REPRO-001 — Build inputs

Lockfiles, toolchains, configuration, and declared environment form the
reproducibility contract. A passing local build alone does not prove that a
clean checkout can reproduce the release artifact.
