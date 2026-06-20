#!/usr/bin/env python3
"""Recursively convert audio files to MP3 with ffmpeg."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


AUDIO_EXTENSIONS = {
    ".aac",
    ".aif",
    ".aiff",
    ".alac",
    ".flac",
    ".m4a",
    ".m4b",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}

COMMON_FFMPEG_PATHS = (
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/usr/bin/ffmpeg",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively convert audio files to MP3 beside the originals."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or folders to process. Folders are scanned recursively.",
    )
    parser.add_argument(
        "--trash-originals",
        action="store_true",
        help="Move original non-MP3 audio files to the macOS Trash after conversion succeeds.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing MP3 outputs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned work without converting or moving files.",
    )
    parser.add_argument(
        "--preset",
        choices=("music", "audiobook"),
        default="music",
        help="Encoding preset. music uses high-quality VBR; audiobook uses smaller 128k MP3 while preserving channels.",
    )
    parser.add_argument(
        "--quality",
        default=None,
        help="Override music preset libmp3lame VBR quality, 0-9. Lower is better.",
    )
    return parser.parse_args()


def find_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    for candidate in COMMON_FFMPEG_PATHS:
        if Path(candidate).exists():
            return candidate
    raise SystemExit(
        "ffmpeg was not found. Install it with Homebrew: brew install ffmpeg"
    )


def iter_audio_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = raw_path.expanduser().resolve()
        if not path.exists():
            print(f"Missing: {path}", file=sys.stderr)
            continue
        if path.is_file():
            if is_convertible(path):
                files.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and is_convertible(child):
                files.append(child)
    return sorted(set(files))


def is_convertible(path: Path) -> bool:
    suffix = path.suffix.lower()
    return suffix in AUDIO_EXTENSIONS and suffix != ".mp3"


def convert_to_mp3(
    source: Path,
    *,
    ffmpeg: str,
    overwrite: bool,
    preset: str,
    quality: str | None,
    dry_run: bool,
) -> bool:
    target = source.with_suffix(".mp3")
    if target.exists() and not overwrite:
        print(f"Skip existing: {target}")
        return False

    print(f"Convert: {source} -> {target}")
    if dry_run:
        return False

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{target.stem}.",
        suffix=".mp3.tmp",
        dir=target.parent,
    )
    os.close(fd)
    tmp_path = Path(tmp_name)

    encoder_args = build_encoder_args(preset=preset, quality=quality)

    try:
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-vn",
                *encoder_args,
                "-map_metadata",
                "0",
                "-id3v2_version",
                "3",
                "-f",
                "mp3",
                str(tmp_path),
            ],
            check=True,
        )
        tmp_path.replace(target)
        return True
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def build_encoder_args(*, preset: str, quality: str | None) -> list[str]:
    if preset == "music":
        return ["-c:a", "libmp3lame", "-q:a", quality or "0"]
    if preset == "audiobook":
        return ["-c:a", "libmp3lame", "-b:a", "128k"]
    raise ValueError(f"Unknown preset: {preset}")


def trash_file(path: Path, *, dry_run: bool) -> None:
    print(f"Trash original: {path}")
    if dry_run:
        return
    subprocess.run(
        [
            "osascript",
            "-e",
            "on run argv",
            "-e",
            "set sourceFile to POSIX file (item 1 of argv) as alias",
            "-e",
            'tell application "Finder" to delete sourceFile',
            "-e",
            "end run",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main() -> int:
    args = parse_args()
    ffmpeg = find_ffmpeg()

    files = iter_audio_files(args.paths)
    if not files:
        print("No convertible audio files found.")
        return 0

    converted = 0
    failed = 0
    for source in files:
        try:
            did_convert = convert_to_mp3(
                source,
                ffmpeg=ffmpeg,
                overwrite=args.overwrite,
                preset=args.preset,
                quality=args.quality,
                dry_run=args.dry_run,
            )
            if did_convert:
                converted += 1
                if args.trash_originals:
                    trash_file(source, dry_run=args.dry_run)
        except subprocess.CalledProcessError as error:
            failed += 1
            print(f"Failed: {source} ({error})", file=sys.stderr)

    print(f"Done. Converted: {converted}. Failed: {failed}.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
