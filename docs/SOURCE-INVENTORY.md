# Consolidation record and historical-source disposition

**Inventory basis:** Local read-only scan dated 2026-09-22 of three mounted
volumes. It examined 4,500,215 files and returned 3,628 broad candidate hits
and 535 access errors, mostly protected directories. Candidate hits include
false positives; this is **not** a claim that every hit is a Constitution copy
or that inaccessible paths were inspected. Exact paths and machine-specific
metadata stay in the ignored local inventory, not this public repository.
That scan predates filename detection for pre-pack backups whose bodies lack
the scanner's markers; it cannot prove those variants absent. A new bounded
scan is required before their physical cleanup.

## Distinct source families

| Source family | Representative SHA-256 | Disposition |
|---|---|---|
| Original short `SOUL.md` instruction | Historical text in user-provided project guidance | Completeness, warnings, testing, research, stack, code quality, docs, performance, security, refactor, communication, and workflow live in `AGENTS.md`, `SOP.md`, and `law/*`. |
| 40-section SOUL v2, archived monolith | `31fd3feeffa6985e18de6ea340cd9b92bb32fd5e1abba5c5038e647f81850aa0` | Generalized into the current rule homes; no active monolith copy. |
| Workspace SOUL v2 formatting variant | `edb6ed67c578056b84fba5f5870213db44521a4c438270c27030b5ec38efdeb7` | Keep as historical evidence until distinct wording is fully reconciled. |
| Downloaded SOUL v2 formatting variant | `d2514d62b8d482610c30110867015e2758c5de99933f91744b1c4510ce8d58fd` | Same treatment; not a source of live law. |
| Project SOUL v2 variants | `4914a973dba8279d3040937b31db296cedba33981d8eae7587f963f479b7454a`, `eb7e72518df0dd3015989f1b1d1a4c9bddac2a1054feb4a0efd585fe1ed87a89` | Preserve project-specific intent in project law; migrate universal requirements to one canonical home. |
| Modular AGENTS Constitution 5.1 pack | Preserved in its tracked Git history and duplicate pack copies | Retained rule families, 15-point gate, and SOP; simplified into five scoped law files. Retired IDs map in `governance/RULE-REGISTRY.md`. |
| GitHub skill 5.2.5 | Prior canonical Git commits | Freeze, one meaningful change per call, anti-churn, quality ceiling, and third-party runtime fixture closure are retained and generalized. |
| Legacy skill proposals (PRs #5, #7, #9, #10 at inventory time) | GitHub PR history | On 2026-10-12, #5 was closed as incorporated under `TEST-DOMAIN-001`; #7 and #9 were closed as superseded by one verified source snapshot. #10 was closed after its distinct runtime-consumer safeguards were ported into reviewable PR #13. The original branches and PR history remain recoverable. Do not merge a 5.x loader or resolver into 6.x merely to clear a conflict. |
| Small `SOUL.md` pointers and generated skill mirrors | Exact paths and hashes in local inventory | Replace with pointers or regenerated verified mirrors, never edit as independent law. |

Token-level comparisons against the archived v2 monolith found 99.1–99.5%
sequence similarity across the representative variants. The material
differences were moving or omitting the Rule of Three and one variant omitting
a chat-silence instruction. The Rule of Three is retained in `ENG-CODE-001`;
the chat-silence wording is not binding because it conflicts with current
interaction requirements. Large line-diff counts were mostly Markdown
wrapping. A further copy-level audit is still required before physical
deletion. This document deliberately does not copy private project text or
name private project folders in the public repository.

## Topic crosswalk

| Historical topics | Active home |
|---|---|
| Identity, human authority, completeness, conflict, gate, Done | `AGENTS.md` |
| Research-to-delivery stages and quality ceiling | `SOP.md`, `SKILL.md` |
| Engineering, tests, documentation, performance, dependencies | `law/ENGINEERING.md` |
| Security, secrets, observability, privacy | `law/SECURITY.md` |
| Version control, migration, project lifecycle, release | `law/OPERATIONS.md` |
| Review, multi-agent work, context, institutional memory | `law/COLLABORATION.md` |
| Novel R&D, IP, networking, low-level, constrained resources | `law/SPECIALIST.md` |
| Source, lock, integrity, evolution, mirrors, archives | `governance/EVOLUTION.md` |

## Cleanup gates

1. Classify each candidate as unique source, tracked project copy, generated
   mirror, pointer, cache, or unrelated false positive. Confirm exact path,
   hash, owner repository, dirty state, and whether a symlink or worktree is
   involved. Re-scan paths before mutation because the inventory is dated.
2. Publish and verify accepted canonical `main`; install a complete new mirror
   and verify its manifest. Update project pointers in their own Git roots.
3. Preserve unique project clauses locally. Move old full packs and historical
   SOUL texts to recoverable archives only after their semantic differences
   are accounted for. Do not recursively delete broad folders or follow links.
4. Record every cleaned path, recovery location, and residual inaccessible or
   unresolved item in a local, non-public cleanup manifest. Repeat a bounded
   scan to verify the active set has one source and no silent shadow law.

## External design inputs

The local instruction-file model follows the [agents.md convention](https://github.com/agentsmd/agents.md)
and the official [GitHub Copilot custom-instructions documentation](https://docs.github.com/en/copilot/reference/custom-instructions-support):
project files are useful entry points but do not themselves guarantee loading
across products. The [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
informs risk-proportional verification, and [SLSA provenance](https://slsa.dev/spec/v1.2/provenance)
informs source-SHA and artifact-provenance separation. [SemVer](https://semver.org/)
and [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) inform human-readable
change records. These are design inputs, not a substitute for this project's
explicit authority and acceptance rules.
