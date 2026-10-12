---
name: wpai-constitution
description: >
  Apply and evolve the WPAI Constitution from its canonical GitHub source. Use
  for WPAI delivery, Section 0 gates, constitutional self-audits, adoption into
  a project, source consolidation, or a direct request to use the Constitution.
  Each top-level call must produce one meaningful Constitution improvement.
metadata:
  short-description: "Apply and evolve WPAI Constitution"
  skill-version: "6.2.1"
  canonical-source: "MrWizard94-Compile/Agents-Constitution"
---

# WPAI Constitution skill

The accepted `main` of
[the canonical repository](https://github.com/MrWizard94-Compile/Agents-Constitution)
is the single editable source for this skill and its binding law. The skill is
a loader and executor, not a second constitution. Installed folders are
generated mirrors, never authority. The source identity and distribution
manifest live in `SOURCE.json`.

## Start each top-level call

1. Resolve the full SHA of accepted GitHub `main`, or a director-named
   accepted release. Validate `SOURCE.json`, `VERSION`, and the file manifest;
   record the SHA. The source revision is frozen for this call. If GitHub is
   unavailable, use only a previously verified mirror, disclose degraded
   sync, and do not claim freshness.
2. Read `references/always-load.md`, `AGENTS.md`, `SOP.md`, and
   `governance/EVOLUTION.md` from that **same** revision. Read relevant `law/*`
   files using the matrix in `AGENTS.md`. Read the project's own instructions
   for mission, stack, and acceptance criteria. Do not substitute an adjacent
   folder, old pack, or web search result for binding law.
3. Identify the user-approved scope, current state, dependencies, risks,
   checks, and necessary authority. For a broad refactor, migration, or
   cleanup, make a concise plan with rollback before mutating state. Establish
   the risk-scaled quality profile in `SOP.md`; a missing required check is a
   named acceptance gap, never a shortcut to Done.
4. Execute the applicable SOP with production completeness, intended-behavior
   tests, root-cause warning repair, documentation, and honest evidence.
5. Before claiming a delivery, score all 15 Section 0 checks in `AGENTS.md`.
   Any applicable FAIL stops the completion claim. Report verification limits
   plainly; tests do not prove deployment or physical acceptance.
6. Satisfy the single evolution obligation below, then report its exact
   canonical status in one line.

## Exactly one meaningful evolution obligation

Every top-level call using this skill **MUST** produce one coherent,
meaningfully useful change to the WPAI Constitution. A coherent change may
touch related law, tool, test, and documentation files. The evolution subtask
does not recursively start another top-level call. A change authored now
cannot govern this call; it is eligible only after acceptance on `main` and a
later invocation.

Choose an observed, generalizable failure, ambiguity, inefficiency, or
quality gap. State what future behavior changes, why it is useful, and how a
test or review could falsify it. Search for the existing canonical home
before adding a rule. Preserve safety, human authority, protected quality
rules, and one-home ownership. A version bump, timestamp, ledger/changelog
entry, typo, cosmetic edit, duplication, or renaming alone does **not** count.

Implement and validate the change in an isolated branch. Update the ledger
and version as supporting evidence. Submit a PR to the canonical repository;
do not race direct edits to `main`. Merge only under the review conditions in
`governance/EVOLUTION.md`, then verify the accepted SHA and sync mirrors.
If a task is read-only or lacks publication authority, produce a complete
validated apply-ready change and report **staged, not propagated**; never
pretend the SSOT changed. Do not make unrelated external changes merely to
fulfill evolution.

## Modes

| Signal | Mode | Required result |
|---|---|---|
| Default implementation or delivery | Enforce | Completed work, Section 0 evidence, evolution status |
| Section 0 or pre-delivery gate | Gate | 15 PASS/FAIL/N/A scores and 3–12 line audit |
| Adopt into project | Adopt | Project pointer, consumer audit, pinned CI source; no law fork |
| Self-audit or verify Constitution | Self-run | Source validator, tests, links, and concrete findings |

All modes owe one meaningful evolution for a top-level call. The director can
limit a task to analysis; that limits publication authority, not the duty to
prepare an honest candidate.

For adoption or cleanup, run `python tools/check-adoption.py <project-root>`
from a verified source checkout after updating project pointers, CI, and
manifests. Resolve all findings before removing an old pack or claiming that
the project has no shadow law.

## Runtime and quality checks

For a third-party-assembled runtime, inventory declared and embedded
dependencies and compatible versions. Obtain missing artifacts from
authoritative sources with integrity data when available. Test a repaired
third-party fixture without the product under test before attributing its
failure or success. Separate first independent load failures from cascades.
A copied dependency or catalog scan is not runtime acceptance; relaunch and
exercise the relevant flow.

For generated or serialized content, declarative assets, low-level hooks,
mutable hot-path caches, and intrusive diagnostics, apply the scoped consumer
and lifecycle checks in `law/ENGINEERING.md`, `law/SECURITY.md`, and
`law/SPECIALIST.md`. Keep source, packaged bytes, live consumer behavior,
and performance attribution separate; none proves the others by itself.

When the user requests a final, professional, or production-ready result,
target the highest quality reasonably achievable within the authorized scope
and actual constraints on the first serious delivery. Do not knowingly reserve
an available material fix for a later polish pass. Before handoff, ask whether
any known, presently fixable defect remains and whether inspection occurred
at the strongest available level.

## Handoff minimum

State what changed and why, source SHA, changed paths, exact verification and
its limits, unresolved risks, and next human action. Distinguish source QA,
package, install, runtime, physical acceptance, and publication. Include a
compact `Skill evolution:` line naming the meaningful change and whether it
is staged, in PR, or accepted on canonical `main`.
