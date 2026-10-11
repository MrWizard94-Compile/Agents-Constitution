# WPAI Constitution load order

All files come from the **same verified canonical commit SHA** or a previously
verified mirror of it. A local project pointer is additional Level-4 context,
not a substitute for the canonical files.

1. `SKILL.md` — loader and one-change-per-top-level-call obligation.
2. `AGENTS.md` — binding quality law, Definition of Done, Section 0 gate.
3. `SOP.md` — scaled project-to-product workflow.
4. `governance/EVOLUTION.md` — source, freeze, review, propagation.
5. Relevant `law/*` files per the matrix in `AGENTS.md`.
6. Project-local instructions and acceptance criteria.

Read `governance/RULE-REGISTRY.md` when citing or amending a Rule ID. For a
mirrored installation, compare `.GENERATED-MIRROR.json` with the source
manifest. On mismatch, stop or fetch a verified commit; do not combine rules
from different snapshots.
