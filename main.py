#!/usr/bin/env python3
"""Publish this entry's artwork to the grader's output folder.

The whole submission is a single picture, ``entry.png``, stored in this
repository beside this script.  Running the program performs one job:
reproduce that picture, unchanged, as ``entry.png`` inside the directory
named by the ``MAKEFUN_OUTPUT_DIR`` environment variable (falling back to
``/output`` when the variable is unset).

Nothing here reaches the network, reads a clock, or rolls dice, so the
bytes produced are a pure function of the repository contents.  As a
final guard the copy is measured and hashed once written; any drift
between source and destination aborts the run instead of silently
handing the grader a corrupted image.
"""

import hashlib
import os
from pathlib import Path

CHUNK = 64 * 1024  # stream the file in 64 KiB slices, never all at once
ARTWORK_NAME = "entry.png"


def repo_artwork() -> Path:
    """Locate the canonical image shipped with this repository."""
    return Path(__file__).resolve().parent / ARTWORK_NAME


def target_folder() -> Path:
    """Resolve where the grader expects the published image to land."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return Path(raw) if raw else Path("/output")


def stream_copy(source: Path, destination: Path) -> None:
    """Move the image across in fixed-size slices, byte for byte."""
    with source.open("rb") as reader, destination.open("wb") as writer:
        while slice_ := reader.read(CHUNK):
            writer.write(slice_)


def fingerprint(path: Path) -> tuple[int, str]:
    """Return a (byte count, SHA-256 hex digest) summary of a file."""
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while block := handle.read(CHUNK):
            total += len(block)
            digest.update(block)
    return total, digest.hexdigest()


def publish() -> Path:
    """Copy the artwork out and prove the copy is faithful."""
    origin = repo_artwork()
    if not origin.is_file():
        raise FileNotFoundError(f"repository artwork missing: {origin}")

    folder = target_folder()
    folder.mkdir(parents=True, exist_ok=True)
    placed = folder / ARTWORK_NAME

    stream_copy(origin, placed)

    if fingerprint(origin) != fingerprint(placed):
        raise RuntimeError(f"copy verification failed for {placed}")
    return placed


if __name__ == "__main__":
    publish()
