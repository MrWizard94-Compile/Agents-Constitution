# Changelog

## 5.2.3 — 2026-09-15

- Generated-mirror sync now removes leftover files from older vendored skill installs.
- Preserves only the canonical mirror file set plus optional host-local `references/pack-root.local`.
- Prevents stale pack copies under `references/` from remaining as shadow law after a GitHub overlay.

## 5.2.2 — 2026-09-14

- Declared default generated-mirror install paths in `SOURCE.json`, including Grok and Codex.
- Sync adapters now use those defaults instead of a Codex-only hardcoded target.
- Aligned `SOURCE.json` / `SKILL.md` skill version with `VERSION`.
- Skill and always-load pointers name the GitHub repository as the only skill source.
- Validator requires the GitHub pointer, matching skill versions, and Grok/Codex default mirror paths.
- Removed host-folder name bias from pack discovery and the pack-root example.

## 5.2.1 — 2026-09-14

- Fixed canonical invariant validation to normalize Markdown whitespace before semantic phrase checks.
- Prevents false CI failures when normal line wrapping splits a required invariant across lines.
- Keeps semantic removal detectable while allowing harmless reflow/formatting changes.

## 5.2.0 — 2026-09-14

- Established `MrWizard94-Compile/Agents-Constitution` as the only editable source of the `agents-constitution` skill.
- Corrected the skill's Constitution pack pin from 5.0.1 to the current 5.1.0 baseline.
- Added mandatory meaningful per-invocation skill evolution.
- Added anti-churn criteria so version/ledger/formatting-only edits do not satisfy evolution.
- Added immutable per-invocation revision freezing and next-invocation activation.
- Added a one-evolution-per-top-level-invocation boundary to prevent recursive self-update loops.
- Added the quality-ceiling rule: do not knowingly reserve already-achievable in-scope polish for a later pass when final/professional quality is requested.
- Added portable generated-mirror sync adapters for PowerShell and Python.
- Hardened sync to resolve a branch/tag once to an immutable commit before downloading any file, preventing mixed-revision installs if `main` moves mid-sync.
- Added canonical source validation and CI evolution enforcement.
