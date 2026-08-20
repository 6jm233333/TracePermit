import json
import unittest

from scripts.evaluate import compute_metrics
from scripts.infer import heuristic_action, render_prompt
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
        self.assertEqual(manifest["train_records"], 288)
        self.assertEqual(manifest["validation_records"], 96)


if __name__ == "__main__":
    unittest.main()
