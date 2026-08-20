#!/usr/bin/env python3
"""Create and verify per-record SHA-256 digests for released JSONL files.

The digest is computed from the UTF-8 JSON representation of one object after
removing the digest field, with object keys sorted and JSON separators fixed to
`,` and `:`.  The file itself is written as UTF-8 JSONL with one LF newline per
record.  This makes the digest independent of source-key order and platform
newline conversion while keeping the released record human-readable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def canonical_record_bytes(record: dict, digest_field: str) -> bytes:
    payload = {key: value for key, value in record.items() if key != digest_field}
    text = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return text.encode("utf-8")


def record_digest(record: dict, digest_field: str) -> str:
    return hashlib.sha256(canonical_record_bytes(record, digest_field)).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def check_jsonl(path: Path, digest_field: str) -> int:
    records = read_jsonl(path)
    for index, record in enumerate(records, start=1):
        observed = record.get(digest_field)
        expected = record_digest(record, digest_field)
        if not isinstance(observed, str) or observed.lower() != expected:
            raise ValueError(f"{path}:{index}: {digest_field} mismatch")
    return len(records)


def write_jsonl(path: Path, digest_field: str) -> int:
    records = read_jsonl(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            record.pop(digest_field, None)
            record[digest_field] = record_digest(record, digest_field)
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write or verify JSONL record SHA-256 digests")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--field", default="record_sha256")
    parser.add_argument("--write", action="store_true", help="write/recompute the digest field")
    args = parser.parse_args()

    for path in args.paths:
        count = write_jsonl(path, args.field) if args.write else check_jsonl(path, args.field)
        action = "wrote" if args.write else "verified"
        print(f"{action} {count} records: {path}")


if __name__ == "__main__":
    main()
