# Reproducibility

## Public verification

The release is self-checking and requires only Python 3.10 or later:

```bash
python scripts/verify_release.py
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

The verifier checks record counts, schema, split membership, core-label totals, group-level development/held-out isolation, held-out stress-family counts, de-identification guards, outcome-to-benchmark joins, learned-condition completeness, validation-gate consistency, the complete-trace masking cross-check, and repository checksums.

## Re-aggregate reported outcomes

```bash
python scripts/summarize_results.py
```

This command recomputes Macro-F1, U2A, B2A, review burden, and the study-defined C-D cost from the released per-trace outcomes. Use:

```bash
python scripts/summarize_results.py --bootstrap 10000 --seed 2026
```

to add paired stored-group bootstrap intervals for the nine within-seed LoRA/Stress-LoRA comparisons.

## Experimental environment

The reported experiments used Ubuntu 22.04.5, 10 allocated AMD EPYC 7402 CPU cores, 52.9 GiB memory, one NVIDIA GeForce RTX 4090 GPU, Python 3.10.12, PyTorch 2.5.1+cu124, and CUDA 12.4. The recorded software stack also included Transformers 4.53.3, PEFT 0.13.2, bitsandbytes 0.45.5, Accelerate 1.13.0, Datasets 2.21.0, NumPy 2.2.6, pandas 2.3.3, and scikit-learn 1.7.2.

Model caches, adapters/checkpoints, raw upstream inputs, and the complete private training runtime are not distributed. The public package supports deterministic re-aggregation of the released outcomes; it does not claim bitwise retraining or inference reproduction.

## Masking and validation summaries

Per-trace masking and validation predictions are not distributed. `results/masking_summary.csv` and `results/validation_summary.csv` provide the corresponding aggregate research outputs. The complete-trace masking row is independently cross-checked against the released Qwen3-14B Stress-LoRA held-out outcomes by `verify_release.py`.

The optional training, inference, prompt, configuration, and model-access
instructions are collected in `docs/TRAINING_INFERENCE_EVALUATION.md` and
`docs/MODEL_ACCESS.md`. They document a reproducible public entry point, but
the private camera-ready training runtime and checkpoints are not distributed.
