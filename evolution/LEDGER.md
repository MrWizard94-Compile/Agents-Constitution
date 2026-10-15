# Evolution Ledger

The ledger is evidence of evolution. A ledger entry, version bump, changelog edit, or formatting-only diff never counts as the meaningful improvement by itself.

## 2026-10-15 — Reject linked ancestor routes in adoption evidence

**Observed gap:** a controlled Git fixture replaced a tracked directory with
a Windows junction. The adoption checker read external Markdown through that
parent because its link check covered only the final file. It also returned
a clean result for an ordinary leaf symlink and accepted a linked Git root.
Three new regression cases failed against the accepted baseline.

**Meaningful change:** the checker inspects candidate components outermost-first
and reports the first link or reparse point once, without reading descendants.
It rejects linked root routes in both modes and retains name-only findings for
retired leaf artifacts. The documentation explicitly limits this read-only
audit to a quiescent tree, not race-free isolation from hostile writers.

**Falsification:** real Windows junction/POSIX symlink fixtures must block
content reads through tracked parents (including absent descendants), return
a nonzero CLI status, preserve external bytes, and reject root aliases.
Clean files and unstaged tracked deletions must retain their prior behavior.
A metadata-order assertion fails if any component beneath a known link is
queried. No binding-law or authority change is needed.

## 2026-10-14 — Budget the actual host-plus-provider system

**Observed gap:** the installed WPAI neural-context provider returned a warm
query quickly, but the user-facing Obsidian vault remained at “Loading vault”
on a workspace with roughly 1.58 million files. A provider-only latency test
could misleadingly mark the integrated neural workspace as accepted.

**Meaningful change:** `PERF-BUDGET-001` now requires a representative corpus
and file-type scope, cold time to a usable host, steady-state behavior, and
peak aggregate resource use across required host and provider processes.
Reversible configuration trials must disclose hidden content and be restored
if ineffective; live host and agent acceptance remain separate from query QA.

**Review oracle:** on the intended corpus, a fast warm provider response with
an unusable or over-budget host must leave acceptance open. An effective
scope reduction must show the host and agent flow working and name hidden
content; an ineffective reduction must be restored. The rule is wrong if it
requires measuring irrelevant processes or treats every large corpus as a
failure without an actual resource or usability limit.

## 2026-10-14 — Require generated artifacts to be discoverable by their consumer

**Observed gap:** a valid WPAI neural-vault Canvas was first exported below
`Software/obsidian-mcp-server/data`, while the vault's `.obsidianignore`
excluded that entire project. The exporter succeeded and JSON Canvas tests
passed, but Obsidian could not discover the view. A second export had to be
placed under a non-ignored vault directory. Native UI acceptance is still open
because Obsidian remained at its loading screen.

**Meaningful change:** `ENG-FW-001` now makes the consumer's discovery boundary
part of generated-artifact correctness. Agents must preflight the destination
against roots, exclusions, registration, and packaged paths; reject hidden or
unsafe destinations and distinguish successful export from consumer visibility.
The skill points to that single rule home.

**Review oracle:** a generated view aimed below an ignored path, outside the
consumer root, or through a linked directory must fail before writing. A valid
path must be observed through the installed consumer before live acceptance.
This rule is wrong if it treats file existence or schema validity as proof of
visibility, or forces an unavailable consumer to be described as accepted.

## 2026-10-14 — Preserve every supported relationship representation in derived context

**Observed gap:** the WPAI vault resolver accepted Markdown links, but its
graph included only wiki links. On the real vault, correcting the omission
raised resolved links from 86 to 2,715 and reduced notes without incoming
links from 2,150 to 1,268. A plausible graph and passing parser checks had
concealed materially false context and orphan statistics.

**Meaningful change:** `ENG-FW-001` now requires every supported relationship
representation to reach each derived consumer that claims that relationship,
with provenance separating authored from inferred edges. Intentional
exclusions must be visible rather than misreported as absence. The skill
points callers to the existing rule home.

**Review oracle:** a Markdown-only or other single-representation fixture
must yield the expected consumer edge, backlink, count, and provenance; an
excluded form must be disclosed. This rule is falsified if the parser succeeds
but the installed graph or visual silently omits that fixture, or if it
requires a consumer to include relationships outside its declared scope.

## 2026-10-14 — Make externally mutable context indexes honest about freshness

**Observed gap:** a live vault MCP context provider reported a deleted
temporary checkout as an indexed note and then failed its stats call with
`ENOENT`. The provider's own writes invalidated its cache, but external
filesystem changes did not. Source tests had missed the installed stdio
consumer path.

**Meaningful change:** `ENG-FW-001` now requires a documented bounded
freshness contract for agent-facing indexes, immediate invalidation on owned
writes, detection of external removals before claiming cached links or paths
are current, and an explicit retry or incomplete result on stale-path
failure. It requires create/edit/delete and installed-consumer tests plus a
refresh-cost measurement. The skill points callers to that one rule home.

**Review oracle:** after an external deletion, an installed context provider
must not return a supposedly current link to the removed file or crash on a
stale path; after an addition or edit it must expose the change within its
declared bound or after refresh. A representative workspace measurement must
make the cost of that guarantee visible. The rule is wrong if it requires an
unbounded scan for each small read or treats a source-only unit test as live
acceptance.

## 2026-10-14 — Audit ignored non-Git project directories without false clean claims

**Observed gap:** the adoption checker required an exact Git root. An ignored
local MCP project had a migrated pointer and live route, but its parent
repository tracked none of its source. The checker refused the project path;
auditing the parent would omit the project's first-party files and built
response. No static adoption result could be claimed for that directory.

**Meaningful change:** `check-adoption.py --filesystem` explicitly scans the
named directory without Git, including built output and ignored first-party
files. It skips only named dependency caches and returns unresolved findings
for linked paths and nested repositories; an entry limit or read failure
aborts without a pass. The default Git-root mode is unchanged. `MIG-CLEAN-001`
and the skill route non-Git projects to the exact-directory mode instead of
the parent repository.

**Review oracle:** a fixture ignored by its parent must reveal old-pack text
in source and built files, while the default mode must reject the child.
Linked and nested repository paths must not be followed or silently passed;
the limit must error. The real local MCP project currently produces specific
historical/fixture reference findings, not a misleading clean result.

## 2026-10-14 — Verify live agent-onboarding routes during adoption

**Observed gap:** a local read-only WPAI intake tool still emitted a directive
to load the retired pack after the root entry and canonical skill had moved to
GitHub. Its source tests and build passed because they checked only document
discovery, not the emitted constitutional route. The existing adoption audit
could not inspect a long-running tool process.

**Meaningful change:** `MIG-CLEAN-001` now includes agent hooks and tool-provided
onboarding output among old-pack consumers. An adoption must inspect the
installed entry point's actual response after restart, or report live
acceptance open when restart is unavailable. The skill and cleanup gate link
to that same operational rule; they do not establish another law home.

**Review oracle:** a fixture or live tool that still tells an agent to load
the retired pack after source migration disproves adoption. A passing source
test with a stale pre-restart process is insufficient. The local intake
consumer's regression test asserts the canonical route and a missing-root
negative path; a newly built process is probed separately.

## 2026-10-14 — Find ignored and filename-only residual law before cleanup

**Observed gap:** the dated all-drive report omitted two ignored root pre-pack
SOUL variants whose exact names carried the only scanner signal. Separately,
the project adoption audit excluded ignored `.agents` and `.claude` trees,
reporting their retired pointers and backups only when a separate manual check
was performed. A clean adoption result or zero inventory hit was therefore
too weak to justify deletion or a no-shadow-law claim.

**Meaningful change:** inventory recognizes `SOUL.md` and `AGENTS.md`
`legacy-pre-pack-*` filenames independent of content. Adoption inspects the
root and four known agent-config directories for retired SOUL names, backups,
instruction loaders, and old pack directories, including when Git ignores
them. It does not crawl arbitrary ignored dependency trees or follow links;
linked agent directories produce an explicit unresolved finding.

**Review oracle:** fixtures with ignored `.agents` SOUL, `.claude` backup,
`.codex` SOUL variant, `.grok` pack, ignored old-pack loader, and a linked
agent directory must fail the adoption audit, while an ignored
`node_modules/SOUL.md` stays outside the bounded scope. A filename-only
backup must appear in a fresh inventory. The old dated report remains an
incomplete historical snapshot, not rewritten.

## 2026-10-14 — Require linkage-complete class-transform caches

**Observed gap:** a warm class-transform cache stored an outer class that
named a mixin anonymous class defined only while the transform ran, and
stored a separate caller of a method that existed only on that cached outer
class. Treating the outer class as a miss, while leaving the caller cached,
made the recomputed outer class disagree with the caller (`NoSuchMethodError`).
Returning the outer bytes without defining the anonymous class failed later
with `NoClassDefFoundError`. `COST-CACHE-001` concerns an agent's notes, not
this bytecode cache, so it did not forbid the split.

**Meaningful change:** `LOW-CACHE-001` requires a hit either to define that
side-effect dependency before the hit is returned, or to miss together with
the cached caller. Identity entries and unrelated contexts stay valid. The
source validator fails if the operational wording is removed.

**Review oracle:** a cache test that returns the outer hit and leaves the
caller cached, with the dependency still undefined, violates the rule. A
validator fixture that deletes "cached caller" from `law/SPECIALIST.md`
must fail. If a later call treats a one-sided miss as a complete fix, this
change failed.

## 2026-10-14 — Correct the ruleset audit's missing-evidence outcome

**Observed gap:** a GitHub response without `bypass_actors` cannot establish
whether the approved ruleset has a bypass, yet the v6.8.0 audit described the
missing field as policy drift. Public unauthenticated responses omit it.

**Meaningful correction:** the live audit now reports `UNVERIFIED` and exits 2
before making a policy claim when the field is absent or redacted. CLI-level
tests cover an API outage, redaction, real bypass drift, and a clean result.

**Review oracle:** a redacted fixture must never return drift or pass, while a
present nonempty bypass list must return drift and an authenticated empty list
must pass. Network failure must remain unverified.

## 2026-10-14 — Detect canonical repository protection drift

**Observed gap:** the Constitution requires PR review and green validation, but
the canonical `main` branch had no active GitHub ruleset. A repository setting
can later change without a source diff, and source validation cannot see it.

**Meaningful change:** `tools/check-repository-ruleset.py` reads the authenticated
repository ruleset and effective branch rules, and checks the approved active
policy: PRs, strict GitHub Actions `validate`, no review approvals or bypass
actors, and no force-push or branch deletion. It distinguishes drift from an
unverified API read. The tool is distributed with the source so future calls
can check the external control without modifying repository settings.

**Review oracle:** an approved live ruleset passes; fixtures with an added
bypass actor, required approval, unexpected unattributed-change approval,
wrong branch, loose status gate, incorrect check-source app, or missing
effective rule fail. An outage must produce `UNVERIFIED`, never `PASS`.
The source suite remains network-free.

## 2026-10-13 — Verify the frozen load and disclose loader drift

**Observed gap:** during a 2026-10-13 call the running loader was v6.5.0 while
accepted `main` was v6.6.1. Nothing said which `SKILL.md` governs or required
the mismatch to be disclosed. The same call first read binding law through a
summarizing web-page reader whose output looked verbatim; the step "read from
that same revision" did not require exact bytes, so a faithful read could not
be told apart from a paraphrase or truncation.

**Meaningful change:** GOV-FREEZE-001 now requires byte-exact reads (a checkout
confirmed by the new `tools/check-frozen-load.py`, or a hash-verified sync),
treats summarized readers as orientation with an "unverified" handoff, and
makes the frozen `SKILL.md` govern when the running loader's `skill-version`
differs, with both versions disclosed. The tool checks full-SHA HEAD, an
unmodified tracked tree, and raw git-blob hashes for every `SOURCE.json`
binding file (catching edits that `git status` cannot see, such as
skip-worktree files), and compares versions numerically (6.10.0 is newer than
6.9.0). `tools/validate-source.py` guards the contract text.

**Review oracle:** a clean checkout passes; a different HEAD, a short or branch
ref, a modified tracked file, a modified skip-worktree file, and a manifest
file missing from the revision each fail; a 6.5.0 loader against 6.6.1 reports
`STALE LOADER` without failing integrity. If a later call relies on summarized
law without the unverified disclosure, or ignores reported loader drift, this
change failed.

## 2026-10-13 — Exclude concurrent mirror writers during recovery

**Observed gap:** the v6.6.0 undo journal made interruption recoverable, but
another sync process could misidentify an active batch as crashed and begin
rollback. Locking only the journal coordinator would not protect overlapping
batches whose target order differed.

**Meaningful change:** sync and offline recovery acquire non-blocking,
process-owned locks for every target in stable path order before inspecting
transaction state. A contending run fails without changing generated files.
The stable empty lock file remains after exit so a new process cannot lock a
different inode while another still uses the old one. Unknown nonempty and
symlinked lock files are preserved and rejected.

**Review oracle:** hold two targets in a separate process and attempt an
overlapping batch in a different order; both install and recovery must fail
without a manifest or journal change, and a retry must work after the holder
is terminated. Existing interruption and rollback tests must continue passing.

## 2026-10-13 — Recover interrupted generated-mirror installations

**Observed gap:** `distribution/sync.py` wrote generated files one at a time
and its provenance manifest last. A write failure or interruption could leave
one mirror internally mixed; a failure in the second target could also leave
the first mirror updated while the second remained old.

**Meaningful change:** preflight all targets, stage their original bytes in a
single batch undo journal, and restore all targets on ordinary failure. A
subsequent run with the same ordered targets rolls back an uncommitted
interruption or finishes cleanup of a fully verified committed batch. Any
unexpected user edit or damaged backup stops recovery rather than overwriting
data. `--recover-only` allows that recovery without GitHub access. The
installer still preserves unknown files and refuses dirty generated files.
This is recoverable installation, not instantaneous multi-file reads.

**Review oracle:** injected failures in the second mirror and during journal
preparation must leave old manifests and content intact; simulated process
interruption must recover on retry; a post-interruption user edit must remain
untouched; and interruption after commit must finalize without rollback.

## 2026-10-13 — Correct the retired-artifact audit during migration

**Observed gap:** the v6.5.1 path check classified OmniFix's deleted but
unstaged `SOUL.md` and pre-pack backup paths as retained artifacts, because
`git ls-files --cached` still listed those index entries. The files were
already absent from the working tree.

**Meaningful correction:** skip a cached path when it no longer exists,
while retaining checks for live files and symlinks. This repairs the same
adoption-integrity change so projects can verify cleanup before staging.

**Review oracle:** a fixture with a tracked then deleted `SOUL.md` must
produce no finding before `git add -u`; a live retired pointer and backup
must still fail. OmniFix's unstaged migration should then pass static audit.

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
