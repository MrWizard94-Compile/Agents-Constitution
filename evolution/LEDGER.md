# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-09-25 — Isolate third-party performance trials from unrelated repairs

**Observed issue:** a modpack profile needed a settled-world control before a separately approved world-generation optimizer trial. While the user launched that control, an unrelated but real claim-provider configuration mismatch was discovered. Applying both changes together would make the optimizer's effect impossible to attribute.

**Meaningful improvement:** runtime performance guidance now requires exact baseline versions and configuration, a one-component trial, deferred unrelated fixes, artifact identity and rollback checks, and no mutation of live runtime files.

**Future failure reduced:** agents are less likely to conflate two valid changes in an A/B test, install an unverified component, or corrupt a running instance while trying to improve performance.

**Changed paths:** `SKILL.md`, `evolution/LEDGER.md`. This extends the open canonical-source PR; the accepted rules frozen for this invocation remain unchanged.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, pack full self-run, and canonical-source CI on the PR.

## 2026-09-25 — Attribute runtime lag using comparable windows

**Observed issue:** a Minecraft integrated-server log reported a 20-second backlog during a 90-second recording. Initially calling it one 20-second stall overstated the evidence: short individual parks, short GC pauses, and simultaneous terrain/render-worker saturation required a different interpretation. Container-opening samples were mixed with new-world generation.

**Meaningful improvement:** enforce-mode guidance now requires time-aligned log, action, and trace evidence; distinguishes accumulated backlog from one blocking call and sampled frames from wall time; separates startup, generation, settled, and interaction windows; and requires an equivalent-workload comparison before crediting an optimization.

**Future failure reduced:** agents are less likely to change a container or GC path because of a misleading backlog line while the actual workload is competing terrain generation and rendering.

**Changed paths:** `SKILL.md`, `evolution/LEDGER.md`. This extends the open canonical-source PR; the accepted rules frozen for this invocation remain unchanged.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, pack full self-run, and canonical-source CI on the PR.

## 2026-09-25 — Close binary fixture repairs against packaged and live content

**Observed issue:** a missing item reported during Minecraft world generation came from two mirrored serialized copies inside one compressed structure template, not from a text recipe. Dropping the structure would hide the error but lose content; changing only one copy would leave the toolbox inconsistent.

**Meaningful improvement:** enforce-mode guidance now requires exact archive-entry tracing, complete mirrored-field inspection, original-payload digest, minimal approved decoded diff, replacement availability, loader-precedence and packaged-byte checks, and a live behavior gate.

**Future failure reduced:** agents are less likely to silence a binary-content warning by deleting a whole feature, ship a partial serialized edit, trust the wrong resource priority, or confuse source validity with in-game generation.

**Changed paths:** `SKILL.md`, `evolution/LEDGER.md`. This extends the open canonical-source PR; the accepted rules frozen for this invocation remain unchanged.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, pack full self-run, and canonical-source CI on the PR.

## 2026-09-25 — Compare exact classes at equivalent memory lifecycle points

**Observed issue:** a modpack world-exit histogram search matched synthetic and lambda class names as well as the intended world classes, producing noisy truncated output. A corrected exact-class comparison showed no retained world objects after two exits, while the prior version retained servers, worlds, a player, and chunks. That result still did not prove all heap growth was gone.

**Meaningful improvement:** the diagnostic hygiene guidance now requires equivalent lifecycle points, exact histogram class matching, scoped conclusions about cleared object roots, and a normal re-entry check after cleanup.

**Future failure reduced:** agents are less likely to mistake noisy substring hits for retained objects, compare incomparable captures, declare an entire runtime leak-free from a few absent classes, or break the next session while clearing caches.

**Changed paths:** `SKILL.md`, `evolution/LEDGER.md`. This extends the open canonical-source PR without changing the frozen accepted rules for this invocation.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, and canonical-source CI on the PR.

## 2026-09-25 — Handle intrusive diagnostic artifacts without leaking credentials or exhausting disk

**Observed issue:** a modpack memory investigation required a 6.35 GiB heap dump and generated large analysis indexes, leaving little free disk. A process-inspection output also exposed a launcher command line containing a session token even though only the game PID was needed.

**Meaningful improvement:** enforce-mode guidance now requires a least-intrusive evidence choice, capture-specific approval and storage budgeting, process identification without command-line or environment disclosure, local review of sensitive artifacts before publication, and explicit authority before deleting material diagnostics.

**Future failure reduced:** agents are less likely to expose live credentials, fill a user's drive, treat a transient observation failure as a stopped runtime, or delete evidence while trying to recover space.

**Changed paths:** `SKILL.md`, `evolution/LEDGER.md`. This extends the open 5.2.5 source-validation PR; the previously proposed version and metadata bump remain unchanged.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, and the PR's canonical-source CI.

## 2026-09-24 — Verify low-level lifecycle call paths before installation

**Observed issue:** a Minecraft NeoForge client-memory repair compiled and passed helper tests but targeted `setLevel(null)`. The actual normal disconnect and client-level teardown paths assign the level field directly and call a different shared method, so the repair would have missed the user-visible exit flow.

**Meaningful improvement:** enforce-mode guidance now requires exact-version call-path inspection, argument and ordering verification, a versioned contract test where practical, and separate runtime exit/re-entry evidence for low-level lifecycle hooks.

**Future failure reduced:** agents are less likely to ship a Mixin that targets a real method yet never executes on the relevant lifecycle path, or to mistake compilation for a verified teardown fix.

**Changed paths:** `SKILL.md`, `VERSION`, `SOURCE.json`, `evolution/LEDGER.md`.

**Validation target:** `python tools/validate-source.py`, `python tools/evolution-guard.py --base <main commit>`, and GitHub Actions `Validate Canonical Skill Source` on the PR.

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
