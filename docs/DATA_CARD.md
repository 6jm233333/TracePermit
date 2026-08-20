# TracePermit Data Card

## Summary

TracePermit is a de-identified benchmark for contextual release decisions in an aviation-engineering language-assistance setting. Each record contains five decision fields: request, engineering context, proxy cyber evidence, access scope, and candidate output. The reference action is one of `allow`, `review`, or `block`.

## Provenance

Compact engineering context is associated with C-MAPSS, PHM08, and N-CMAPSS; HAI 22.04 provides proxy industrial-control cyber context. These upstream datasets do not provide TracePermit release-action labels. A study-defined contextual category is also used and is not an independent upstream dataset.

The public release does not redistribute raw upstream records. It omits raw source values, timestamps, native HAI `Attack` labels, original source identifiers, source filenames, raw source metadata, and trace-to-source mappings.

The machine-readable provenance and rights snapshots are in `manifests/provenance.json` and `manifests/rights.json`.

## Annotation

All 600 core traces were independently labelled by three qualified aircraft-engine experts under the written study policy. Experts were blinded to model predictions and to one another's initial labels and provided written rationales for `review` and `block` decisions. Majority labels were checked against the written policy; three-way disagreements and safety-critical cases were referred to a senior adjudicator.

Pre-adjudication nominal inter-rater reliability was Krippendorff's α = 0.79. Final core labels comprise 167 `allow`, 233 `review`, and 200 `block` cases. Individual rater records, adjudication histories, and written rationales are not included in the public release.

Separately, two independent blinded domain experts assessed the semantics of 14 policy clauses. Exact agreement was 14/14 for both the permitted-action-set and resolution-status endpoints. This clause-level assessment is distinct from trace-label reliability.

## Stress records

The 1,472 contextual-stress reference actions were obtained by reapplying the study policy after predefined contextual transformations; no second trace-by-trace expert annotation round was performed for these records.

Development and held-out branches are separated at the stored pre-transformation grouping-unit level before transformations are applied. The held-out known-stress set contains 320 traces: 80 each for access-scope flip, cyber-status flip, output-sensitivity flip, and prompt-injection insertion.

The isolation claim is limited to the stored grouping level because original source-document identifiers are not released.

## Public schema

See `data/data_dictionary.csv`. `counterfactual_group_id` and `parent_counterfactual_group_id` are release-specific grouping identifiers and are not original source identifiers.

## Intended use

The release is intended for research on contextual release control, direction-sensitive evaluation, group-isolated stress testing, and reproducible re-aggregation of the accompanying controller outcomes.

## Out of scope

The dataset is not an operational aviation standard, certification artifact, access-control system, forensic cyber dataset, or substitute for specialist engineering review. It should not be interpreted as evidence of deployment readiness or universal aviation ground truth.

## Upstream references

- Saxena, A., Goebel, K., Simon, D., & Eklund, N. (2008). *Damage propagation modeling for aircraft engine run-to-failure simulation*. IEEE PHM. DOI: 10.1109/PHM.2008.4711414.
- Arias Chao, M., Kulkarni, C., Goebel, K., & Fink, O. (2021). *Aircraft engine run-to-failure dataset under real flight conditions for prognostics and diagnostics*. Data, 6(1), 5. DOI: 10.3390/data6010005.
- Shin, H.-K., Lee, W., Yun, J.-H., & Min, B.-G. (2021). *Two ICS security datasets and anomaly detection contest on the HIL-based augmented ICS testbed*. CSET. DOI: 10.1145/3474718.3474719.

Raw upstream datasets are not redistributed or relicensed by this repository and remain subject to their original terms.
