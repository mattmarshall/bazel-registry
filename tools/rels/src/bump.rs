//! `rels bump` — ripple a `bazel_dep` version pin across every
//! repo whose MODULE.bazel references the named module.
//!
//! Status: **stub** (v0.2). Lands in a follow-up release alongside
//! the cross-repo test harness — we want `bump` to know not just
//! "edit MODULE.bazel" but also "run bazel test //... per
//! dependent and report success/failure" before we ship it.

use anyhow::{bail, Result};
use clap::Args as ClapArgs;

use crate::common::Env;

#[derive(ClapArgs, Debug)]
pub struct Args {
    /// Module name to bump (e.g. `rules_jsonschema`).
    #[arg(long)]
    pub module: String,

    /// Version to pin to (e.g. `0.2.0`).
    #[arg(long)]
    pub to: String,

    /// Print the planned edits without writing them.
    #[arg(long)]
    pub dry_run: bool,
}

pub fn run(_env: &Env, args: Args) -> Result<()> {
    eprintln!(
        "rels bump: not yet implemented (would set {} to {} across all dependents).",
        args.module, args.to,
    );
    eprintln!(
        "Planned v0.2 behavior:",
    );
    eprintln!(
        "  1. Walk every sibling repo's MODULE.bazel for `bazel_dep(name = {:?}, ...)`",
        args.module,
    );
    eprintln!(
        "  2. Rewrite the version pin to {:?}",
        args.to,
    );
    eprintln!(
        "  3. Run `bazel test //...` in each dependent (skip if --dry-run)",
    );
    eprintln!(
        "  4. Print a per-repo summary (passed / failed / skipped)",
    );
    bail!("rels bump is a v0.2 deliverable — track in docs/ROADMAP.md");
}
