#!/usr/bin/env python3  # noqa: N999
"""
Syncs environment manifests to .bumpversion.cfg.

Created on Thu Jul  8 14:55:55 2021
"""
import configparser
import contextlib
import pathlib
import shutil

from toolbag.datastructures.formatting import yamlify
from toolbag.datastructures.mash import Mash
from toolbag.utils.load_file import load_file

__version__ = "0.26.74"

assert pathlib.Path(".bumpversion.cfg").is_file(), "Run from project root"
assert pathlib.Path("manifests").is_dir(), "Run from project root"
bumpversion_cfg = configparser.ConfigParser()
bumpversion_cfg.read(".bumpversion.cfg")
VERSION = bumpversion_cfg["bumpversion"]["current_version"]
print(f"VERSION: {VERSION}")


def fix_manifest_version(
    manifest: pathlib.Path,
    version: str,
    data: Mash,
) -> None:
    """Fix a manifest version."""
    print(f"Fixing {manifest / 'manifest.yaml'} to version {version}")
    data.metadata.version = version
    with contextlib.closing((manifest / "manifest.yaml").open("w")) as manifest_fh:
        text = yamlify(
            {
                key: sect
                for key, sect in data.items()
                if key
                not in (
                    "metadata",
                    "manifests",
                )
            },
        )
        if "manifests" in data:
            text += yamlify({"manifests": data.manifests})
        text += yamlify({"metadata": data.metadata})
        manifest_fh.write(text)


def update_bumpversion_cfg(
    bumpversion_cfg: configparser.ConfigParser,
    manifest: pathlib.Path,
    section: configparser.SectionProxy,
    add: bool = False,
) -> None:
    """Update a manifest in .bumpversion.cfg."""
    if not add:
        print(f"Updating {manifest / 'manifest.yaml'}({section.name}) of .bumpversion.cfg")
    for key, value in {
        "parse": "version: (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+),",
        "search": "version: {current_version}",
        "replace": "version: {new_version}",
    }.items():
        section[key] = value

    bumpversion_cfg[section.name] = section


def add_bumpversion_cfg(
    bumpversion_cfg: configparser.ConfigParser,
    manifest: pathlib.Path,
    version: str,  # noqa: ARG001
) -> None:
    """Add a manifest to .bumpversion.cfg."""
    print(f"Adding {manifest / 'manifest.yaml'} to .bumpversion.cfg")
    bumpversion_cfg.add_section(f"bumpversion:file:{manifest / 'manifest.yaml'}")
    section = bumpversion_cfg[f"bumpversion:file:{manifest / 'manifest.yaml'}"]
    update_bumpversion_cfg(bumpversion_cfg, manifest, section, add=True)


for manifest in pathlib.Path("manifests").glob("*"):
    if not (manifest.is_dir() and (manifest / "manifest.yaml").is_file()):
        continue
    print(f"Checking {manifest}")
    data = Mash(load_file(manifest / "manifest.yaml"))
    version = data.metadata.version
    if version != VERSION:
        fix_manifest_version(manifest, VERSION, data)
    try:
        section = bumpversion_cfg[f"bumpversion:file:{manifest / 'manifest.yaml'}"]
        update_bumpversion_cfg(bumpversion_cfg, manifest, section=section)
    except KeyError:
        add_bumpversion_cfg(bumpversion_cfg, manifest, VERSION)

shutil.copy(".bumpversion.cfg", ".bumpversion.cfg.bak")
with contextlib.closing(pathlib.Path(".bumpversion.cfg").open("w")) as bvcfg_fh:
    bumpversion_cfg.write(bvcfg_fh)
bvcb = pathlib.Path(".bumpversion.cfg.bak").read_text()
bvc = pathlib.Path(".bumpversion.cfg").read_text()
if bvcb == bvc:
    print(".bumpversion.cfg unchanged")
    pathlib.Path(".bumpversion.cfg.bak").unlink()
