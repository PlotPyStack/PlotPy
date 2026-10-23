# -*- coding: utf-8 -*-
"""
Install development versions of dependencies for Read the Docs builds.

This project is developed alongside other PlotPyStack and DataLab Platform
projects: development branches and pull requests may require dependency versions
which are not yet published on PyPI, so installing the documentation requirements
from PyPI alone would fail.

This script mirrors the GitHub Actions test workflows:

- tag builds and release branches: nothing is done, dependencies are installed
  from PyPI by the regular ``python.install`` step;
- other branches and pull requests: the dependencies listed in
  ``DEV_DEPENDENCIES`` are installed from GitHub. The regular ``python.install``
  step then keeps these versions as they already satisfy the project
  requirements.

It is intended to be run as a ``build.jobs.pre_install`` step and only relies on
the standard library and ``git``.

The same script is used by several projects: only the project-specific settings
below differ between copies.
"""

from __future__ import annotations

import os
import subprocess
import sys

# ---- Project-specific settings ----------------------------------------------
PROJECT_REPO = "https://github.com/PlotPyStack/PlotPy.git"
#: Placeholder for the name of the branch being built
SAME_BRANCH = "{branch}"
#: Dependencies to install from GitHub for development builds:
#: package name -> (repository URL, candidate branches, first existing one is used)
DEV_DEPENDENCIES = {
    "PythonQwt": ("https://github.com/PlotPyStack/PythonQwt.git", ("master",)),
    "guidata": ("https://github.com/PlotPyStack/guidata.git", ("develop",)),
}
# -----------------------------------------------------------------------------

RELEASE_BRANCHES = ("main", "master", "release")


def get_remote_branches(url: str) -> dict[str, str]:
    """Return the branches of a remote Git repository.

    Args:
        url: Remote repository URL

    Returns:
        Mapping of branch names to the commit hash of their head
    """
    output = subprocess.run(
        ["git", "ls-remote", "--heads", url],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    branches = {}
    for line in output.splitlines():
        commit, ref = line.split("\t", 1)
        branches[ref.removeprefix("refs/heads/")] = commit
    return branches


def get_built_branch() -> str | None:
    """Return the branch being built, if it can be determined.

    For pull request builds, Read the Docs only provides the pull request number,
    so the branch is the one of the project repository whose head is the commit
    being built.

    Returns:
        Branch name, or None for tag builds and pull requests from forks
    """
    version_type = os.environ.get("READTHEDOCS_VERSION_TYPE")
    if version_type == "branch":
        return os.environ["READTHEDOCS_GIT_IDENTIFIER"]
    if version_type == "external":
        commit = os.environ["READTHEDOCS_GIT_COMMIT_HASH"]
        for branch, head in get_remote_branches(PROJECT_REPO).items():
            if head == commit:
                return branch
    return None


def select_branch(url: str, candidates: tuple[str, ...], built: str | None) -> str:
    """Return the first candidate branch which exists in a remote repository.

    Args:
        url: Remote repository URL
        candidates: Candidate branch names, ``SAME_BRANCH`` standing for the
         branch being built
        built: Branch being built, or None if unknown

    Returns:
        Selected branch name
    """
    names = [built if name == SAME_BRANCH else name for name in candidates]
    existing = get_remote_branches(url)
    for name in names:
        if name is not None and name in existing:
            return name
    raise SystemExit(f"None of the branches {names} exists in {url}")


def main() -> None:
    """Install dependencies from GitHub for development builds."""
    version_type = os.environ.get("READTHEDOCS_VERSION_TYPE")
    if version_type not in ("branch", "external"):
        print(f"Version type {version_type!r}: dependencies installed from PyPI")
        return
    built = get_built_branch()
    if built in RELEASE_BRANCHES:
        print(f"Branch {built!r}: dependencies installed from PyPI")
        return
    print(f"Development build (branch: {built or 'unknown'})")
    requirements = []
    for name, (url, candidates) in DEV_DEPENDENCIES.items():
        branch = select_branch(url, candidates, built)
        print(f"  {name}: {branch!r} branch")
        requirements.append(f"{name} @ git+{url}@{branch}")
    # Single pip call, so that dependencies between these packages are resolved
    # against their development versions rather than against PyPI releases
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", *requirements],
        check=True,
    )


if __name__ == "__main__":
    main()
