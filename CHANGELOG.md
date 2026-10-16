# Changelog

## 6.16.3 — 2026-10-16 (candidate)

- Extended adoption text scanning to native/JVM sources, shell entry points,
  and related source/build languages. Retired-law references in compiled CLI
  help no longer disappear solely because their file suffix was omitted.
  Git and filesystem fixtures retain size limits, binary exclusion, canonical
  URL acceptance, and existing path checks. This is literal-source coverage,
  not proof of dynamic data flow or installed consumer behavior.

## 6.16.2 — 2026-10-15 (candidate)

- Changed the evolution guard from a filename check to committed-content
  comparison. Synchronized release-version fields, JSON formatting, and
  unchanged-content renames cannot satisfy evolution alone. Git fixtures
  cover merge-base drift, negative paths, and preservation of meaningful
  Markdown/code whitespace. Passing output explicitly requires semantic
  review; the tool does not certify usefulness or widen workflow-only scope.

## 6.16.1 — 2026-10-15 (candidate)

- Fixed adoption scanning through linked ancestors of Git-listed files.
  Each candidate's components are checked outermost-first before content is
  read; symlinks and Windows reparse points leave explicit unresolved coverage.
  Ordinary leaf links no longer silently pass, and both audit modes reject
  linked project-root routes. Real junction/symlink regression fixtures cover
  the boundary; concurrent hostile directory replacement is not sandboxed.

## 6.16.0 — 2026-10-14 (candidate)

- Required end-to-end resource acceptance for host-plus-provider workflows on
  the intended corpus. Cold host usability, enabled file-type scope, and peak
  combined process use now matter alongside warm query speed. Configuration
  trials must be reversible, disclose hidden content, and cannot close the
  live gate when the user-facing host still fails to load (`PERF-BUDGET-001`).

## 6.15.0 — 2026-10-14 (candidate)

- Required generated artifacts to pass their actual consumer's discovery
  boundary: root location, ignore/exclusion rules, registration, and packaged
  paths. A valid but hidden file is not a delivered view. Preflight unsafe
  destinations, test rejection, and keep live acceptance open until the
  intended consumer visibly loads a valid artifact. This extends `ENG-FW-001`.

## 6.14.0 — 2026-10-14 (candidate)

- Required representation parity and provenance across derived indexes,
  graphs, retrieval, statistics, and visuals that claim a relationship. A
  supported source-link form cannot silently vanish downstream or be counted
  as an orphan. Consumer-level tests must exercise each form alone. This
  extends `ENG-FW-001` at its existing canonical home.

## 6.13.0 — 2026-10-14 (candidate)

- Required a bounded freshness and stale-path recovery contract for
  agent-facing file indexes. Owned writes invalidate immediately; external
  removals cannot leave supposedly current links; additions and edits become
  visible within a stated bound or explicit refresh. Tests must exercise
  create, edit, delete, installed-consumer behavior, and realistic refresh
  cost. This extends `ENG-FW-001` rather than introducing duplicate law.

## 6.12.0 — 2026-10-14 (candidate)

- Added an explicit, bounded filesystem adoption audit for ignored or
  standalone project directories without their own Git root. It inspects
  first-party source and built output regardless of a parent ignore rule,
  excludes named dependency caches, and refuses a clean result when a link,
  nested repository, or scan limit leaves coverage unresolved. The default
  exact-Git-root audit remains unchanged.

## 6.11.0 — 2026-10-14 (candidate)

- Closed a migration evidence gap for agent-facing context providers. Project
  adoption now includes hooks and tool-emitted onboarding responses, with a
  probe of the installed entry point after process restart. Source changes or
  a clean static audit alone cannot establish that a live agent stopped
  receiving retired-law instructions.

## 6.10.0 — 2026-10-14 (candidate)

- Closed two residual-discovery blind spots: the all-drive inventory now
  recognizes `SOUL.md` and `AGENTS.md` pre-pack backups by filename even when
  their bodies lack scanner signatures; the project adoption audit checks
  ignored retired law in bounded agent-config locations without crawling
  arbitrary ignored dependencies or following links. A dated inventory must
  be refreshed before it can support an absence or cleanup claim.

## 6.9.0 — 2026-10-14 (candidate)

- Required a persistent class-transform cache to be linkage-complete.
  `LOW-CACHE-001` forbids returning a hit whose missing dependency was
  defined only as a side effect of the original transform, unless that
  dependency is defined before the hit is returned. Skipping only the class
  that names the missing type, while a cached caller of a symbol from the
  same pass remains a hit, is a defect. The source validator guards the
  rule text. `COST-CACHE-001` stays the home for an agent's working notes.

## 6.8.1 — 2026-10-14 (candidate)

- Corrected the live ruleset audit to classify a redacted bypass-actor field
  as unverified, not policy drift. Added CLI-level outage, redaction, drift,
  and passing-path tests so the tool cannot misreport missing evidence.

## 6.8.0 — 2026-10-14 (candidate)

- Added a read-only live audit of the canonical GitHub `main` ruleset. It
  detects missing or inactive PR, strict `validate`, force-push, and deletion
  gates, check-source spoofing, bypass actors, unintended approval requirements,
  and branch-target drift. API failure is reported as unverified, never a pass.

## 6.7.0 — 2026-10-13 (candidate)

- Required byte-exact reads of the frozen revision and made loader drift
  explicit. `tools/check-frozen-load.py` confirms a full-SHA checkout, an
  unmodified tracked tree, and raw-byte hashes for every binding file, and
  compares the running loader's `skill-version` numerically with the frozen
  law. GOV-FREEZE-001 demotes summarized page text to orientation, makes the
  frozen `SKILL.md` govern a stale or newer loader, and requires both facts in
  the handoff. The source validator guards the contract text.

## 6.6.1 — 2026-10-13 (candidate)

- Prevented overlapping mirror installations and offline recovery from racing
  the same target. Stable-order, non-blocking OS file locks cover every target
  through journal recovery, installation, verification, and cleanup. A real
  second-process test confirms that reordered, overlapping batches fail
  without changing generated content, then succeed after holder termination.
  Persistent empty lock files are reserved control files, not binding mirrors.

## 6.6.0 — 2026-10-13 (candidate)

- Made mirror installation recoverable across all targets in one invocation.
  The installer preflights every target, stages an undo journal before the
  first generated-file write, rolls back ordinary failures, and resumes an
  interrupted rollback or committed cleanup on the next same-target run.
  Recovery refuses post-interruption user edits and damaged backups. Fault-
  injection tests cover a failing second target, process interruption, and
  cleanup interruption. `--recover-only` works without GitHub access.
  Per-file replacement is atomic; simultaneous readers are not promised an
  instantaneous multi-file snapshot.

## 6.5.2 — 2026-10-13 (candidate)

- Corrected the retired-artifact audit to ignore tracked paths already deleted
  from the working tree but not yet staged. Such paths are not retained local
  copies; a migration can now be audited before staging its cleanup commit.

## 6.5.1 — 2026-10-13 (candidate)

- Closed a project-adoption audit blind spot: short retired `SOUL.md` and
  `SOULv2.0.0.md` files, pre-pack `SOUL.md`/`AGENTS.md` backups, and explicit
  claims that SOUL remains active law now produce findings. This prevents a
  false clean result after only the primary project pointer is migrated.

## 6.5.0 — 2026-10-12 (candidate)

- Separated inventory traversal completion from coverage. Final schema-3
  reports classify each named root as scanned, partial, or inaccessible and
  disclose the scanner's no-link policy. A scan with access errors still
  preserves its report but exits 2 with `INCOMPLETE COVERAGE`, rather than
  printing a misleading `PASS`. Existing schema-1 checkpoints remain
  resumable; older schema-2 reports remain readable with their errors treated
  as coverage gaps.

## 6.4.1 — 2026-10-12 (candidate)

- Corrected resumable inventory validation for multiple Windows drive roots.
  A queued directory on `D:` or `E:` now continues past a nonmatching `C:`
  root; an out-of-root or link-escaped frontier is still rejected. Added a
  cross-drive regression test so a long scan's checkpoint remains usable.

## 6.4.0 — 2026-10-12 (candidate)

- The local copy inventory now checkpoints completed directories atomically,
  prints progress, and resumes only with matching scan parameters. Interrupted
  scans cannot publish a partial final report or silently overwrite a prior
  report. The retained checkpoint and final `status: complete` distinguish
  recovery state from a completed inventory.

## 6.3.1 — 2026-10-12 (candidate)

- The project adoption audit now rejects GitHub workflow checkouts of the
  canonical repository without a literal 40-character commit pin and detects
  floating `main`/`master` raw-source URLs in workflows. This closes an SSOT
  drift path while leaving ordinary documentation links untouched.
- Documented the audit's static limit: dynamic source fetches and acceptance
  of a syntactically pinned SHA still require human/source verification.

## 6.3.0 — 2026-10-12 (candidate)

- Added protected `CONST-CRAFT-001` against AI slop across code, documents,
  designs, data, and media. Purpose-fit, substantive content, delivered-form
  inspection, and an independent or human review oracle are now explicit
  before a Done claim; superficial polish and volume cannot substitute.
- Connected the rule to the quality profile, Section 0 gate, source validator,
  and regression test without adding a parallel rule home.

## 6.2.1 — 2026-10-12

- Strengthened the read-only project adoption audit to identify old
  browser-stored SOUL text used as a live model system prompt, even when the
  old file is no longer present. Precisely marked, commit-pinned historical
  recovery instructions remain allowed so cleanup does not erase the
  rollback path.

## 6.2.0 — 2026-10-12

- Ported the useful, still-unmerged runtime integrity safeguards from legacy
  PR #10 into current one-home law: generated-content capacity and fallback,
  serialized/declarative asset closure, low-level lifecycle paths, mutable
  hot-path caches, intrusive diagnostic hygiene, and defensible performance
  attribution. These are scoped obligations, not a return to the 5.x loader.
- Clarified that a build, synthetic fixture, selected profiler stack, source
  package, or benchmark cannot stand in for the actual runtime consumer.

## 6.1.0 — 2026-10-12

- Added an end-to-end evidence-integrity profile: verify generated API claims
  against the installed stack, inspect test and CI diffs before trusting green
  status, reproduce review findings, recheck context after compaction, and
  withhold Done when a necessary independent oracle is unavailable. The
  profile scales depth to risk but explicitly forbids shortcuts.
- Added a read-only adoption audit for stale project consumers of vendored law
  (CI, manifests, scripts, UI, and full SOUL copies), distinguishing the
  canonical repository's legacy URL slug from the retired skill name.
- Require consumer and pinned-CI migration before declaring a project copy
  retired; this makes source provenance part of the same evidence chain.

## 6.0.0 — 2026-10-11

- Renamed the active law and loader **WPAI Constitution**; one repository
  snapshot now contains both skill and binding law.
- Consolidated the modular 5.1 pack and SOUL's 40 topics into a short root,
  scoped law files, one rule registry, and a ten-stage SOP.
- Kept the 15-point gate, intended-behavior tests, zero-warning standard,
  human authority, quality ceiling, frozen invocation, and meaningful
  evolution requirement; added exact evidence-stage language.
- Added a source-disposition record and recoverable migration gates instead
  of publishing private project copies or deleting unresolved variants.
- Changed mirror sync to a same-SHA file manifest with hashes and generated-
  file-only pruning; a legacy mirror is not silently overwritten or pruned.

## 5.2.5 — 2026-09-22

- Explicit pack-root validation and separation of canonical skill source from
  the old local binding pack. Historical 5.x detail remains in Git history.
