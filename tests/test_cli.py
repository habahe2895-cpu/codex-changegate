"""Integration-style checks for documented offline CLI examples."""

import contextlib
import io
import unittest
from pathlib import Path

from changegate.cli import run


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "examples" / "sample-policy.json"


class CliFixtureTests(unittest.TestCase):
    def execute(self, fixture):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = run([
                "check", "--config", str(POLICY), "--fixture", str(fixture)
            ])
        return result, out.getvalue(), err.getvalue()

    def test_approved_example_returns_success(self):
        code, stdout, stderr = self.execute(ROOT / "examples" / "approved-pr.json")
        self.assertEqual(0, code)
        self.assertIn("PASS", stdout)
        self.assertIn("received 2 valid approval(s)", stdout)
        self.assertEqual("", stderr)

    def test_blocked_example_returns_failure(self):
        code, stdout, stderr = self.execute(ROOT / "examples" / "blocked-pr.json")
        self.assertEqual(1, code)
        self.assertIn("BLOCK", stdout)
        self.assertIn("received 0 valid approval(s)", stdout)
        self.assertEqual("", stderr)

    def test_missing_fixture_is_an_error(self):
        code, stdout, stderr = self.execute(ROOT / "examples" / "does-not-exist.json")
        self.assertEqual(2, code)
        self.assertEqual("", stdout)
        self.assertIn("ERROR", stderr)


if __name__ == "__main__":
    unittest.main()
