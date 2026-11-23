# Proposal review register

Reviewed against accepted v6.22.0 (`c5331af55d3aadf30633c96ae2404845ec830723`).
The v6.23.0 review resolves all 17 known entries: 11 incorporated, two local
freeze variants superseded, two older PRs already covered and two obsolete.
No known proposal remains pending in this register. Decisions take effect
only after this change is accepted on canonical `main`.

The original nine public patches remain byte-exact in `archive/`, with their
original commits, parents and SHA-256 in `manifest.json`. **Archived patches
are historical evidence, not active law. Do not load or auto-apply them.**
Old versions, IDs and pack layouts inside a patch remain historical. The
current canonical homes below contain the reconciled requirements.

| Source | Disposition and canonical home |
|---|---|
| [PR #42](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/42) | Incorporated: fetched base, history preservation and combined integration in `VCS-INTEG-001` |
| [PR #44](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/44) | Incorporated: approval and observed-trial evidence remain distinct in `REL-HARDEN-001` |
| [PR #46](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/46) | Incorporated into `TEST-QUALITY-001`: production payload measurement and round-trip, separate from index/RSS |
| [PR #47](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/47) | Incorporated into `TEST-QUALITY-001`: authored sampling span on shipped inputs in contract units |
| [PR #48](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/48) | Incorporated into `TEST-QUALITY-001`: each shared-pipeline mesh producer uses the same winding oracle |
| [PR #49](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/49) | Incorporated: named actions require their own observed result in `MIG-VERIFY-001` |
| Owned-source warning-gate proposal | Incorporated: actual task/source ownership and uncached evidence in `ENG-STACK-001`; protected warning policy remains unchanged |
| Stacked-resource proposal | Incorporated: resolver order, earlier side effects, initial load/reload and repair evidence in `ENG-FW-001` |
| Streaming-discontinuity proposal | Incorporated: clock/consumer transitions, re-entry and callback-cost evidence in `LOW-RISK-001` |
| Local headless-worker proposal | Incorporated: baseline/delta and immutable-candidate completion/review evidence in `AI-COORD-002` and `AI-COORD-003` |
| Local complete-file repair | Incorporated: preserve the whole source and reconcile unexpected deletions under `OPS-DEL-002` |
| Two local foreign-freeze variants | Superseded: `GOV-FREEZE-001`, `CTX-SELF-001` and `CTX-ASSUME-001` already establish source trust and actual invocation continuity; tool identity does not automatically start a new invocation |
| [PR #5](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/5) | Already covered: current `TEST-DOMAIN-001` requires the actual live entry to call shipped production code |
| [PR #7](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/7), [PR #9](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/9) | Obsolete: local pack discovery and separate skill/pack roots were retired by the unified verified snapshot |
| [PR #10](https://github.com/MrWizard94-Compile/Agents-Constitution/pull/10) | Already covered: accepted PR #13 and current `LOW-RISK-001`/`OBS-PRIV-001` retain its lifecycle and capture safeguards |

The three unaccepted measurement-specific IDs were consolidated into the
existing testing home. Their useful requirements survive without adding
three narrow rule definitions. Old release metadata and the 5.x loader
architecture were not applied. Original local proposal bytes and staged work
remain private and unchanged; only generic requirements, decisions and
provenance hashes are published here.

Run `python tools/check-proposals.py --require-resolved` from the repository
root to validate this register, canonical homes and archive hashes and reject
an unresolved queue. Ordinary validation allows explicitly pending entries.
The checker and source mutation tests establish structural integrity, not
proof that every future agent or product will comply with the rule.
