# Copyright (c) Microsoft Corporation. All rights reserved.
import functools
from pathlib import Path

import versioningit
from packaging.version import parse

PROJECT_DIR = Path(__file__).parent.parent


def _get_version() -> str:
    return versioningit.get_version(project_dir=PROJECT_DIR)


def _versioningit() -> versioningit.Versioningit:
    # Special config for pcell versioning.
    config = versioningit.config.Config.parse_obj(
        {
            "format": {
                "dirty": "{version}.{branch}.{vcs}{rev}.dirty",
                "distance": "{version}.{branch}.{vcs}{rev}",
                "distance-dirty": "{version}.{branch}.{vcs}{rev}.dirty",
            }
        }
    )
    kw = {"template_fields": config.template_fields.load(PROJECT_DIR)} if parse(versioningit.__version__) >= parse("2.0.0") else {}
    return versioningit.Versioningit(
        project_dir=PROJECT_DIR,
        default_version=config.default_version,
        vcs=config.vcs.load(PROJECT_DIR),
        tag2version=config.tag2version.load(PROJECT_DIR),
        next_version=config.next_version.load(PROJECT_DIR),
        format=config.format.load(PROJECT_DIR),
        write=None,
        onbuild=None,
        **kw
    )


@functools.lru_cache
def _format_version_function():
    # Cache the versioningit instance do_vcs call, so that it is only created once.
    V = _versioningit()
    return functools.partial(V.format, description=V.do_vcs())


def format_pcell_version(version: str) -> str:
    """Formats a pcell version string.

    If imported from main and there are no unstaged changes, the version string
    is returned unchanged, so "1.0.0" remains "1.0.0".

    In all other cases, the version string is formatted, e.g., "1.0.0" becomes
    - on a branch "foo" on commit 477c16f2 with *no* unstaged changes "1.0.0.foo.g477c16f2"
    - on a branch "foo" on commit 477c16f2 *with* unstaged changes "1.0.0.foo.g477c16f2.dirty"

    Parameters
    ----------
    version : str
        Version string, e.g. "1.0.0"

    Returns
    -------
    str
        Formatted version string.
    """
    try:
        format = _format_version_function()
    except (versioningit.errors.NoTagError, versioningit.errors.NotVCSError):
        # No Git history available, return the version unchanged.
        return version
    vcs = format.keywords["description"]  # take from partial kewords
    if "dirty" not in vcs.state and vcs.branch == "main":
        # If on main branch, with unstaged changes, return unchanged version.
        return version
    kw = {"base_version" if parse(versioningit.__version__) >= parse("2.0.0") else "version": version}
    return format(**kw, next_version=version)


__version__ = _get_version()
