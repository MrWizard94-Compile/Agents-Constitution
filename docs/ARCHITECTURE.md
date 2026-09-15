# Canonical Source and Propagation Architecture

## Authority model

`MrWizard94-Compile/Agents-Constitution` is the only editable source for the
`agents-constitution` skill.

Canonical URL: https://github.com/MrWizard94-Compile/Agents-Constitution

- `main` = accepted canonical source.
- A commit SHA = exact source revision.
- A tag/release = immutable distribution point.
- Local agent skill folders = generated mirrors.
- Vendored project copies = generated snapshots.

Local copies are never promoted to source by editing them. Persistent changes flow
back through this repository.

## Invocation lifecycle

1. Resolve the latest authorized canonical revision for the configured channel.
2. Verify source invariants and provenance.
3. Record the exact revision/version.
4. Freeze that revision for the entire top-level invocation.
5. Load the AGENTS Constitution pack and perform governed work.
6. If professional/final quality is implied, perform the quality-ceiling review.
7. Derive one meaningful reusable skill improvement from the invocation.
8. Submit that candidate on an isolated branch/PR.
9. Update the evolution ledger and version as evidence, not as the qualifying change.
10. Validate the candidate.
11. Merge accepted source.
12. Other agents receive it on their next sync/invocation.

## Why the revision freezes

An agent cannot legitimately change the rules by which its current work is judged.
The invocation therefore runs under one immutable source revision. Any update it
authors becomes active only on a later invocation.

## Mandatory evolution without infinite recursion

The evolution requirement applies once per **top-level skill invocation**. The
required evolution subtask is part of that invocation and does not recursively
create another evolution obligation.

## Concurrency

Multiple agents may discover useful improvements at the same time. They must not
race edits directly onto `main`.

Each agent:

1. starts from the newest accepted `main`;
2. creates an isolated branch;
3. makes one coherent evolution;
4. rebases/reconciles if canonical source moved;
5. reruns validation;
6. submits a PR.

## What counts as meaningful

The qualifying change must reduce a concrete future failure, ambiguity,
inefficiency, validation weakness, quality gap, or repeated manual step. Metadata
churn never qualifies on its own.

## Platform integration

The source repository can be universal, but no Git repository can force every AI
product to load a skill. Each platform needs either:

- a startup/bootstrap hook that runs `distribution/sync.py` or `sync.ps1`, or
- a native connector that reads this repository when the skill is invoked.

ChatGPT can use the connected GitHub repository directly. Local agents install
generated mirrors into their own skill directories. Default paths are listed in
`SOURCE.json` (`default_mirror_paths`):

- Grok: `~/.grok/skills/agents-constitution`
- Codex: `~/.codex/skills/agents-constitution`
