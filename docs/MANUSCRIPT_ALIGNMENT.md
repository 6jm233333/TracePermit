# Manuscript and public-artifact alignment

This note maps the public TracePermit companion release to the manuscript
**"TracePermit: Context-Complete Release Control for LLM Assistance in
Safety-Critical Engineering."** It is intended to help reviewers distinguish
claims that can be checked directly from the public release from claims that
depend on bounded private construction or annotation records.

## Publicly verifiable results

| Manuscript component | Public files | Verification route |
| --- | --- | --- |
| Seven split sizes and 2,072 total traces | `data/tracepermit_benchmark.jsonl` | `python scripts/verify_release.py` |
| 600 core traces, 200 stored groups, 167/233/200 adjudicated actions | `data/tracepermit_benchmark.jsonl` | `python scripts/verify_release.py` |
| Development/held-out stored-group isolation | `counterfactual_group_id`, `parent_counterfactual_group_id`, and `split` fields | `python scripts/verify_release.py` |
| Four held-out stress families with 80 traces each | `declared_transformation` in the benchmark | `python scripts/verify_release.py` |
| Rule-Conservative held-out results and supplementary confusion matrices | `outcomes/rule_conservative_outcomes.jsonl` | `python scripts/summarize_results.py` and direct count aggregation |
| Eighteen learned model-seed-condition cells and supplementary count table | `outcomes/learned_heldout_outcomes.jsonl` | `python scripts/summarize_results.py` and direct count aggregation |
| Complete-trace masking cross-check | learned outcomes plus `results/masking_summary.csv` | `python scripts/verify_release.py` |
| File integrity and record digests | `CHECKSUMS.sha256` and `record_sha256` | `python scripts/verify_release.py` |

Running the following commands validates the release and regenerates the
aggregate controller tables without downloading model weights:

```bash
python scripts/verify_release.py
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

## Bounded non-public evidence

The released benchmark intentionally omits raw upstream rows, source filenames,
native timestamps, original identifiers, trace-to-source mappings, individual
rater records, written annotation rationales, private checkpoints, and the
complete private training/inference runtime. Consequently, the public release
does not independently verify raw-source-document independence, source-family
allocation of every transformed trace, individual-rater decisions, or bitwise
reproduction of private model execution.

The manuscript and supplementary material report source-construction counts,
expert qualifications, the pre-adjudication reliability statistic, and the
hardware/software environment as study records. These claims should be read
together with the limitations in `docs/DATA_CARD.md`,
`docs/REPRODUCIBILITY.md`, and `docs/MODEL_ACCESS.md`.

## Frozen release boundary

The GitHub tag `v1.0.0` is the frozen public data/code release point. Later
documentation-only changes on the default branch do not change the benchmark,
outcome files, policy, or reported numerical results. Submission manuscripts
and journal-formatted PDFs are maintained separately from this public release
tree so that the repository remains a compact verification artifact.
