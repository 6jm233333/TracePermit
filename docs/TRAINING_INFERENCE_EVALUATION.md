# Training, inference and evaluation entry points

The public package exposes a small, auditable reproduction layer. It is
designed to run on the released de-identified traces and frozen outcomes; the
private training runtime, model caches, adapters and original upstream inputs
are not part of this release.

## Minimal checks

```bash
python scripts/verify_release.py
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

## Configuration and prompt

`configs/default.json` fixes the public example configuration: version 1.0.0,
seed 2026, 1 epoch, batch size 1, gradient accumulation 8, learning rate
2e-4, maximum sequence length 1,024, and LoRA `(r, alpha, dropout) =
(16, 32, 0.05)`. `prompts/release_decision_v1.txt` serializes the five public
trace fields and requires one of `allow`, `review`, or `block` as the output.

## Training

Inspect the data counts and prompt hash without downloading a model:

```bash
python scripts/train.py --config configs/default.json
```

An actual LoRA run is opt-in and requires a compatible GPU environment:

```bash
python -m pip install -r requirements-ml.txt
python scripts/train.py --config configs/default.json --run
```

The script uses only `core_train` and `core_validation`, writes an explicit
training manifest, and never claims that its output reproduces the private
camera-ready checkpoints. Adjust model-specific LoRA target modules in the
config when the selected architecture uses different names.

The public default config records a content-addressed model manifest in
`model_revision`; set `model_hub_revision` to an immutable provider commit
before invoking `--run`.

## Inference

The standard-library demonstration baseline is deterministic and needs no
weights:

```bash
python scripts/infer.py --mode heuristic --split test \
  --output artifacts/heuristic_test.jsonl
```

For a locally downloaded Hugging Face model, use the optional Transformers
path and record the exact model revision in your run notes:

```bash
python scripts/infer.py --mode transformers --model-id Qwen/Qwen3-14B \
  --revision <immutable-provider-commit> --split heldout_known_stress \
  --output artifacts/qwen3_predictions.jsonl
```

The heuristic is a runnable demonstration only; it is not the manuscript's
frozen Rule-Conservative result. A generated action that cannot be parsed is
mapped to `review` as a conservative parsing fallback.

The Transformers path rejects placeholder revisions such as the release
config's content-manifest token; `--revision` must be an actual provider commit.

## Evaluation

Evaluate any prediction JSONL with `reference_action` and `predicted_action`:

```bash
python scripts/evaluate.py artifacts/heuristic_test.jsonl
```

The evaluator reports Macro-F1, U2A, B2A, review burden, and denominators. For
the manuscript's frozen controller comparisons, use
`python scripts/summarize_results.py`; it consumes the released per-trace
outcomes and is independent of the optional model stack.
