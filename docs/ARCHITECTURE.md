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
meaningful change in the single authorized review slot; validation and review precede
acceptance. The new rule is eligible only on a later invocation. This avoids
self-amendment and concurrent writes to `main`. Version, ledger, and
changelog support traceability but never count as the substantive change.
The frozen revision is read byte-exact (`tools/check-frozen-load.py`), and a
running loader that differs from it is disclosed, not obeyed.

Branch history is not a branch backlog. `main` and the optional serial
`codex/constitution-review` slot are the only allowed remote names. Completed
branches are retired; unique pending work retains exact patches or verified
private recovery. `evolution/proposals` records decisions and historical
patches outside generated law mirrors. Only the accepted current canonical
homes define active law. The per-call evolution requirement
can produce a complete queued patch while the shared review slot is occupied.

The repository cannot force every AI platform to auto-load a skill. Local
agents must install or sync the mirror through their supported mechanism;
other agents may read the repository directly. A GitHub commit, local mirror,
project adoption, and successful runtime use are separate acceptance gates.

`SOP-EXEC-001` owns a mandatory workflow for every mode. Its ten stages share
one run record that survives continuation, tracks acceptance and reopens
affected gates after change. The loader and project pointer route into that
single process; domain laws supply checks, not competing workflows.

Enforcement has distinct layers: source guards protect the published contract;
the task-record checker rejects missing or internally inconsistent evidence;
observed agent trials test actual choices; host permission controls constrain
actions. None substitutes for the others. A record checker never grants
permission or authenticates its evidence. A host adapter must be tested through
its installed entry and actual action boundary before claiming enforcement.
This source does not install such an adapter or claim universal client control.

Historical SOUL and AGENTS copies are cataloged in `docs/SOURCE-INVENTORY.md`.
Their unique requirements are mapped into active law, or marked as
project-specific/archival. The archive is evidence, not a second source.
