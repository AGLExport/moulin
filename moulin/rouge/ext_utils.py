# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 EPAM Systems
"""
External utils interfaces/wrappers for rouge image builder
"""

from typing import BinaryIO, Union, Optional
import subprocess
import logging

log = logging.getLogger(__name__)


def _run_cmd(args):
    log.info("Running %s", " ".join(args))
    subprocess.run(args, check=True)


# pylint: disable=invalid-name
def dd(file_in: Union[str, BinaryIO],
       file_out: BinaryIO,
       out_offset: int,
       out_size: Optional[int] = None,
       sparse: bool = True):
    "Run dd with the given arguments"
    # Try to guess block size. We would like to use as big block as
    # possible. But we need take into account that "seek" parameter
    # uses block size as the unit.
    blocksize: int = 65536
    while out_offset % blocksize != 0:
        blocksize //= 2

    if isinstance(file_in, str):
        file_in_path = file_in
    else:
        file_in_path = file_in.name
    args = [
        "dd",
        f"if={file_in_path}",
        f"of={file_out.name}",
        f"bs={blocksize}",
        f"seek={out_offset // blocksize}",
        "status=progress",
        "conv=notrunc",
    ]  # yapf: disable
    if sparse:
        args.append("conv=sparse")
    if out_size:
        args.append(f"count={out_size // blocksize}")
    _run_cmd(args)


def simg2img(file_in: Union[str, BinaryIO], file_out: BinaryIO):
    "Run simg2img with the given arguments"
    if isinstance(file_in, str):
        file_in_path = file_in
    else:
        file_in_path = file_in.name
    args = [
        "simg2img",
        file_in_path,
        file_out.name,
    ]  # yapf: disable
    _run_cmd(args)


def mkext4fs(file_out: BinaryIO, contents_dir=None):
    "Create ext4 fs in given file"
    args = ["mkfs.ext4", file_out.name]
    if contents_dir:
        args.append("-d")
        args.append(contents_dir)

    _run_cmd(args)


def mkvfatfs(file_out: BinaryIO, sector_size=None):
    "Create FAT fs in given file"
    args = ["mkfs.vfat"]
    if sector_size:
        args.append("-S")
        args.append(str(sector_size))
    args.append(file_out.name)

    _run_cmd(args)


def mcopy(img: BinaryIO, file: str, name: str):
    "Copy a file to a vfat image with a given name"
    args = ["mcopy", "-i", img.name, file, "::" + name]

    _run_cmd(args)


def mmd(img: BinaryIO, folders: list):
    "Create directories inside a vfat image"
    args = ["mmd", "-i", img.name]
    args.extend(folders)

    _run_cmd(args)


def resize2fs(img: str, size: Optional[int] = None):
    "Resize fs image to the given size"
    args = ["resize2fs", img]

    if size:
        args.append(str(size))

    _run_cmd(args)
