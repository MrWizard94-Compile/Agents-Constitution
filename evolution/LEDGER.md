# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-10-12 — Trace quality claims to source and independent evidence

**Observed gap:** plausible generated code, green test badges, polished review
findings, and a canonical pointer can all be false assurance. An agent could
reference an invented API, weaken tests, repeat a phantom finding, drift after
compaction, or leave CI and a UI consuming an obsolete vendored pack while
reporting a high-quality result.

**Meaningful change:** the SOP now starts with a risk-scaled quality profile
and requires independent evidence for consequential claims; relevant law
requires installed-version API checks, test/gate diff review, reproduced
review findings, context reconciliation, least privilege, and outage
checkpoints. `MIG-CLEAN-001` closes the source end of this evidence chain with
a consumer sweep and pinned canonical CI source. The read-only
`tools/check-adoption.py` checks project files and full SOUL copies without
confusing the unchanged GitHub repository URL with the retired skill name.

**Future failure reduced:** agents are less likely to present an apparently
clean but unverified result, silently skip a required acceptance check, retain
shadow law, or break quality gates while removing a duplicate pack.

**Review oracle:** a fixture with a vendored folder or stale CI command must
fail; a pointer containing only the canonical repository URL must pass. In a
project review, an invented API, hidden test skip, unreproduced finding, or
missing required live flow must prevent a Done claim even if formatting and
unit tests are green. If the profile permits such a claim, this amendment
failed its purpose.

## 2026-10-11 — Bind skill and law to one verified snapshot

**Observed gap:** the old canonical skill was current while the binding pack
could be resolved from a separate, stale local folder. A sync could also
prune unknown files in a legacy install, making cleanup difficult to audit.

**Meaningful change:** the WPAI Constitution skill loads the law from the
same frozen GitHub commit as its loader. `SOURCE.json` declares the full
mirror file set. Sync records hashes and prunes only previously generated
files. A project pointer adds local facts without becoming another law copy.

**Future failure reduced:** a fresh skill cannot silently enforce an older
pack, and mirror refresh cannot delete untracked user files as collateral.

**Review oracle:** reject a mirror that omits a binding law file, combines
revisions, has a mismatched hash, or prunes an unknown file; verify the
invocation continues under its original commit after proposing an amendment.

## 2026-09-22 — Explicit PACK_ROOT validation cannot silently fall through

**Meaningful improvement:** `resolve-pack.ps1` now validates a human-specified
`-RequestedPackRoot` (or `-PackRoot`) and explicit root environment variables as
binding law packs, reporting exactly which required files or gate marker are
missing. The skill instructions distinguish a canonical skill-source checkout
from a valid law pack and require clarification when an explicit root is invalid.

**Future failure reduced:** an agent is less likely to silently apply law from a
different local pack when the user explicitly requested an isolated checkout
that contains skill source but no binding pack files.

**Changed paths:** `SKILL.md`, `scripts/resolve-pack.ps1`, `VERSION`,
`SOURCE.json`, `CHANGELOG.md`, `evolution/LEDGER.md`.

**Validation target:** canonical source validation plus resolver checks for a
valid explicit fixture, invalid explicit fixture, and invalid explicit env root.

## 2026-09-16 — Runtime fixture dependency-closure preflight

**Observed issue:** a third-party mod fixture had two independent missing runtime dependencies, followed by a later secondary exception. File installation and a catalog rescan could have been mistaken for a complete repair even though no clean relaunch had occurred.

**Meaningful improvement:** enforce-mode delivery now inventories declared and nested runtime dependencies, requires authoritative artifacts and integrity evidence, validates the repaired third-party fixture before adding the product under test, separates primary load failures from cascade errors, and withholds runtime acceptance until a clean relaunch and behavior flow pass.

**Future failure reduced:** agents are less likely to blame the final crash line, install an incomplete dependency set, attribute a pre-existing bundle failure to their product, or report a dependency copy as a verified runtime repair.

**Changed paths:** `SKILL.md`, `VERSION`, `SOURCE.json`, `tools/validate-source.py`, `evolution/LEDGER.md`.

**Validation target:** `python tools/validate-source.py`, pack full self-run against an isolated pack copy, and GitHub Actions `Validate Canonical Skill Source` must pass on the evolution PR.

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
