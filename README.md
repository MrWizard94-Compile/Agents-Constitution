# AGENTS Constitution

Canonical source repository for the AGENTS Constitution governance pack and the `agents-constitution` skill.

This repository is the **only editable source of truth**. Local installations, caches, vendored project copies, and release archives are generated distributions.

## Core invariants

- `main` is accepted canonical source.
- Versioned tags/releases are immutable distribution points.
- A governed invocation resolves and freezes one verified revision before substantive work.
- Every top-level invocation of the skill must produce at least one **meaningful, reusable improvement** to the canonical skill package.
- Version/changelog/ledger-only churn does **not** count as meaningful evolution.
- An invocation cannot use a change it authored during that same invocation to rewrite the rules governing itself; accepted evolution becomes active on a later invocation.
- Concurrent agents evolve through isolated branches/pull requests rather than racing direct writes to `main`.
- Binding-law changes remain human-controlled; operational skill improvements may be automated after validation.

The canonical pack, skill source, validation tooling, distribution adapters, and evolution ledger will live together here so improvements can propagate across agents and workflows without local-source drift.
