"""Ensure packaging metadata is guarded against unreviewed PR changes."""

import unittest
from pathlib import Path

from changegate.check import evaluate
from changegate.policy import load_policy


class ProtectedMetadataTests(unittest.TestCase):
    def test_build_configuration_is_protected(self):
        policy_path = Path(__file__).resolve().parents[1] / ".changegate.json"
        result = evaluate(
            load_policy(policy_path),
            author="contributor",
            head_sha="head-1",
            files=["pyproject.toml"],
            reviews=[],
        )
        self.assertFalse(result.passed)
        self.assertEqual(("pyproject.toml",), result.protected_files)


if __name__ == "__main__":
    unittest.main()
