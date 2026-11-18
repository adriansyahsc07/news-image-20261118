#!/usr/bin/env python3
"""news-image-20261118 entry (Python 3.13, standard library only).

Mirrors the kit starter's contract: the image is the entry.png beside this
file, and the program copies it to <output>/entry.png, where <output> is
$MAKEFUN_OUTPUT_DIR outside the grader's container and /output inside it:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

The copy is a fixed byte-for-byte transfer of a repo-held file: no network,
no randomness, no clock, so two runs in separate sandboxes write identical
bytes.
"""
import os
import shutil
from pathlib import Path

src = Path(__file__).resolve().parent / "entry.png"
dst_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
shutil.copyfile(src, dst_dir / "entry.png")
