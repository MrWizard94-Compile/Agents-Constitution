# WPAI delivery SOP

**Version:** 3.5.0

**Authority:** `AGENTS.md`
**Applies to:** Human-directed work under the WPAI Constitution

## SOP-EXEC-001 — Always execute the workflow

Every invocation under this Constitution MUST use this SOP from intake through
closeout, in every skill mode. Reading or mentioning the SOP is not execution.
This includes research, advice, audits, plans, creative work, code, maintenance,
adoption, recovery and delivery. A review-only task produces a reviewed analysis
or proposal at stage 5; it does not acquire implementation or publication rights.

Account for all ten stages. Scale depth and evidence to the actual risk and
medium, never silently omit a stage. Research at stage 3 may be N/A with a reason
when no uncertain or changing claim needs investigation. Publication at stage 9
may be N/A when it is outside the requested outcome. Missing permission for a
requested deployment is an OPEN gate, not N/A. The other stages always apply;
a small task may satisfy them briefly using the conversation and existing
verified evidence. Do not create ceremonial documents or gratuitous tool calls.

Keep one compact run record identifying the invocation, frozen law SHA, scope,
candidate, acceptance criteria, stage results and evidence. Each stage is DONE,
OPEN or reasoned N/A; DONE refers to its stated exit condition, not elapsed
effort. For non-trivial work, use the machine-checkable format in
[the workflow record guide](references/workflow-record.md). A trivial answer
may account for the same fields compactly in its handoff. Keep sensitive task
evidence with the project or private working records, not in this public source.

Stages are ordered by dependency, not a rigid waterfall. Research, planning,
implementation and testing may iterate. When scope, inputs, candidate bytes or
environment change, reopen every affected acceptance item and downstream gate;
old evidence remains historical and cannot certify the changed result. Reuse
unaffected checks only with a stated equivalence of their relevant inputs.
Record material decisions and authorization before their dependent actions.
Existing authorization persists within its exact scope; do not ask repeatedly.

A continuation, approval reply, recovery, handoff or compaction resumes the
existing invocation and freeze under `GOV-FREEZE-001` and `CTX-SELF-001`.
Reconcile the record with the latest genuine instruction and current state.
Workers account for their assigned scope; the integrator owns the complete
workflow and the single evolution obligation. Delegation creates no authority.
The machine-checkable complete record belongs to that top-level invocation.
Workers supply stage updates and evidence to it; they do not need a separate
complete ten-stage record or their own amendment. A worker can finish its
assigned contribution while the parent workflow remains open.

Before claiming completion, account for stages 9 and 10 and recheck stages 7
and 8 against the final state. An applicable OPEN/FAIL gate blocks Done; report
partial progress and the exact remaining requirement. A director stop, pause or
cancellation takes precedence: preserve a safe checkpoint, report stopped or
partial, and do not continue merely to finish a checklist or evolution quota.
The existing gates in `AGENTS.md` remain controlling. A valid record is evidence
organization, not proof that its claims are true or that an agent complied.

## Stage exits

| Stage | Exit evidence required before dependent work or a completion claim |
|---|---|
| 1. Contract | Outcome, scope, authority, law SHA, quality profile and independently checkable acceptance criteria |
| 2. Baseline | Current sources and consumers inspected; inherited state and recovery needs recorded |
| 3. Design | Material uncertainty resolved or visible; chosen approach, alternatives and boundaries justified, or reasoned N/A |
| 4. Plan | Complete authorized slice, dependencies, verification and recovery path |
| 5. Produce | Requested code, artifact, analysis or proposal exists as a complete reviewable candidate |
| 6. Verify | Each acceptance item has the required observation on that candidate; failures repaired or OPEN |
| 7. Audit | Claims reconciled with evidence, test changes reviewed, limitations and residual findings explicit |
| 8. Review package | Section 0 scored; candidate and evidence ready for director review; completion withheld if gates remain |
| 9. Authorized delivery | Exact authorized destination/state independently confirmed, or reasoned N/A; requested but unverified delivery remains OPEN |
| 10. Close and evolve | One useful amendment staged/in PR/accepted; final state, limitations and next owner/action reconciled |

## 1. Establish the working contract

Identify the outcome, affected repositories and people, exclusions, acceptance
criteria, and the evidence needed to support completion. Separate read-only
inspection, local mutation, publication, deployment, spending, external
communication, and destructive cleanup. Record the canonical law commit SHA,
project instructions, current branch, worktree state, and inherited findings.
Ask the director when a missing choice would materially change the result.
Create a risk-scaled quality profile for the deliverable: which dimensions of
functional fit, correctness, reliability, security/privacy, usability and
accessibility, maintainability, compatibility, performance/resources, and
release or operational readiness matter; what the relevant industry's
current standards are; and what independent observation would falsify each
important claim. Mark inapplicable dimensions with a reason. See the
[quality assurance map](docs/QUALITY-ASSURANCE-MAP.md) for examples, not a substitute for the
project's actual requirements. Risk scaling changes the depth of relevant
checks, not whether a known required check may be skipped. If a necessary
oracle is unavailable, report the acceptance gate as unmet and arrange a
safe next step; do not call the result Done.
For every medium, include the intended-use and substance check in
`CONST-CRAFT-001`; a polished surface is not an acceptance criterion by itself.
When a specification enumerates named player-facing controls, fields, or
surfaces, treat each named item as its own acceptance unit under
`CONST-COMPLETE-001`; a parent screen or section that omits a named control is
not complete.

Give each material acceptance criterion a stable identifier and required
evidence class before production. This applies to all deliverables, including
documents and governance changes. An approval, build, fixture, installed file
or live observation satisfies only the class it actually demonstrates.

## 2. Inventory and baseline

Read current source and project guidance before editing. Inventory affected
files, consumers, interfaces, dependencies, variants, and data. For migration or
cleanup, record exact targets and recovery paths before moving or deleting.
Establish current build and runtime evidence, versions, hashes, and known
failures. Label facts as verified, director decision, inference, or unverified.

## 3. Research and design

Use official documentation, primary standards, library source, and relevant
repository evidence for uncertain or changing claims. Compare enough reference
projects to expose real tradeoffs; ten references are appropriate only when
their breadth changes the design. Record dates and direct sources for volatile
facts. For major work, design interfaces, trust boundaries, migration, rollback,
compatibility, and verification before coding.

## 4. Plan a complete slice

Define prerequisites, implementation order, failure modes, tests, documentation,
and rollback. A slice may be small, but it must be usable and validated as its
own unit. State which evidence classes will remain outside the current scope.
Preserve the full requested outcome when scheduling slices: track remaining
criteria and dependencies explicitly; completing one slice does not complete
the parent goal. Set a bounded investigation/retry budget and a useful safe
checkpoint for long work. Escalate only the precise input or decision needed
after applying `CONST-RESOURCEFUL-001`; continue independent authorized work.

## 5. Implement

Build dependencies first. Keep affected code, tests, configuration, and docs
synchronized. Preserve behavior unless the requested change intentionally
alters it. Keep each checkpoint buildable and source-controlled. Avoid
unrelated edits and protect existing worktree changes.
Treat technical obstacles as engineering work under `CONST-RESOURCEFUL-001`,
not an automatic stop or permission to narrow the requested outcome. Its
canonical home in `AGENTS.md` defines workaround, verification and escalation.
Inventory enumerated named controls from the specification and wire each one
(`CONST-COMPLETE-001`); do not call a destination done because the parent
screen exists.

## 6. Verify and harden

Run relevant formatting, compilation, linting, type checking, static analysis,
unit, integration, property, end-to-end, security, and dependency checks.
Exercise real runtime and device flows when acceptance requires them. Distinguish
the first independent failure from downstream cascades. Fix causes, then rerun
affected and broader gates. A successful catalog scan or artifact copy is
preparation; runtime acceptance requires a clean launch and behavior flow.
When acceptance names an action, require evidence of that action and its
observable result under `MIG-VERIFY-001`; a token from another path is
insufficient. Check named quantities and shared producers under
`TEST-QUALITY-001`, including payload, sampling and culling evidence.
Verify generated API claims against the installed stack. Inspect changes to
tests, fixtures, mocks, skips, and CI gates before trusting green status. Use
an independent oracle for consequential behavior, such as a real consumer,
reference implementation, measured workload, accessibility inspection, or
human acceptance, selected by the quality profile.
Inspect non-code work in its delivered form as well; a source file or prompt
alone cannot establish the quality of a rendered, heard, or experienced result.
Speed is not a reason to omit that inspection or any other applicable check
(`CONST-QUALITY-001`).

## 7. Audit the evidence

Record exact commands, exit codes, versions, artifacts, and test scope. Report
source QA, packaging, deployment, runtime behavior, and physical acceptance
separately. Do not infer one from another. Keep inherited findings distinct from
new defects, and do not call a release clean if a relevant blocker remains.
Reconcile the evidence against the original quality profile and changed scope.
Investigate contradictions and review-tool findings against the current tree;
withdraw unsupported claims. A percentage, green badge, or polished artifact
is not a substitute for evidence about the intended use.
A human approval of terms or an adaptation does not close a trial, demo or
live-consumer gate, and the reverse also holds (`REL-HARDEN-001`).

## 8. Package for review

Execute the 15-point Section 0 gate. Present the outcome, changed-path manifest,
verification, risks, evidence boundaries, and next actions under
`REV-PACK-001`. A final-quality request requires the strongest quality
achievable within the authorized scope and actual constraints; do not reserve
an obvious in-scope correction for an artificial later pass.
This is the pre-publication review gate. It does not certify later publication,
installation or runtime. Include the SOP run record and resolve missing stage
evidence before claiming the requested scope complete.

## 9. Publish only to the authorized destination

Commit, push, open a PR, merge, release, deploy, or distribute only when the
director authorized that action and destination. Verify remote state after each
external action. Protect shared history; never force-push to cover drift.
Release tags and published versions are immutable.
Before claiming a PR current or recommending a merge order, verify the
fetched base and combined result under `VCS-INTEG-001`.
When deployment is in scope, verify the intended consumer after the change and
name the operational owner, observation window, rollback trigger and recovery
path. A queued job or successful upload is not observed deployment. If an
authorized operation has an uncertain outcome, inspect its state before retry
to avoid duplicate writes, charges or releases. A required observation window
that has not elapsed remains OPEN; do not create unsolicited recurring jobs.

## 10. Close, hand off and evolve

For each top-level skill invocation, complete one meaningfully useful
Constitution change under `GOV-EVOLVE-001`. Ground it in a specific observed
failure, ambiguity, inefficiency, or quality gap. Search for an existing
canonical rule first, validate the improvement, and record it in the evolution
ledger. It governs only later invocations after acceptance on `main`.
Validate the complete apply-ready amendment even when publication is outside
scope; report **staged, not propagated** under `GOV-EVOLVE-001`. Do not recurse
into another evolution obligation or modify current law to pass this task.

Reconcile the final candidate, authorized external state and acceptance record.
Re-run affected verification after later edits or integration; re-score Section
0 against what is actually handed off. State delivered outcome, scope, evidence
limits, remaining work and next owner/action. Retire only authorized temporary
state with recovery preserved. The run ends as complete, partial or stopped;
none of those labels silently waives an unmet criterion or accepts new law.

## Evidence vocabulary

| Status | Minimum evidence |
|---|---|
| Verified | Direct check passed for the stated scope |
| Partial | Some checks passed; named acceptance gates remain |
| Packaged | Artifact created and integrity checked |
| Deployed | Intended environment reports the intended revision live |
| Physically accepted | Required person/device flow completed |
| Inherited finding | Pre-existing condition evidenced independently |
| Unstarted | No implementation or validation evidence |
