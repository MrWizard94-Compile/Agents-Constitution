# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-09-14 — Canonical source, frozen invocation revision, and mandatory meaningful evolution

**Observed issue:** the skill previously existed as local/project copies, which allowed drift between agents and workflows. A mandatory self-update rule also creates two failure modes unless bounded: an agent could recursively trigger infinite updates, or could rewrite its own governing rules mid-invocation.

**Meaningful improvement:** centralized the source skill in this repository; added canonical-source enforcement, per-invocation revision freezing, next-invocation activation, a one-evolution-per-top-level-invocation boundary, non-regression requirements, and explicit anti-churn criteria for what qualifies as meaningful.

**Future failure reduced:** agents are less likely to diverge, silently skip evolution, manufacture fake changes, recurse indefinitely, or change the rules by which their current work is judged.

**Changed paths:** `SKILL.md`, `SOURCE.json`, `scripts/resolve-pack.ps1`, `references/*`, `evolution/LEDGER.md`, distribution and validation tooling.

**Validation target:** canonical-source validator, sync dry-run, GitHub PR review, and pack verification where the local pack is available.
