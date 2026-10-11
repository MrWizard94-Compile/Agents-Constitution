# Version control, migration, release, and cleanup

**Status:** Binding for repository mutation, migration, refactor, release,
deployment, project lifecycle, or destructive cleanup.

## Change control

### VCS-ATOMIC-001 — Coherent commits

Use intention-revealing commits that leave their affected tree buildable.
Stage exact paths, inspect the staged diff, and keep unrelated user changes
out of the commit. Do not treat the workspace root as one monorepo when
projects have independent Git roots.

### VCS-MSG-001 — Explain the intent

Commit messages describe what changed and why. Include relevant verification
and known risk in the handoff or PR.

### VCS-CLEAN-001 — No residue

Keep temporary files, caches, generated reports, credentials, and backup
artifacts out of release commits unless they are intentionally versioned
evidence. Inspect the package before publication.

### VCS-HISTORY-001 — Preserve history

No reset, rebase, force-push, squash, or replacement of shared or unrelated
history without explicit direction. Preserve dirty worktrees and unpublished
commits. Use isolated branches and recoverable checkpoints for large changes.

## Refactor and migration

### REF-PLAN-001 — Plan broad refactors

Map components, contracts, rollback, compatibility, migration, and tests
before a cross-cutting change. Keep the plan short enough to be useful.

### REF-GREEN-001 — Working checkpoints

Keep each logical checkpoint buildable with clean affected tests and
analysis. After a broad refactor, verify core runtime flows and update
documentation.

### REF-SAFE-001 — Observable behavior

Preserve behavior unless the director requests a deliberate change.
Compatibility adapters, feature flags, and parallel paths are tools when
they reduce actual migration risk; do not add them as permanent complexity.

### MIG-INV-001 — Inventory before replacing

List old and new APIs, data, behavioral differences, consumers, source
copies, and ownership. Record hashes and provenance for duplicate copies.
Classify each as canonical, active project law, generated mirror, historical
archive, transient cache, or unresolved. Never delete an unresolved copy.

### MIG-FEEL-001 — Preserve the experience

Port the intended semantics, performance profile, and user or player feel.
Document and test intentional divergences.

### MIG-NOTES-001 — Decision record

Maintain a concise source-linked mapping of old to new behavior, remaining
risks, rollback, and acceptance gates. Do not leave silent migration debt.

### MIG-VERIFY-001 — Core flow first

A clean build is preparation. Exercise the core user/runtime flow before
secondary polish and before claiming the migration accepted.

### MIG-CLEAN-001 — Recoverable cleanup

Resolve exact paths and ownership before a move or delete. Preserve unique
content in the canonical history or a recoverable archive. For a tracked
project copy, update its pointer and verify behavior before removing the old
pack. Do not follow links or recursively delete a broad workspace target.
Record what was removed and how to recover it.

## Delivery and release

### OPS-DEL-001 — Complete package

Deliver complete files or an apply-ready package. Check for broken links,
missing imports, unmanaged prerequisites, and temporary residue.

### OPS-DEL-002 — Full replacements when useful

Prefer complete file replacements in human copy/paste handoffs. Tool-driven
patches are acceptable when the final tree is complete and reviewable.

### REL-PACKAGE-001 — Release contents

When a release is requested, include version, changelog, build command,
artifact, checksum or signature, installation/upgrade instructions,
compatibility, rollback, and known limitations.

### REL-DETERM-001 — Reproducible artifacts

Record source SHA and environment. Compare output hashes across clean builds
when deterministic release artifacts are claimed. A checksum of one build
proves identity of that artifact, not reproducibility.

### REL-UPGRADE-001 — Upgrade path

Document data and configuration migration, breaking changes, downgrade
limits, and backup/rollback. Test retained state when updating in place.

### REL-HARDEN-001 — Pre-ship evidence

Resolve critical security and quality findings. Source QA, release
packaging, deployment, live runtime, and physical acceptance have separate
gates and must be reported separately.

## Project lifecycle

### LIFE-PHASE-001 — Respect maturity

An explicitly scoped spike is not production. Growth requires stable
contracts and tests; maintenance protects compatibility; archive/deprecation
requires a clear stop-use marker and recovery path.

### LIFE-NODEAD-001 — No abandoned half-state

Keep active projects healthy, or archive them cleanly. Report a blocked
project honestly rather than calling partial QA complete.

### LIFE-TOOL-001 — Developer setup

Prefer free, open, offline-capable and reproducible tools when feasible.
Document setup and verification so a fresh maintainer can reproduce the
development environment.
