#!/usr/bin/env python3
"""Config-driven optional LoRA training entry point.

The public release does not contain the private training runtime or model
weights. ``--dry-run`` is therefore the default-safe path and only builds a
manifest from the released data. ``--run`` requires the optional
Transformers/Datasets/PEFT stack and downloads the model named in the config.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_path(value: str, root: Path = ROOT) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_prompt(template: str, row: dict) -> str:
    return template.format(
        request=row["request"],
        engineering_context=row["engineering_context"],
        proxy_cyber_evidence=row["proxy_cyber_evidence"],
        access_scope=row["access_scope"],
        candidate_output=row["candidate_output"],
    )


def build_manifest(config: dict) -> dict:
    data_path = resolve_path(config["data_path"])
    data = read_jsonl(data_path)
    train = [row for row in data if row["split"] == config["train_split"]]
    validation = [row for row in data if row["split"] == config["validation_split"]]
    prompt = resolve_path(config["prompt_path"]).read_text(encoding="utf-8")
    return {
        "version": config["version"],
        "model_id": config["model_id"],
        "model_revision": config.get("model_revision"),
        "model_hub_revision": config.get("model_hub_revision"),
        "model_artifact_manifest_sha256": config.get("model_artifact_manifest_sha256"),
        "model_manifest_path": config.get("model_manifest_path"),
        "environment_manifest_path": config.get("environment_manifest_path"),
        "experiment_cell_manifest_path": config.get("experiment_cell_manifest_path"),
        "train_split": config["train_split"],
        "validation_split": config["validation_split"],
        "train_records": len(train),
        "validation_records": len(validation),
        "seed": config["seed"],
        "max_seq_length": config["max_seq_length"],
        "num_train_epochs": config["num_train_epochs"],
        "per_device_train_batch_size": config["per_device_train_batch_size"],
        "gradient_accumulation_steps": config["gradient_accumulation_steps"],
        "learning_rate": config["learning_rate"],
        "lora_r": config["lora_r"],
        "lora_alpha": config["lora_alpha"],
        "lora_dropout": config["lora_dropout"],
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "data_sha256": sha256_file(data_path),
    }


def run_training(config: dict, output_dir: Path) -> None:
    hub_revision = config.get("model_hub_revision")
    if not hub_revision:
        raise SystemExit(
            "The release config records a content-addressed private model manifest, "
            "not a provider checkout revision. Supply an immutable provider commit "
            "in model_hub_revision before using --run."
        )
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, TaskType, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    except ImportError as exc:
        raise SystemExit(
            "Optional training dependencies are missing. Install the versions "
            "listed in docs/TRAINING_INFERENCE_EVALUATION.md and retry --run."
        ) from exc

    random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    data = read_jsonl(resolve_path(config["data_path"]))
    template = resolve_path(config["prompt_path"]).read_text(encoding="utf-8")
    train_rows = [row for row in data if row["split"] == config["train_split"]]
    validation_rows = [row for row in data if row["split"] == config["validation_split"]]

    tokenizer = AutoTokenizer.from_pretrained(
        config["model_id"],
        revision=hub_revision,
        trust_remote_code=config.get("trust_remote_code", False),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        config["model_id"],
        revision=hub_revision,
        trust_remote_code=config.get("trust_remote_code", False),
    )
    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        target_modules=config["lora_target_modules"],
    )
    model = get_peft_model(model, lora)

    def tokenize(row):
        text = render_prompt(template, row) + "\nAnswer: " + row["reference_action"]
        encoded = tokenizer(
            text,
            max_length=config["max_seq_length"],
            truncation=True,
            padding="max_length",
        )
        encoded["labels"] = list(encoded["input_ids"])
        return encoded

    train_ds = Dataset.from_list(train_rows)
    validation_ds = Dataset.from_list(validation_rows)
    train_ds = train_ds.map(tokenize, remove_columns=train_ds.column_names)
    validation_ds = validation_ds.map(tokenize, remove_columns=validation_ds.column_names)
    args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        per_device_eval_batch_size=config["per_device_eval_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        learning_rate=config["learning_rate"],
        warmup_ratio=config["warmup_ratio"],
        logging_steps=config["logging_steps"],
        evaluation_strategy="epoch",
        save_strategy="epoch",
        report_to="none",
        seed=config["seed"],
        bf16=bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported()),
    )
    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=validation_ds)
    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    (output_dir / "training_manifest.json").write_text(
        json.dumps(build_manifest(config), indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="TracePermit optional LoRA trainer")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "default.json")
    parser.add_argument("--run", action="store_true", help="download the configured model and train")
    parser.add_argument("--output-dir", type=Path, help="override config output_dir")
    args = parser.parse_args()
    config = load_json(resolve_path(str(args.config)))
    manifest = build_manifest(config)
    if not args.run:
        print(json.dumps({"mode": "dry-run", **manifest}, indent=2))
        return
    output_dir = args.output_dir or resolve_path(config["output_dir"])
    run_training(config, output_dir)


if __name__ == "__main__":
    main()
