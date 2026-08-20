#!/usr/bin/env python3
"""Run a transparent baseline or an optional Transformers model."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"allow", "review", "block"}


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def render_prompt(template: str, row: dict) -> str:
    return template.format(
        request=row["request"],
        engineering_context=row["engineering_context"],
        proxy_cyber_evidence=row["proxy_cyber_evidence"],
        access_scope=row["access_scope"],
        candidate_output=row["candidate_output"],
    )


def heuristic_action(row: dict) -> str:
    """A conservative, non-trained demonstration baseline."""
    text = " ".join(str(row[field]).lower() for field in (
        "request", "engineering_context", "proxy_cyber_evidence", "access_scope", "candidate_output"
    ))
    block_terms = ("unauthorized", "prohibited", "bypass", "malware", "exfiltrat", "credential", "secret")
    review_terms = ("unclear", "uncertain", "ambiguous", "conflicting", "unknown", "restricted", "prompt injection")
    if any(term in text for term in block_terms):
        return "block"
    if any(term in text for term in review_terms):
        return "review"
    return "allow"


def transformer_actions(rows, template: str, model_id: str, revision: str, trust_remote_code: bool, max_new_tokens: int):
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise SystemExit(
            "Transformers is not installed. Use --mode heuristic or install the optional ML stack."
        ) from exc
    generator = pipeline(
        "text-generation",
        model=model_id,
        revision=revision,
        trust_remote_code=trust_remote_code,
        device_map="auto",
    )
    outputs = []
    for row in rows:
        prompt = render_prompt(template, row)
        result = generator(prompt, max_new_tokens=max_new_tokens, do_sample=False, return_full_text=False)
        text = result[0]["generated_text"] if result else ""
        match = re.search(r"\b(allow|review|block)\b", text.lower())
        outputs.append(match.group(1) if match else "review")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="TracePermit inference")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "tracepermit_benchmark.jsonl")
    parser.add_argument("--split", default="test")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "predictions.jsonl")
    parser.add_argument("--mode", choices=("heuristic", "transformers"), default="heuristic")
    parser.add_argument("--model-id", default="Qwen/Qwen3-14B")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts" / "release_decision_v1.txt")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = [row for row in read_jsonl(args.input) if row["split"] == args.split]
    if args.limit is not None:
        rows = rows[: args.limit]
    template = args.prompt.read_text(encoding="utf-8")
    print(json.dumps({"mode": args.mode, "split": args.split, "records": len(rows), "model_id": args.model_id}, indent=2))
    if args.dry_run:
        return
    if args.mode == "heuristic":
        actions = [heuristic_action(row) for row in rows]
    else:
        actions = transformer_actions(rows, template, args.model_id, args.revision, args.trust_remote_code, 8)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for row, action in zip(rows, actions):
            if action not in ACTIONS:
                raise SystemExit(f"Invalid action generated for {row['record_id']}: {action}")
            handle.write(json.dumps({
                "record_id": row["record_id"],
                "split": row["split"],
                "reference_action": row["reference_action"],
                "predicted_action": action,
                "mode": args.mode,
                "model_id": args.model_id if args.mode == "transformers" else None,
            }) + "\n")


if __name__ == "__main__":
    main()
