# Changelog

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
