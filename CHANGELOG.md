# Changelog

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
