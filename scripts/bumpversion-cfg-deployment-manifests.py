#!/usr/bin/env python3  # noqa: N999, EXE001
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
assert pathlib.Path("config").is_dir(), "Run from project root"
bumpversion_cfg = configparser.ConfigParser()
bumpversion_cfg.read(".bumpversion.cfg")
VERSION = bumpversion_cfg["bumpversion"]["current_version"]
print(f"VERSION: {VERSION}")


def fix_manifest_version(
    manifest: pathlib.Path,
    version: str,
    data: Mash,
) -> None:
    """Fix manifest version."""
    print(f"Fixing {manifest} to version {version}")
    data.metadata.version = version
    with contextlib.closing(manifest.open("w")) as manifest_fh:
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


def add_bumpversion_cfg(
    bumpversion_cfg: configparser.ConfigParser,
    manifest: pathlib.Path,
    version: str | None = None,  # noqa: ARG001
) -> None:
    """Add manifest to .bumpversion.cfg."""
    print(f"Adding {manifest} to .bumpversion.cfg")
    bumpversion_cfg.add_section(f"bumpversion:file:{manifest}")
    section = bumpversion_cfg[f"bumpversion:file:{manifest}"]
    for key, value in {
        "parse": "version: (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+),",
        "search": "{current_version}",
        "replace": "{new_version}",
    }.items():
        section[key] = value


for manifest in pathlib.Path("config").glob("*.yaml"):
    print(f"Checking {manifest}")
    data = Mash(load_file(manifest))
    # print(yamlify(data))
    version = data.metadata.version
    if version != VERSION:
        fix_manifest_version(manifest, VERSION, data)
    try:
        _ = bumpversion_cfg[f"bumpversion:file:{manifest}"]
        # print(f"{manifest} already in .bumpversion.cfg")
    except KeyError:
        add_bumpversion_cfg(bumpversion_cfg, manifest, VERSION)

for section in bumpversion_cfg.sections():
    if not section.startswith("bumpversion:file:"):
        continue
    file = section.split(":", 2)[2]
    if not pathlib.Path(file).is_file():
        print(f"Removing {section} from .bumpversion.cfg")
        bumpversion_cfg.remove_section(section)

shutil.copy(".bumpversion.cfg", ".bumpversion.cfg.bak")
with contextlib.closing(pathlib.Path(".bumpversion.cfg").open("w")) as bvcfg_fh:
    bumpversion_cfg.write(bvcfg_fh)
bvcb = pathlib.Path(".bumpversion.cfg.bak").read_text()
bvc = pathlib.Path(".bumpversion.cfg").read_text()
if bvcb == bvc:
    print(".bumpversion.cfg unchanged")
    pathlib.Path(".bumpversion.cfg.bak").unlink()
