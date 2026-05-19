# rels

`rels` is the fastverk bazel-registry CLI. It owns the cross-repo
operations that used to be hand-run scripts: cutting releases,
auditing for drift, and emitting status overviews.

## Build

`rels` is a real `rust_binary` built via rules_rust + crates_universe
— consistent with how every other fastverk Rust tool ships.

```sh
bazel run //tools/rels:rels -- --help
```

Cargo also works for local iteration:

```sh
cargo build --release -p rels
./target/release/rels --help
```

## Subcommands

### `rels release` — cut a new version

Replaces `tools/add_module/add_module.py`. Given a `--repo` + `--version`:

1. Resolves the GitHub-auto-generated tarball URL
   (`<repo>/archive/refs/tags/v<version>.tar.gz`).
2. Downloads it; computes SRI integrity (`sha256-<base64>`).
3. Extracts `<strip_prefix>/MODULE.bazel` from the tarball.
4. Writes `modules/<name>/<version>/{source.json, MODULE.bazel}`
   and upserts `modules/<name>/metadata.json`.

```sh
rels release --repo fastverk/rules_uv --version 0.5.1
```

### `rels audit` — cross-repo consistency check

Walks every registered module and the sibling rules_* checkout
under `<workspaces_root>/<name>/`, surfacing:

- **Tag↔registry drift**: tags on the remote that aren't
  registered (or registry entries with no matching tag).
- **Module version drift**: the on-disk `MODULE.bazel#version`
  diverges from the latest remote tag.
- **Missing infrastructure**: CHANGELOG.md, .github/workflows/ci.yml,
  docs/BUILD.bazel (stardoc setup).
- **`.gitignore` gaps**: `.claude/` and `MODULE.bazel.lock` not
  listed.
- **Dirty trees**: uncommitted changes in the local checkout.

```sh
rels audit                 # full audit (touches the network)
rels audit --no-remote     # skip git ls-remote calls
rels audit --markdown      # Markdown bulleted output
```

Exits non-zero if any finding is reported. Suitable for nightly
GH Actions jobs (see `.github/workflows/nightly-audit.yml`).

### `rels matrix` — status overview as Markdown

Emits a Markdown table of every registered module with the latest
version, plus presence badges for CHANGELOG / CI / stardoc.
Useful for the bazel-registry README:

```sh
rels matrix > MATRIX.md
```

### `rels bump` — ripple a `bazel_dep` version pin

**Stub** (v0.2). Will rewrite the version pin for a named module
across every dependent repo and run `bazel test //...` in each.
Tracked in the roadmap.

## Conventions

`rels` resolves two filesystem roots:

- `--registry-root` (or auto-discovered): the bazel-registry
  checkout. Contains `bazel_registry.json` + `modules/`.
- `--workspaces-root` (default: `<registry_root>/..`): the parent
  directory holding sibling rules_* checkouts.

Every subcommand exits non-zero on failure with a human-readable
message on stderr. Stdout is reserved for structured output
(Markdown, future JSON) so callers can pipe.
