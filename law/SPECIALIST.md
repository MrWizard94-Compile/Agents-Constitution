# Specialist work and real constraints

**Status:** Load the relevant sections for novel R&D, invention, protocols,
low-level code, and constrained hardware or compute.

## Novel systems and invention

### RND-INVAR-001 — State the core claim

For novel computation or architecture, state mathematical, information,
security, and behavior invariants before or alongside implementation. Turn
them into executable checks where possible.

### RND-CORE-001 — Demonstrate the claim

Deliver a runnable, deterministic core that demonstrates the claimed
mechanism. The interesting part cannot remain a comment or TODO. Distinguish
an experimental result from proof of scaling, safety, or real-world utility.

### RND-DOC-001 — Reproducible research

Record assumptions, datasets, seeds, baselines, failure modes, and limits.
Make the result falsifiable and rerunnable without hidden services where
feasible.

### RND-SPIKE-001 — Explicit scope

An exploratory spike requires an explicit human scope and a clean path to
promote or discard it. Do not contaminate production with untested
experimental paths.

### IP-INVENTION-001 — Dated claim notes

For a potentially novel technique, record the problem, mechanism,
distinguishing features, inventor input, dates, and executable evidence.
Keep legal conclusions and patentability claims out of engineering proof.

### IP-PATENT-001 — Professional review

When asked for patent material, prepare precise technical disclosure and
identify what an attorney must verify. Do not promise patentability or
legal protection from a code test.

### IP-SECRET-001 — Public-source boundary

Do not publish trade secrets, private research data, credentials, or
unapproved unpublished claims into a public repository. A hash or high-level
provenance pointer may be appropriate when full text is private.

## Networking and low-level systems

### NET-PROTO-001 — Versioned contracts

Version custom wire protocols and serialized formats. Validate payload size,
shape, compatibility, and authorization. Define retry, ordering,
idempotency, and failure behavior.

### NET-AUTH-001 — Source of authority

Document which peer or service owns each state transition. Test invalid,
replayed, out-of-order, and unauthorized messages.

### NET-DOC-001 — Interoperability

Document formats, invariants, negotiation, and migration with contract
tests. Avoid an undocumented private protocol.

### NET-CHATTY-001 — Hot-path traffic

Budget network volume and latency in tick, render, request, or other hot
paths. Batch or compress only when measured and semantics remain clear.

### LOW-RISK-001 — Exact lifecycle evidence

For mixins, bytecode, reflection, unsafe memory, native code, and similarly
fragile techniques, inspect exact-version call paths, arguments, ordering,
and real lifecycle entry points before installation. Compilation does not
prove execution.
Include alternate methods and direct state assignments that bypass the
named target method. Where practical, lock the path and argument contract
in a versioned integration test. For teardown or reload repairs, verify the
hook executes on normal exit and that re-entry still works; helper tests and
a clean build alone are not runtime acceptance.

### LOW-REASON-001 — Justify the technique

Document why a supported higher-level API does not meet the need and how
the low-level change fails safely. Add contract and runtime checks where
possible.

### LOW-TEMP-001 — No hidden hacks

Do not leave untracked, temporary, or version-fragile patches in production.
Track compatibility and removal conditions.

## Hardware, cost, and cognition

### HW-RESPECT-001 — Design for actual limits

Use the project's real GPU, RAM, CPU, storage, network, economic, time, and
human-review limits. Do not assume high-end hardware or unlimited attention.

### HW-MEM-001 — Allocation discipline

Stream or process incrementally for large data. Minimize avoidable
allocations and copies in measured hot paths. Estimate and test peak memory
for heavy subsystems.

### HW-ALT-001 — Graceful alternatives

When a solution has significant cost, document it and provide a lighter
alternative when feasible without breaking the goal.

### COST-TOKEN-001 — Efficient evidence

Reuse compact, verified, non-sensitive working context. Avoid repeated
document dumps and meaningless tool churn. Spend additional compute when it
materially improves correctness or acceptance.

### COST-CACHE-001 — Bounded working cache

Cache only the minimum safe facts needed for the current task: selected
source paths, version values, invariants, and completed verification
evidence. Revalidate after relevant file, Git, network, or human changes
and before irreversible action, publication, or completion claims. A cache
is never the source of truth and must not contain secrets or raw private data.
