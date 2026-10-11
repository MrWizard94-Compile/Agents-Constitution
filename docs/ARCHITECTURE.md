# WPAI Constitution architecture

The canonical GitHub repository's accepted `main` is the only editable law
source. A full commit SHA identifies an immutable snapshot. `SKILL.md`
loads `AGENTS.md`, `SOP.md`, governance, and applicable `law/*` from that
snapshot. Project pointers supply project-specific facts. Generated Codex,
Grok, or other installs carry a source SHA and file hashes, not authority.

```text
accepted main commit
  ├─ SKILL.md + SOURCE.json     loader and distribution manifest
  ├─ AGENTS.md + SOP.md         quality law and operating process
  ├─ law/*                      one canonical home per active rule
  ├─ governance/*               amendment and registry
  └─ generated mirrors          pinned, validated distributions
        └─ project pointers     mission, stack, acceptance; never law fork
```

The source freezes at invocation start. An agent proposes one coherent,
meaningful change on an isolated branch; validation and review precede
acceptance. The new rule is eligible only on a later invocation. This avoids
self-amendment and concurrent writes to `main`. Version, ledger, and
changelog support traceability but never count as the substantive change.

The repository cannot force every AI platform to auto-load a skill. Local
agents must install or sync the mirror through their supported mechanism;
other agents may read the repository directly. A GitHub commit, local mirror,
project adoption, and successful runtime use are separate acceptance gates.

Historical SOUL and AGENTS copies are cataloged in `docs/SOURCE-INVENTORY.md`.
Their unique requirements are mapped into active law, or marked as
project-specific/archival. The archive is evidence, not a second source.
