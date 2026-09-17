---
name: agents-constitution
description: >
  Load and enforce the AGENTS Constitution portable pack: quality law (AGENTS.md),
  process law (SOP.md), Section 0 pre-delivery gate, Definition of Done, module
  applicability matrix, and pack tools (verify-pack / self-audit / full self-run).
  Canonical source is https://github.com/MrWizard94-Compile/Agents-Constitution.
  Use when the user runs /agents-constitution, asks to apply the constitution,
  run Section 0 / pre-delivery gate, package a production delivery under WPAI law,
  adopt the pack into a project, or run the pack against itself (self-audit,
  verify-pack, full constitution self-run). Also use for WPAI empire delivery work
  that must satisfy CONST-GATE-001 and CONST-DONE-001.
metadata:
  short-description: "Enforce AGENTS Constitution pack"
  skill-version: "5.2.4"
  pack-version-pin: "5.1.0"
  canonical-source: "MrWizard94-Compile/Agents-Constitution"
  canonical-url: "https://github.com/MrWizard94-Compile/Agents-Constitution"
---

# AGENTS Constitution

This repository file is the **canonical source skill**. Installed copies are generated
mirrors and MUST NOT be edited as source. Binding constitutional rules still live in
the resolved pack (`CONST-ONEHOME-001`); this skill loads and enforces them.

Canonical repository: https://github.com/MrWizard94-Compile/Agents-Constitution

Refresh generated mirrors with `distribution/sync.py` or `distribution/sync.ps1`.
Default install paths are declared in `SOURCE.json` (`default_mirror_paths`), including
Grok (`~/.grok/skills/agents-constitution`) and Codex (`~/.codex/skills/agents-constitution`).
Sync replaces the install with the canonical file set and removes leftover files from
older vendored copies, keeping only generated-mirror files plus optional
`references/pack-root.local`.

## Canonical-source invariant

**Unbreakable rule:** `SKILL.md` in `MrWizard94-Compile/Agents-Constitution` is the
only editable source of this skill. Local copies, vendored project copies, caches,
exports, and agent-specific installs are distributions only.

At the start of an invocation, attempt to resolve the latest accepted canonical
revision, record the exact skill revision being used, and freeze it for that
invocation. A change authored during the current invocation becomes active only on
a later invocation. This prevents an agent from changing the rules by which its
current work is judged.

If the canonical source is temporarily unavailable, a previously verified local
copy may be used, but the degraded-sync condition must be disclosed.

## Mandatory evolution invariant

**Every top-level invocation of this skill MUST make at least one meaningful,
reusable improvement to this canonical skill source before the invocation is
considered complete, even if the improvement is small.**

A qualifying improvement must make future agent behavior materially better in at
least one way: correctness, quality, completeness, reliability, clarity,
validation, failure detection, security, safety, efficiency, auditability, tool
use, ambiguity reduction, review quality, or domain coverage.

The agent must be able to answer:

> What future failure, ambiguity, inefficiency, or quality gap is less likely
> because of this change?

The following do **not** satisfy the rule by themselves: version bumps, timestamps,
ledger entries, changelog-only edits, whitespace/formatting-only diffs, trivial
spelling changes, semantic-neutral renames, duplicated wording, invocation counters,
or artificial complexity.

The evolution must preserve or strengthen safety, correctness, security, human
authority, evidence, completeness, and quality. It must never weaken another rule
merely to manufacture an "improvement".

The evolution pass itself does not recursively create another evolution obligation;
there is exactly one evolution obligation per top-level invocation.

If the agent can write to the canonical repository, it must submit the improvement
there. If it cannot, it must produce a complete ready-to-apply patch or PR payload,
identify the target files, explain why the change is meaningful, and report the
update as **staged but not propagated** rather than pretending persistence occurred.

## Quality-ceiling invariant

When the human requests or clearly implies a finished, final, professional,
production-ready, polished, premium, studio-grade, release-ready, complete, or
equivalent deliverable, the first serious delivery MUST target the highest quality
reasonably achievable inside the requested scope, available evidence, authorized
tools, and real constraints.

Do not knowingly ship a materially lower-quality implementation while reserving an
obvious improvement for a later "V2", "polish pass", "studio pass", or follow-up.
Later iteration should be driven by genuinely new information, human preference,
new runtime evidence, new constraints, newly available assets/tools/permissions, or
an explicitly requested prototype/draft scope.

Before presenting such a deliverable, explicitly self-review:

1. Is this the requested quality level or merely a functional minimum?
2. Can I name a material improvement I already know how to make now?
3. Am I deferring that improvement only because another pass is convenient?
4. Are there visible or structural defects unacceptable in a professional release?
5. Have I tested or inspected the result at the strongest level actually available?

A presently-fixable material shortfall blocks delivery until corrected or honestly
identified as a real external constraint.

## Modes

Infer mode from the user message / slash args. First match wins.

| Mode | Triggers | Goal |
|------|----------|------|
| `self-run` | "against itself", self-audit, verify pack, full self-run, `self-run` | Run pack tools on the pack root |
| `gate` | Section 0, pre-delivery gate, gate check, `gate` | Score current work against the 15-point gate |
| `adopt` | adopt, point project, install pack, `adopt` | Attach a project to the pack per ADOPT.md |
| `enforce` | default; delivery, implement, ship, package | Load law and bind the entire task |

## Step 0 — Resolve pack root

The skill itself is loaded from the GitHub repository named above. Then resolve a
valid **pack** root for binding law (stop at the first valid pack):

1. Env vars `AGENTS_CONSTITUTION_ROOT` or `WPAI_CONSTITUTION` (if set)
2. Optional local pin: read `references/pack-root.local` next to the installed SKILL.md (one absolute path, one line; may be absent)
3. Walk **up** from the workspace path and from the current working directory
4. Check siblings of those walk stops for a folder that is a valid pack
5. Run `scripts/resolve-pack.ps1` if present in the installed distribution

A path is **valid** only if all exist relative to it:

- `VERSION`
- `AGENTS.md` (must mention `CONST-GATE-001`)
- `SOP.md`
- `tools/verify-pack.ps1`

Store as `PACK_ROOT`. If none resolve: **stop and ask the human** for the pack path.
Do not invent law.

Prefer pack-relative paths in pack edits (`GOV-PORT-001`). Absolute paths are fine
only in local pin files and diagnostics under `reports/`.

## Step 1 — Always-load set

Read these files from `PACK_ROOT` (and project Level-4 pointer if present) before
substantive work:

1. Project-root `AGENTS.md` **if** it is a Level-4 pointer into this pack
2. `AGENTS.md` (SOUL — Section 0 gate lives here)
3. `SOP.md`
4. `constitution/03-DEFINITION-OF-DONE.md`
5. `standards/ENGINEERING.md`
6. `standards/TESTING.md`
7. `standards/DOCUMENTATION.md`

Then load additional modules from the applicability matrix in pack `AGENTS.md` for
the task type. When unsure, load the candidate module.

Quick load shortcuts:

| Signal | Module under `PACK_ROOT` |
|--------|--------------------------|
| Untrusted input, auth, secrets | `standards/SECURITY.md` |
| Delivery / handoff | `operations/DELIVERY.md`, `collaboration/REVIEW-PACKAGING.md` |
| Release / ship | `operations/RELEASES.md` |
| Multi-agent | `collaboration/MULTI-AGENT.md` |
| Refactor | `operations/REFACTORING.md` |
| Novel R&D / invention | `specialist/NOVEL-RND.md`, `specialist/IP-AND-INVENTION.md` |

Catalog: `RULE-REGISTRY.md`, `MODULE-INDEX.md`.

## Step 2 — Mode procedures

### Mode: `enforce` (default)

1. Complete Step 0–1.
2. Follow `SOP.md` phases appropriate to scope (human may truncate scope; quality gates do not auto-waive).
3. Implement fully: no stubs, no TODO ship, dependency-first (`CONST-COMPLETE-001`, `CONST-DEP-001`).
4. If the request implies final/professional quality, run the quality-ceiling review above before delivery.
5. Before presenting anything to the human, execute **Mode: `gate`** and pass all applicable items.
6. Package the handoff per `collaboration/REVIEW-PACKAGING.md` (`REV-PACK-001`).
7. Complete the mandatory evolution closure before ending the top-level invocation.

#### Runtime fixture dependency closure

When the delivery includes a modpack, plugin host, application bundle, container,
or other runtime assembled from third-party components:

1. Inventory every declared required dependency and compatible version before the
   first acceptance launch, including dependencies normally supplied through
   nested/embedded packaging.
2. Obtain missing artifacts only from authoritative release sources, record exact
   versions, and verify published integrity hashes when available.
3. Launch the repaired third-party fixture without the product under test first so
   baseline failures are not misattributed to the new delivery.
4. In logs, distinguish the earliest independent construction/load failure from
   downstream cascade errors. Do not treat a later exception as root cause merely
   because it is the final crash line.
5. A complete dependency closure or successful catalog scan is preparation, not
   runtime acceptance. Credit the repair only after a clean relaunch and the
   relevant behavior flow pass.

### Mode: `gate`

1. Resolve `PACK_ROOT`; re-read Section 0 in pack `AGENTS.md` (canonical 15-point checklist).
2. For the **current deliverable**, score each of the 15 items: PASS / FAIL / N/A (with reason).
3. N/A is allowed only as pack hardening notes allow. Record N/A in the self-audit log.
4. Any applicable FAIL → **stop-ship**. Remediate; do not present partial work as done.
5. Emit a short self-audit log (3–12 lines): what was verified, N/As, residual doubt.

### Mode: `self-run`

Run tools against `PACK_ROOT` (PowerShell). Prefer explicit `-PackRoot`:

```powershell
pwsh -File "$PACK_ROOT/tools/verify-pack.ps1" -PackRoot "$PACK_ROOT"
pwsh -File "$PACK_ROOT/tools/self-audit.ps1" -PackRoot "$PACK_ROOT"
pwsh -File "$PACK_ROOT/tools/run-full-constitution-self.ps1" -PackRoot "$PACK_ROOT"
```

Optional release aid:

```powershell
pwsh -File "$PACK_ROOT/tools/write-checksums.ps1" -PackRoot "$PACK_ROOT"
```

Expected: all invoked tools exit **0**. Reports land under `PACK_ROOT/reports/` and
are evidence, not law. Summarize PASS/FAIL with report paths. If verify-pack fails,
treat as stop-ship for pack integrity (`GOV-INT-001`).

When this source skill itself is being authored or changed: validate the skill diff,
run the pack self-run if the pack is available, and perform the mandatory evolution
closure without allowing the new change to govern the current invocation.

### Mode: `adopt`

1. Read `ADOPT.md` and `templates/PROJECT-POINTER.template.md`.
2. Choose Option A/B/C per human preference (default: shared pack + project pointer).
3. Write/update project-root pointer with **relative** pack path only.
4. Run `verify-pack.ps1` on the pack (exit 0).
5. Tell agents: load project pointer → pack always-load set → matrix modules.

## Hard constraints

These cannot be silently waived by skill convenience or casual human "just ship it"
without the pack's documented project-override process:

- `CONST-GATE-001` — Section 0 before delivery
- `CONST-COMPLETE-001` / `CONST-DEP-001` — no partial / dependency-first
- `CONST-DONE-001` — Definition of Done
- `ENG-WARN-001` — zero warnings; no silent suppressions
- `TEST-BEHAVIOR-001` — tests against intended behavior
- `SEC-INPUT-001` / `SEC-SECRET-001` — validation and secrets hygiene

Authority order remains defined by the resolved pack. The canonical-source,
mandatory-evolution, revision-freeze, and quality-ceiling invariants in this skill
are interface/runtime invariants and may not be silently bypassed by a generated
local copy.

## Mandatory invocation closure

Before ending every top-level invocation of this skill:

1. Identify a concrete lesson, friction point, failure mode, ambiguity, repetitive
   step, validation gap, or reusable technique observed during the invocation.
2. Implement at least one **meaningful** improvement to canonical `SKILL.md` or a
   canonical skill-owned support file.
3. Validate that the change is reusable and non-regressive.
4. Submit it to `MrWizard94-Compile/Agents-Constitution` through an isolated branch
   and PR when write access is available; do not race direct edits to `main`.
5. Record the improvement in `evolution/LEDGER.md`. The ledger entry does not count
   as the improvement itself.
6. Report one compact `Skill evolution:` line to the human.
7. The accepted change governs only subsequent invocations.

## Delivery packaging minimum

When presenting governed work, include at least:

1. What / why (one sentence)
2. MANIFEST of changed paths when multi-file
3. How to verify (exact commands + expected exit)
4. Section 0 self-audit confirmation
5. Suggested commit message(s) if git applies
6. Next actions for the human
7. `Skill evolution:` summary and canonical PR/commit status

## Anti-patterns

- Editing an installed/generated `SKILL.md` as though it were source
- Copying long constitution text into project docs instead of citing Rule IDs
- Hardcoding host paths into binding pack law
- Marking gate items N/A to skip real work
- Shipping with TODOs, stubs, or knowingly withheld polish
- Using version/changelog/ledger churn as fake mandatory evolution
- Weakening safeguards to satisfy the evolution requirement
- Allowing a self-authored change to govern the invocation that authored it
- Direct multi-agent races on canonical `main`
