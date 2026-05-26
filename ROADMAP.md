# bazel-registry — Roadmap

The fastverk bazel-registry + its `rels` tooling. This roadmap
covers near-term registry + tooling work. Each sibling module has
its own ROADMAP.md describing per-module plans.

## Recently shipped

- **rels srcs fix** (this turn): `//tools/rels:rels` was missing
  `scaffold.rs` and `mcp.rs` from its `rust_binary` srcs, blocking
  any `rels` subcommand. Fixed by adding both files to the srcs
  list in `tools/rels/BUILD.bazel`.

## Near-term: cut releases for the new sibling constellation

Ten new modules ship in working trees but not yet in the registry.
Each has a ROADMAP.md of its own; this section tracks the
**registry-side** registration work.

For each module, the cut-release flow is:

1. Init git in the module's repo (if not already) + create a
   GitHub repo under `fastverk/`:
   ```
   cd /Volumes/Workspace/<module>
   git init -b main && git add -A && git commit -m "Initial scaffold"
   gh repo create fastverk/<module> --public --source=. --push
   ```
2. Tag the release: `git tag v0.X.Y && git push --tags`.
3. Run `bazel run //tools/rels:rels -- release --module <module> --version <X.Y.Z>`
   in this registry checkout. That writes
   `modules/<module>/<version>/{MODULE.bazel,source.json}` and
   upserts `modules/<module>/metadata.json` with the SRI integrity
   hash + GitHub tarball URL.
4. Commit the new registry entries + push to fastverk/bazel-registry.

Modules ready to cut (smoke-verified end-to-end):

| Module | Version | Notes |
|---|---|---|
| `rules_cc_cross` | 0.1.0 | aarch64-none-elf, sha256-pinned. |
| `rules_qemu` | 0.1.0 | hermetic via Homebrew bottles. |
| `rules_microkit_tool` | 0.0.1 | SDK download, multi-host pinned. |
| `rules_microkit` | 0.0.1 | hello_on_qemu boots end-to-end. |
| `rules_kicad` | 0.2.0 | hermetic via DMG + hdiutil. |

Modules to cut once they have a real smoke example:

| Module | Notes |
|---|---|
| `rules_verilog` | Needs verilator/yosys hermetic path (see its roadmap). |
| `rules_board` | Needs end-to-end PCB + microkit smoke. |
| `rules_riscv_core` | Needs first curated preset (`ibex_small`). |
| `rules_chisel` | Scaffold only; full Mill/JVM integration TBD. |
| `rules_sel4` | Scaffold only; full kernel-from-source build TBD. |

## Tooling: rels improvements

- **`rels scaffold --template embedded`** — per the master plan,
  add a template variant that pre-adds `rules_foreign_cc` +
  `toolchains/` skeleton. Reduces boilerplate for any future
  cross-compile module.
- **`rels release` integration with sibling git tags** — current
  implementation requires manually tagging. Could extend `rels
  release` to drive the whole flow (tag, push, write registry
  entries, push registry).
- **`rels audit` cross-module** — once all ten modules are in,
  audit consistency: same minimum bazel version, same minimum
  rules_cc version, consistent `bazel_dep` formatting,
  consistent `.bazelrc` registry pins.
- **`rels matrix`** — refresh the Markdown status table with the
  new modules.

## Registry-wide policy items

- **CI standard.** All new modules ship with the scaffold's
  default CI (`ubuntu-latest` + `macos-latest` matrix, buildifier
  lint). The hermetic modules (`rules_qemu`, `rules_kicad`, `rules_cc_cross`)
  need an additional smoke job that exercises their hermetic
  extraction paths — that requires a CI runner with enough disk
  for the cached downloads (~1.5 GB for kicad, ~400 MB for qemu).
- **Modules-vs-registry releases.** A registry release isn't
  required for every sibling-module commit; the registry is the
  source of truth for *consumable* versions. Sibling modules can
  iterate freely on `main`, then cut when stable.
- **Lockstep version bumps.** When a foundational module (e.g.
  `rules_cc_cross`) makes a breaking change, all dependents
  (`rules_microkit`, `rules_board`) need a coordinated bump. Use
  `rels bump` for the mechanical rewrites.

## Housekeeping

- **`.gitignore` for `target/rust-analyzer/`.** Some prior commit
  accidentally tracked rust-analyzer flycheck noise; should
  un-track + extend .gitignore.
- **README** mentions the registry workflow but doesn't yet list
  all ten new sibling modules. Refresh after the first batch is
  released.
