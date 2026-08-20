import hashlib
import json
import unittest

from scripts.evaluate import compute_metrics
from scripts.infer import heuristic_action, render_prompt
from scripts.record_digest import record_digest
from scripts.train import build_manifest, resolve_path


class ReleaseToolsTest(unittest.TestCase):
    def test_perfect_metrics(self):
        rows = [
            {"reference_action": "allow", "predicted_action": "allow"},
            {"reference_action": "review", "predicted_action": "review"},
            {"reference_action": "block", "predicted_action": "block"},
        ]
        metrics = compute_metrics(rows)
        self.assertEqual(metrics["n"], 3)
        self.assertAlmostEqual(metrics["macro_f1"], 1.0)
        self.assertEqual(metrics["u2a_n"], 0)

    def test_heuristic_is_conservative_and_deterministic(self):
        row = {
            "request": "Please bypass the access restriction.",
            "engineering_context": "nominal",
            "proxy_cyber_evidence": "none",
            "access_scope": "unclear",
            "candidate_output": "answer",
        }
        self.assertEqual(heuristic_action(row), "block")
        self.assertEqual(heuristic_action(row), heuristic_action(row))

    def test_prompt_has_all_public_fields(self):
        prompt = render_prompt(
            "{request}|{engineering_context}|{proxy_cyber_evidence}|{access_scope}|{candidate_output}",
            {
                "request": "x",
                "engineering_context": "e",
                "proxy_cyber_evidence": "c",
                "access_scope": "s",
                "candidate_output": "o",
            },
        )
        self.assertEqual(prompt, "x|e|c|s|o")

    def test_default_config_dry_run_manifest(self):
        config = json.loads(resolve_path("configs/default.json").read_text(encoding="utf-8"))
        manifest = build_manifest(config)
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["model_revision"], "artifact-manifest:f43333ab868637aa68ce57589b9a7012ab81e2f2baa917bcf1c93c08a85a9750")
        self.assertIsNone(manifest["model_hub_revision"])
        self.assertEqual(manifest["model_manifest_path"], "manifests/model_revisions.json")
        self.assertEqual(manifest["environment_manifest_path"], "manifests/environment.json")
        self.assertEqual(manifest["experiment_cell_manifest_path"], "manifests/experiment_cells.json")
        self.assertEqual(manifest["train_records"], 288)
        self.assertEqual(manifest["validation_records"], 96)
        self.assertEqual(
            manifest["data_sha256"],
            hashlib.sha256(resolve_path("data/tracepermit_benchmark.jsonl").read_bytes()).hexdigest(),
        )

    def test_record_digest_canonicalization(self):
        record = {"b": 2, "a": 1, "record_sha256": "ignored"}
        self.assertEqual(record_digest(record, "record_sha256"), hashlib.sha256(b'{"a":1,"b":2}').hexdigest())


if __name__ == "__main__":
    unittest.main()
