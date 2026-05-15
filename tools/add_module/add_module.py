#!/usr/bin/env python3
"""Add a module version to the registry.

Typical usage:
    tools/add_module/add_module.py \\
        --repo fastverk/rules_lean \\
        --version 0.1.0

The repo/version pair is resolved to the GitHub auto-generated tag tarball at
    https://github.com/<repo>/archive/refs/tags/v<version>.tar.gz
with strip_prefix `<repo-basename>-<version>`. Override with --url and
--strip-prefix for non-GitHub sources.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REGISTRY_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REGISTRY_ROOT / "modules"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def sri_integrity(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def extract_module_bazel(tarball: bytes, strip_prefix: str) -> str:
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        candidate = f"{strip_prefix}/MODULE.bazel" if strip_prefix else "MODULE.bazel"
        for member in tar.getmembers():
            if member.name == candidate:
                f = tar.extractfile(member)
                if f is None:
                    raise RuntimeError(f"{candidate}: not a regular file in tarball")
                return f.read().decode("utf-8")
    raise RuntimeError(
        f"MODULE.bazel not found at '{strip_prefix}/MODULE.bazel' inside tarball. "
        "Pass --strip-prefix if the tarball uses a non-standard top-level directory."
    )


def write_source_json(dst: Path, url: str, integrity: str, strip_prefix: str) -> None:
    data = {
        "integrity": integrity,
        "strip_prefix": strip_prefix,
        "url": url,
    }
    dst.write_text(json.dumps(data, indent=2) + "\n")


def upsert_metadata(metadata_path: Path, repo: str, version: str) -> None:
    if metadata_path.exists():
        meta = json.loads(metadata_path.read_text())
    else:
        meta = {
            "homepage": f"https://github.com/{repo}",
            "maintainers": [
                {"name": "Matt Marshall", "github": "mattmarshall"}
            ],
            "repository": [f"github:{repo}"],
            "versions": [],
            "yanked_versions": {},
        }
    if version not in meta["versions"]:
        meta["versions"].append(version)
        meta["versions"].sort(key=_version_sort_key)
    metadata_path.write_text(json.dumps(meta, indent=2) + "\n")


def _version_sort_key(v: str) -> tuple:
    """Semver-style sort key tolerating pre-release suffixes (`-rc1`, `-alpha`,
    etc.). Pre-releases sort *before* their base release: `0.3.0-rc1` <
    `0.3.0` < `0.3.1`."""
    base, _, pre = v.partition("-")
    base_parts = tuple(int(p) for p in base.split("."))
    # `(0, pre)` for pre-releases sorts before `(1, "")` for the base release.
    pre_marker = (0, pre) if pre else (1, "")
    return base_parts + pre_marker


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", help="GitHub repo as owner/name (e.g. fastverk/rules_lean)")
    p.add_argument("--version", required=True, help="Module version (e.g. 0.1.0)")
    p.add_argument("--name", help="Module name. Defaults to repo basename.")
    p.add_argument("--url", help="Override tarball URL (skips GitHub convention)")
    p.add_argument("--strip-prefix", help="Override strip_prefix")
    p.add_argument("--tag-prefix", default="v", help="Tag prefix (default: 'v')")
    p.add_argument("--force", action="store_true", help="Overwrite existing version entry")
    args = p.parse_args()

    if not args.repo and not (args.url and args.name):
        p.error("either --repo, or both --url and --name, is required")

    name = args.name or args.repo.split("/")[-1]
    tag = f"{args.tag_prefix}{args.version}"

    if args.url:
        url = args.url
        strip_prefix = args.strip_prefix or ""
    else:
        repo_basename = args.repo.split("/")[-1]
        url = f"https://github.com/{args.repo}/archive/refs/tags/{tag}.tar.gz"
        strip_prefix = args.strip_prefix or f"{repo_basename}-{args.version}"

    version_dir = MODULES_DIR / name / args.version
    if version_dir.exists() and not args.force:
        print(f"error: {version_dir.relative_to(REGISTRY_ROOT)} already exists; use --force to overwrite",
              file=sys.stderr)
        return 1

    print(f"fetching {url} ...", file=sys.stderr)
    tarball = fetch(url)
    integrity = sri_integrity(tarball)
    module_bazel = extract_module_bazel(tarball, strip_prefix)

    version_dir.mkdir(parents=True, exist_ok=True)
    (version_dir / "MODULE.bazel").write_text(module_bazel)
    write_source_json(version_dir / "source.json", url, integrity, strip_prefix)

    if args.repo:
        upsert_metadata(MODULES_DIR / name / "metadata.json", args.repo, args.version)

    print(f"wrote {version_dir.relative_to(REGISTRY_ROOT)}/", file=sys.stderr)
    print(f"  integrity: {integrity}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
