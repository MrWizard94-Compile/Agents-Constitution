# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-09-21 — Resolve packs one directory inside walk siblings

**Observed issue:** `resolve-pack.ps1` only tested the walk directory and its direct siblings. A valid pack at `C:\WPAI\AGENTS Constitution` was invisible from a user-profile workspace, so Step 0 exited 1 even though the pack was present.

**Meaningful improvement:** the resolver now also tests one directory level inside each sibling, and Step 0 says that is required. Direct sibling packs still win because they are tested first.

**Future failure reduced:** an agent is less likely to stop and ask for a pack path when the pack sits one folder below a drive-level studio directory.

**Changed paths:** `scripts/resolve-pack.ps1`, `SKILL.md`.

**Validation target:** `scripts/resolve-pack.ps1 -StartPath` from a profile path whose sibling-of-parent contains the pack one level down, exit 0. `python tools/validate-source.py`.

## 2026-09-15 — Prune leftover vendored files on generated-mirror sync

**Observed issue:** overlaying the GitHub skill onto Codex left the old 5.0.1 pack tree under `references/` (`AGENTS.md`, modules, templates, `gate_check.py`). Those leftovers could still be read as law even after `SKILL.md` pointed at GitHub.

**Meaningful improvement:** both sync adapters now delete files that are not in the canonical generated-mirror set, after confirming the target is an `agents-constitution` skill directory. Optional `references/pack-root.local` is preserved.

**Future failure reduced:** replacing a vendored agent skill with the GitHub mirror is less likely to leave a second, stale constitution beside the generated files.

**Changed paths:** `distribution/sync.py`, `distribution/sync.ps1`, `SKILL.md`.

**Validation target:** `python tools/validate-source.py` and GitHub Actions `Validate Canonical Skill Source` must pass on the evolution PR.

## 2026-09-14 — Grok default mirrors and GitHub-only skill pointers

**Observed issue:** the Grok install at `~/.grok/skills/agents-constitution` stayed on the old 5.0.1 host-local pack pin because `distribution/sync.ps1` defaulted only to Codex, `sync.py` required explicit targets, and `SOURCE.json` / `SKILL.md` skill versions lagged `VERSION`.

**Meaningful improvement:** default generated-mirror paths now live in `SOURCE.json` and include Grok and Codex; both sync adapters use those defaults; validators require the GitHub pointer, version alignment, and those default paths; pack discovery no longer keys off a host folder name.

**Future failure reduced:** a Grok or Codex agent is less likely to keep enforcing a stale local skill while GitHub `main` moves, and less likely to treat a host folder as skill source.

**Changed paths:** `SKILL.md`, `SOURCE.json`, `distribution/sync.py`, `distribution/sync.ps1`, `tools/validate-source.py`, `references/always-load.md`, `references/pack-root.local.example`, `docs/ARCHITECTURE.md`.

**Validation target:** `python tools/validate-source.py` and GitHub Actions `Validate Canonical Skill Source` must pass on the evolution PR.

## 2026-09-14 — Canonical source, frozen invocation revision, and mandatory meaningful evolution

**Observed issue:** the skill previously existed as local/project copies, which allowed drift between agents and workflows. A mandatory self-update rule also creates two failure modes unless bounded: an agent could recursively trigger infinite updates, or could rewrite its own governing rules mid-invocation.

**Meaningful improvement:** centralized the source skill in this repository; added canonical-source enforcement, per-invocation revision freezing, next-invocation activation, a one-evolution-per-top-level-invocation boundary, non-regression requirements, and explicit anti-churn criteria for what qualifies as meaningful.

**Future failure reduced:** agents are less likely to diverge, silently skip evolution, manufacture fake changes, recurse indefinitely, or change the rules by which their current work is judged.

**Changed paths:** `SKILL.md`, `SOURCE.json`, `scripts/resolve-pack.ps1`, `references/*`, `evolution/LEDGER.md`, distribution and validation tooling.

**Validation target:** canonical-source validator, sync dry-run, GitHub PR review, and pack verification where the local pack is available.

## 2026-09-14 — Markdown-reflow-tolerant invariant validation

**Observed issue:** the first live CI run failed even though the required quality-ceiling invariant was present. The validator searched for literal contiguous whitespace, while normal Markdown wrapping split `highest quality reasonably achievable` across a newline.

**Meaningful improvement:** canonical invariant validation now case-folds and normalizes all prose whitespace before semantic phrase checks. Formatting/reflow can change without creating a false constitutional failure, while removal of the invariant still fails validation.

**Future failure reduced:** agents and formatters can reflow canonical Markdown without breaking CI for presentation-only reasons, so validation failures more accurately indicate semantic drift rather than line wrapping.

**Changed path:** `tools/validate-source.py`.

**Validation:** GitHub Actions `Validate Canonical Skill Source` must pass on the evolution PR and again after merge.
