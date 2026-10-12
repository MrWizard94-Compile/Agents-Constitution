# Changelog

## 6.1.0 — 2026-10-12 (candidate)

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
