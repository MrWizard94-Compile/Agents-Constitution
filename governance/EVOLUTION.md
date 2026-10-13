# Constitutional evolution and single source of truth

**Version:** 1.0.0

**Authority:** `AGENTS.md`
**Canonical repository:** `MrWizard94-Compile/Agents-Constitution`

## GOV-SSOT-001 — One editable source

The accepted `main` branch of the canonical GitHub repository owns the
skill, law, process, templates, and verification tools. Each accepted commit
is a complete, immutable source snapshot. Generated installs, project
pointers, caches, local clones, tags, and archives may distribute or refer
to that snapshot; they do not acquire authority by being nearby.

## GOV-FREEZE-001 — A frozen invocation

At a top-level skill call, resolve and record a full commit SHA of accepted
`main`. Validate it. That revision governs the entire call. An amendment
authored during the call does not change its own gate or authorize itself.
The change becomes eligible only on a later call after acceptance on
`main`. If GitHub is unavailable, a previously verified mirror may be
used with a visible degraded-sync note.

## GOV-EVOLVE-001 — One meaningful improvement per call

Every top-level use of the `wpai-constitution` skill MUST author one
coherent, meaningfully useful Constitution change. Related file edits form
one change; unrelated changes do not become a bundle merely to meet a
count. The evolution step does not recursively create another obligation.

A qualifying change must reduce an identified future failure, ambiguity,
inefficiency, validation weakness, security risk, or quality gap. The agent
must state the observed problem, exact changed behavior, and a test or
review oracle that could show the improvement was wrong. Version bumps,
timestamps, ledger-only entries, changelog-only entries, renames without
semantic effect, duplicate rules, and cosmetic formatting do not qualify.

The standing requirement to evolve does not expand authorization for an
unrelated user task. If publication or canonical write is unavailable,
produce a complete, validated apply-ready patch or PR and mark the
evolution **staged, not propagated**. Do not claim the canonical
Constitution changed. A task-specific read-only instruction still controls
that task.

## GOV-RATCHET-001 — Safety and quality

An improvement must preserve or strengthen safety, human authority,
correctness, security, completeness, evidence truthfulness, and protected
rules. First look for an existing canonical rule and edit it there; avoid
adding a second home or a narrow rule for a one-off incident. Generalize
only from evidence, and use risk-proportional wording.

## GOV-CHANGE-001 — Review and acceptance

1. Branch from the latest accepted `main` and check its current SHA.
2. Write one coherent change and update the version, changelog, ledger,
   registry, and migration notes only where needed.
3. Run `python -m unittest discover -s tests -v` and
   `python tools/validate-source.py`; test the new behavior directly.
4. Inspect the full diff for secrets, private data, broken links,
   conflicting rules, and unrelated changes.
5. Commit and push an isolated branch; open a pull request.
6. A protected-invariant, authority, public exposure, or major
   architectural change requires explicit Human Director review before
   merge. Routine skill/tool improvements may merge under existing
   authorization when checks pass and no protected rule changes.
7. Verify accepted `main`, then sync generated mirrors from that SHA.

Do not race direct writes to `main`, force-push accepted history, silently
rewrite a release tag, or merge while a required check is red. If `main`
moves, reconcile the branch and rerun validation.

## GOV-MIRROR-001 — Distribution

A mirror records canonical repository, source SHA, version, and a manifest
of generated files. Sync downloads all files from one resolved SHA, preflights
every target, replaces individual files atomically, and validates before
declaring success. A batch undo journal permits rollback after a failed or
interrupted install; it does not make the multi-file view instantaneous to
concurrent readers. Prune only previously identified generated files.
Preserve local user data and unknown files.
The old `agents-constitution` install is a compatibility entry only until
the new skill is installed and verified; retire it through a recorded,
recoverable migration.

## GOV-ARCHIVE-001 — Historical sources

The source inventory identifies SOUL, SOUL v2, modular AGENTS Constitution,
skill revisions, project variants, and open proposals by path, hash, and
disposition. Preserve unique meaning in active law. Keep public history
free of private project data; record a checksum and private location
instead of publishing private content. Historical text is not active law.

## Versioning

The pack and skill share one SemVer `VERSION`. A major release changes a
binding contract or migration path; a minor release adds compatible
capability; a patch fixes behavior without weakening the contract. Git tags
are immutable. The ledger records why a change matters, but the actual
substantive diff is the evidence of evolution.
