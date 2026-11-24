# SOP run record

`SOP-EXEC-001` in [the SOP](../SOP.md) owns the workflow. This format makes
its evidence reviewable; it is not additional authority or a replacement gate.

For non-trivial work, copy [the empty record](../templates/WORKFLOW-RECORD.json)
into the task's private evidence location and fill it as work proceeds. Reuse
an existing project record if it provides these fields. Do not create a new
record on every continuation. The template intentionally cannot pass completion.
This is the integrator's top-level invocation record. Workers return their
assigned stage results and evidence to it; a worker's completed contribution
does not require a separate complete record or another evolution amendment.

```powershell
python tools/check-workflow-record.py <record.json>
python tools/check-workflow-record.py <record.json> --require-complete
```

The first command validates even honest partial/stopped records. The second
also requires a complete claim, ten accounted stages, all acceptance items
passed, all 15 Section 0 results closed, a 3–12 line self-audit and a staged,
in-PR or accepted evolution. A source CI run does not execute these task checks
on behalf of the agent. If Python is unavailable, inspect the same contract
manually and disclose that the automated record check was not run; never mark
the unavailable checker as passed.

- `invocation`: stable task identity, reused through continuation and recovery.
- `law_sha`: full accepted source frozen at start, not the amendment's version.
- `scope`: actual authorized outcome and boundaries.
- `candidate`: precise immutable subject, such as a commit, artifact digest or
  recorded complete-file hash manifest. A label alone is not artifact integrity.
- `claim`: `complete`, `partial` or `stopped`, for this scope only.
- `stages`: ordered 1–10, `done`/`open`/`na`, exit result/reason, evidence IDs.
  Only 3 and 9 may be N/A. Stage 9 done requires both authorization and observed
  destination evidence. Requested but unavailable delivery must remain open.
- `acceptance`: stable IDs, intended criteria, `pass`/`fail`/`open`, required
  evidence classes and evidence IDs. Define required classes before production;
  do not drop a class to make the checker pass. Passing evidence must identify
  the current candidate. Record the exact named action in the criterion and
  cited observation; class labels alone cannot detect a sibling-action proxy.
- `section0`: ordered 1–15, `pass`/`fail`/`na`/`open`, reason and evidence IDs.
  Each passing item needs evidence on the current candidate. Reused baseline
  evidence also needs a current review of relevant-input equivalence; do not
  simply relabel historical observations with the new candidate identity.
  Apply the actual N/A restrictions in `AGENTS.md`; the tool checks presence of
  a reason, not whether its reasoning is justified.
- `evidence`: unique ID, `kind`, `subject` and `reference`. Kind is `analysis`,
  `review`, `source`, `package`, `install`, `runtime`, `physical`, `authorization`
  or `publication`. `source` includes source QA; `publication` is verified
  destination state after an authorized external action. A command request,
  queued job or approval alone is not that observation. References identify
  exact commands/results, paths, logs or messages, including their limits.
- `evolution`: `unstarted`/`staged`/`in-pr`/`accepted` and evidence IDs. Staged
  means a complete validated apply-ready change, never a suggestion alone.
- `self_audit`: 3–12 concise factual lines at completion; `remaining`: explicit
  next actions/owners, including adoption outside a completed proposal scope.

On change, reopen affected criteria and stages, update the candidate, obtain
fresh evidence and close them again. Preserve prior observations as historical.
Do not relabel old evidence with a new subject without proving unchanged inputs.

The checker validates shape, cross-references and stated evidence classes. It
does not open evidence references, execute commands, contact services, inspect
private data beyond the supplied record, grant approval, authenticate a SHA,
detect false assertions, or guarantee that every client loaded the SOP. Those
claims require actual observation and review. Keep credentials and raw sensitive
content out of records; a private reference can identify evidence without
copying it. Runtime enforcement requires a separately tested host integration.
