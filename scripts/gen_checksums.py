#!/usr/bin/env python3
"""Generate the immutable CHECKSUMS.sha256 manifest for the release.

One line per file: "<sha256>  <relative/path>" (two spaces). LF newlines.
Digests are computed over LF-normalized bytes, so a CRLF checkout still matches.
Run this after any content change and commit the manifest together with it.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


lines = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or ".git" in p.parts:
        continue
    rel = p.relative_to(ROOT).as_posix()
    if rel == "CHECKSUMS.sha256":
        continue
    lines.append(f"{sha256(p)}  {rel}")

(ROOT / "CHECKSUMS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print(f"wrote CHECKSUMS.sha256 ({len(lines)} files)")
