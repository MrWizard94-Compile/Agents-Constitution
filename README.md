# WPAI Constitution

The [canonical GitHub repository](https://github.com/MrWizard94-Compile/Agents-Constitution)
is the single source of truth for WPAI's agent quality law, operating process,
skill loader, and verification tools. The accepted `main` commit SHA, not a
local folder name, identifies the binding revision. The prior SOUL and AGENTS
Constitution files are historical inputs; they are not competing law.

Start with [`SKILL.md`](SKILL.md) for how an agent loads and evolves the law,
[`AGENTS.md`](AGENTS.md) for the Definition of Done and 15-point Section 0
gate, and [`SOP.md`](SOP.md) for execution. The applicability matrix selects
scoped `law/*` files. [`governance/EVOLUTION.md`](governance/EVOLUTION.md)
controls source freeze, one meaningful improvement per top-level call,
review, and mirror propagation. [Architecture](docs/ARCHITECTURE.md) and the
[historical-source record](docs/SOURCE-INVENTORY.md) explain the migration.

## Verify source

From a clean checkout, run:

```powershell
python -m unittest discover -s tests -v
python tools/validate-source.py
```

Both commands must exit 0. CI runs the same checks and checks each PR for a
substantive change. A passing source check is not proof that a local mirror,
project pointer, runtime, or published release has been updated.

## Install generated local mirrors

After the accepted `main` commit is verified:

```powershell
python distribution/sync.py --ref main
```

The defaults are in `SOURCE.json`. The sync resolves one immutable SHA,
downloads all binding files before writing, records per-file hashes, and
removes only files named in a previous generated manifest. Unknown local
files are not deleted. A legacy `agents-constitution` install must be
reviewed and retired separately; it is never silently promoted to source.

Project adoption uses [`templates/PROJECT-POINTER.md`](templates/PROJECT-POINTER.md)
with project mission, stack, and acceptance in that project's own repository.
Do not vendor editable law into each project.

The [quality assurance map](docs/QUALITY-ASSURANCE-MAP.md) helps select
domain-specific evidence and independent oracles. It does not waive Section 0
or turn a green test result into a claim of complete acceptance.

Before retiring an old project pack, run the read-only consumer audit:

```powershell
python tools/check-adoption.py <project-git-root>
```

It checks tracked and unignored project files, the top-level retired-pack
folder, and full SOUL copies. Resolve old CI, generator, manifest, pointer,
and UI references before the old tree is removed. A clean audit is not a
substitute for the project's build and runtime checks.

## Inventory local Constitution copies

The read-only scanner hashes candidates and records access errors. For a broad
PC inventory, name each intended root and choose an output outside the scanned
roots when practical:

```powershell
python -u tools/inventory_copies.py --root C:\ --root D:\ --root E:\ --output "C:\WPAI\WPAI Constitution\.local-audit\inventory-2026-10-12.json"
```

The scanner excludes its own output and checkpoint files when they sit inside
a scanned root. It writes `<output>.checkpoint.json` atomically after each
1,000 completed directories and prints durable progress. If interrupted, rerun the
same command with `--resume`; root order, output, and text-size limit must
match. `--checkpoint-directories` adjusts the interval when a shorter recovery
window is needed. A final report is created **only** after every root has been
traversed and has `status: complete`. The checkpoint is intentionally retained
as recovery evidence. Access errors and skipped filesystem links still bound
the completeness claim; inspect them before any cleanup. Use a new output name
for a new scan, rather than replacing a prior report.

Resume validates each queued directory against every named root independently;
unrelated Windows drive letters do not abort the scan, while a queued path
outside all roots (including through a reparse-point parent) is rejected.

The public repository deliberately omits raw private project variants,
machine-specific paths, credentials, and local cleanup manifests. See the
source inventory for what is and is not yet reconciled.
