# WPAI delivery SOP

**Version:** 3.1.0

**Authority:** `AGENTS.md`
**Applies to:** Human-directed work under the WPAI Constitution

The ten-stage project-to-product workflow in the AGENTS Constitution 5.1 pack
is preserved as a complete path for broad product work. For a narrow task,
scale the depth of each phase to its risk and acceptance criteria. Do not
perform ceremonial research or documentation that adds no decision value.
Never scale away safety, quality, authorization, or evidence.

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

## 5. Implement

Build dependencies first. Keep affected code, tests, configuration, and docs
synchronized. Preserve behavior unless the requested change intentionally
alters it. Keep each checkpoint buildable and source-controlled. Avoid
unrelated edits and protect existing worktree changes.

## 6. Verify and harden

Run relevant formatting, compilation, linting, type checking, static analysis,
unit, integration, property, end-to-end, security, and dependency checks.
Exercise real runtime and device flows when acceptance requires them. Distinguish
the first independent failure from downstream cascades. Fix causes, then rerun
affected and broader gates. A successful catalog scan or artifact copy is
preparation; runtime acceptance requires a clean launch and behavior flow.
Verify generated API claims against the installed stack. Inspect changes to
tests, fixtures, mocks, skips, and CI gates before trusting green status. Use
an independent oracle for consequential behavior, such as a real consumer,
reference implementation, measured workload, accessibility inspection, or
human acceptance, selected by the quality profile.

## 7. Audit the evidence

Record exact commands, exit codes, versions, artifacts, and test scope. Report
source QA, packaging, deployment, runtime behavior, and physical acceptance
separately. Do not infer one from another. Keep inherited findings distinct from
new defects, and do not call a release clean if a relevant blocker remains.
Reconcile the evidence against the original quality profile and changed scope.
Investigate contradictions and review-tool findings against the current tree;
withdraw unsupported claims. A percentage, green badge, or polished artifact
is not a substitute for evidence about the intended use.

## 8. Package and deliver

Execute the 15-point Section 0 gate. Present the outcome, changed-path manifest,
verification, risks, evidence boundaries, and next actions under
`REV-PACK-001`. A final-quality request requires the strongest quality
achievable within the authorized scope and actual constraints; do not reserve
an obvious in-scope correction for an artificial later pass.

## 9. Publish only to the authorized destination

Commit, push, open a PR, merge, release, deploy, or distribute only when the
director authorized that action and destination. Verify remote state after each
external action. Protect shared history; never force-push to cover drift.
Release tags and published versions are immutable.

## 10. Learn and evolve

For each top-level skill invocation, complete one meaningfully useful
Constitution change under `GOV-EVOLVE-001`. Ground it in a specific observed
failure, ambiguity, inefficiency, or quality gap. Search for an existing
canonical rule first, validate the improvement, and record it in the evolution
ledger. It governs only later invocations after acceptance on `main`.

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
