# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-10-13 — Detect retired law artifacts after project pointer migration

**Observed gap:** OmniFix retained short `SOUL.md` pointers, tracked
`*.legacy-pre-pack-*` law backups, and documents still calling SOUL active
law. The v6.5.0 adoption audit missed these artifacts and declarations after
the primary pointers were changed, so it could falsely report a clean
project while shadow law remained in the working tree.

**Meaningful change:** the read-only audit now flags exact retired SOUL
filenames, known pre-pack backup filenames, and explicit active-law claims.
It still leaves historical prose and product terms alone. This is one
adoption-integrity improvement, not a new constitutional rule.

**Future failure reduced:** a project migration cannot pass the static
adoption check merely by replacing its main entry points while retaining
old law artifacts or declaring them binding elsewhere.

**Review oracle:** a fixture with short pointers and pre-pack backups must
produce path findings, and `Law: SOUL.md` must produce an active-law finding.
Historical text saying the old copy is not active law must not be classified
as active. After OmniFix migration, the audit must be clean without deleting
any unreconciled source; Git history must retain recovery.

## 2026-10-12 — Make inventory coverage failures impossible to mistake for a pass

**Observed gap:** the completed C:/D:/E: inventory examined 4,804,532 files
and retained 130 access errors, including denial at the D: root. The scanner
still printed `PASS`, exited 0, and wrote `status: complete`. That status
correctly described traversal termination but could be misread as evidence
that all named roots were inspected before cleanup.

**Meaningful change:** a final report now separately states coverage and
classifies each named root as scanned, partial, or inaccessible. The command
preserves a useful report when errors occur, but prints `INCOMPLETE COVERAGE`
and exits 2. No-root invocations are rejected. Checkpoint schema and
cross-drive resume remain compatible; skipped links are explicitly outside
the reported traversal scope.

**Future failure reduced:** a denied drive or protected subtree cannot yield
a green inventory command or an unqualified absence claim just because the
scanner finished attempting traversal.

**Review oracle:** with one readable root and one root whose `scandir` fails,
the report must keep both results, label the denied root `inaccessible`, and
the CLI must exit 2. A fully readable fixture must exit 0; an empty default
root set must not create a report. Resume tests must still pass. A live
all-drive scan would still require review of access errors, excluded links,
and candidate ownership before any physical cleanup claim.

## 2026-10-12 — Resume a checkpoint across Windows drive roots

**Observed gap:** a real `C:\`, `D:\`, `E:\` copy inventory saved 94,000
completed directories, but `--resume` failed with `Paths don't have the same
drive` while checking the pending frontier against the first nonmatching root.
The checkpoint was intact; restarting the all-drive scan would waste work and
weaken cleanup evidence.

**Meaningful change:** each pending path is checked against the named roots
independently. A cross-drive comparison is a nonmatch, not an abort. Resume
also resolves parent links before containment checking and rejects relative or
out-of-root frontier entries.

**Future failure reduced:** interrupted multi-volume inventories recover from
their checkpoint without repeating completed traversal or relaxing the
frontier's filesystem boundary.

**Review oracle:** simulate a Windows cross-drive `commonpath` error for the
first root with a pending path under the second. Resume must complete; an
outside or link-escaped path must still fail. Then resume the real retained
checkpoint and inspect the final report and access-error count.

## 2026-10-12 — Make PC copy inventory resumable and completion-safe

**Observed gap:** an all-drive inventory that examined millions of files
ended without a final report. The old scanner wrote only at the end, so an
interruption discarded its evidence and could encourage cleanup from a stale
or incomplete snapshot.

**Meaningful change:** the scanner now commits progress after fully inspected
directories to an atomic checkpoint, reports file/directory/hit/error counts,
and resumes only when roots, output, and text-size settings match. It refuses
to overwrite an existing final report and writes one only after traversal
finishes. The checkpoint remains for recovery and the final report identifies
itself as complete.

**Future failure reduced:** a long PC scan can recover from interruption without
repeating completed directories or misrepresenting partial output as a
complete inventory.

**Review oracle:** interrupt a nested scan after a checkpoint: no final report
must exist, resume must produce the same hit set and file count as an
uninterrupted scan, and changed parameters or a frontier outside the requested
roots must be rejected. Access errors and intentionally skipped links remain
explicit limitations, not proof of absence.

## 2026-10-12 — Reject floating constitutional source in project CI

**Observed gap:** a migrated project could pass the old-copy audit while its
CI fetched `MrWizard94-Compile/Agents-Constitution` from a floating branch.
The governing source could change between otherwise identical project builds,
undermining the frozen-invocation and one-SSOT contract.

**Meaningful change:** `tools/check-adoption.py` now inspects GitHub workflow
steps for literal canonical-repository checkouts and fails when the same step
lacks a full commit SHA. It also flags floating `main`/`master` canonical raw
URLs in workflows. Tests cover an unrelated sibling-step pin, a genuine pin,
and a documentation link that must remain permissible.

**Future failure reduced:** project adoption CI cannot silently track a moving
constitutional branch while claiming a reproducible, validated law snapshot.

**Review oracle:** an unpinned canonical checkout or raw `main` URL must fail;
a same-step 40-hex ref must pass, while an unrelated step's ref must not rescue
the unpinned checkout. The static check cannot prove that a full SHA is an
accepted `main` commit or detect every dynamic fetch, so source validation and
manual CI review remain necessary.

## 2026-10-12 — Require purpose-fit substance in every agent artifact

**Observed gap:** completeness, zero warnings, test evidence, and a quality
profile can still yield a superficially polished artifact that misses the
director's actual brief, contains invented details, or pads the delivery with
generic filler. The existing rules do not explicitly reject this failure
across creative and non-code media as well as software.

**Meaningful change:** protected `CONST-CRAFT-001` defines AI slop as a
purpose-fit and substance defect, requires review of the delivered form and
material claims against the brief, and ties consequential claims to an
independent oracle. It distinguishes a review-ready artifact from one the
director has accepted when taste or lived use is decisive. The Section 0 gate,
SOP, and quality map reference this one canonical home.

**Future failure reduced:** agents are less likely to trade working substance
for plausible prose, ornament, volume, or invented specificity, or to claim
human acceptance from their own self-review.

**Review oracle:** give an agent a brief for a functioning UI and a beautiful
but nonfunctional mockup, or a source-constrained report with a plausible
invented fact. In either case it must withhold Done and name the failed
real-use or independent-source check. For a subjective media brief, it must
deliver an inspectable asset and call it review-ready until the director's
feedback is incorporated. The validator test guards the clause's core
operational wording but does not claim to evaluate artistic merit.

## 2026-10-12 — Detect active browser-stored shadow law

**Observed gap:** a project could delete its full SOUL file yet still read a
browser-stored `soul_config` value into a model's system prompt. The existing
adoption audit saw the old filename but missed this live consumer. Conversely,
an exact Git-history recovery instruction was reported as a live reference.

**Meaningful change:** `tools/check-adoption.py` now fails on a direct legacy
storage read in a JavaScript/TypeScript prompt-consuming module. It permits a
narrowly labeled, full-commit Git recovery instruction in Markdown while
continuing to flag ordinary legacy references. Browser data may be preserved
for export without remaining active agent law.

**Future failure reduced:** a migration cannot pass merely by removing the
tracked monolith while a local runtime keeps enforcing it; projects also
retain a precise rollback path without hiding active consumers.

**Review oracle:** a fixture with `localStorage.getItem('soul_config')` and a
system prompt in the same module must fail, while an inert export helper and
explicit commit-pinned historical recovery line pass. This static check does
not prove absence of indirect data flow; consumer review and runtime testing
remain required.

## 2026-10-12 — Close runtime claims against the actual consumer

**Observed gap:** legacy PR #10 recorded several real failure modes, but it
targeted the retired 5.x skill architecture and conflicted with accepted 6.x
`main`. The 6.1 law retained its lifecycle and diagnostic principles while
omitting concrete capacity/fallback, serialized and declarative asset,
mutable-cache, sample-attribution, and indivisible-work checks. Closing the
old PR without porting those would lose useful quality protections.

**Meaningful change:** the existing engineering, security, and specialist
homes now require exact-version consumer limits and fallback semantics,
minimal digest-guarded asset repair, real packaged and lifecycle behavior,
mutation-complete cache invalidation, sample and workload attribution, and
capture-specific safeguards. The skill points to those homes rather than
copying a large case-specific checklist into its root.

**Future failure reduced:** an agent is less likely to ship a serializable but
unusable conversion, dead lifecycle hook, stale cache, content-deleting warning
fix, unsupported optimization claim, or intrusive diagnostic leak while
calling source QA runtime acceptance.

**Review oracle:** in a representative fixture, boundary inputs must preserve
the converter's original fallback and load in the actual consumer; a rebuild
must invalidate a cache without changing equality semantics; normal exit and
re-entry must execute a low-level hook; and a truncated profiler stack must
remain unattributed. If the rule text permits a Done claim from only unit
tests, package parsing, or selected samples in those cases, this port is
insufficient. Source validation and unit tests protect structure, not these
runtime truths.

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
