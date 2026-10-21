import unittest

from changegate.check import evaluate
from changegate.policy import PolicyError, parse_policy


BASE = {
    "version": 1,
    "protected_patterns": ["infra/**", ".github/workflows/**"],
    "voters": ["alice", "bob", "carol"],
    "minimum_approvals": 2,
    "require_latest_commit": True,
    "allow_author_vote": False,
}


def vote(identifier, login, state="APPROVED", commit="current"):
    return {
        "id": identifier,
        "user": {"login": login},
        "state": state,
        "commit_id": commit,
    }


def check(files=("infra/deploy.yaml",), reviews=(), author="contributor", head="current", policy=None):
    return evaluate(policy or parse_policy(BASE), author=author, head_sha=head,
                    files=files, reviews=reviews)


class PolicyTests(unittest.TestCase):
    def test_rejects_duplicate_voters(self):
        with self.assertRaises(PolicyError):
            parse_policy({**BASE, "voters": ["Alice", "alice"]})

    def test_rejects_impossible_quorum(self):
        with self.assertRaises(PolicyError):
            parse_policy({**BASE, "minimum_approvals": 4})

    def test_rejects_bool_as_integer_quorum(self):
        with self.assertRaises(PolicyError):
            parse_policy({**BASE, "minimum_approvals": True})

    def test_rejects_unknown_policy_key(self):
        with self.assertRaises(PolicyError):
            parse_policy({**BASE, "extra": True})


class GateTests(unittest.TestCase):
    def test_unprotected_changes_pass(self):
        result = check(files=("docs/intro.md",))
        self.assertTrue(result.passed)
        self.assertEqual(result.protected_files, ())

    def test_requires_quorum(self):
        self.assertFalse(check(reviews=[vote(1, "alice")]).passed)
        self.assertTrue(check(reviews=[vote(1, "alice"), vote(2, "bob")]).passed)

    def test_stale_approval_not_counted(self):
        self.assertFalse(check(reviews=[vote(1, "alice", commit="old"), vote(2, "bob")]).passed)

    def test_latest_change_request_revokes_approval(self):
        self.assertFalse(check(reviews=[vote(1, "alice"), vote(2, "bob"),
                                        vote(3, "alice", state="CHANGES_REQUESTED")]).passed)

    def test_dismissed_revokes_approval(self):
        self.assertFalse(check(reviews=[vote(1, "alice"), vote(2, "bob"),
                                        vote(3, "alice", state="DISMISSED")]).passed)

    def test_comment_does_not_revoke_approval(self):
        self.assertTrue(check(reviews=[vote(1, "alice"), vote(2, "bob"),
                                       vote(3, "alice", state="COMMENTED")]).passed)

    def test_untrusted_voters_do_not_count(self):
        self.assertFalse(check(reviews=[vote(1, "alice"), vote(2, "mallory")]).passed)

    def test_author_cannot_approve(self):
        self.assertFalse(check(author="alice", reviews=[vote(1, "alice"), vote(2, "bob")]).passed)

    def test_case_insensitive_voters(self):
        self.assertTrue(check(reviews=[vote(1, "ALICE"), vote(2, "Bob")]).passed)

    def test_ignore_order_sort_by_id(self):
        self.assertFalse(check(reviews=[vote(8, "alice", state="CHANGES_REQUESTED"),
                                        vote(1, "alice"), vote(2, "bob")]).passed)

    def test_protects_ci_workflows(self):
        self.assertFalse(check(files=(".github/workflows/ci.yml",)).passed)

    def test_policy_file_is_protected_in_default_policy(self):
        from changegate.policy import load_policy
        from pathlib import Path
        config = Path(__file__).resolve().parents[1] / ".changegate.json"
        result = check(files=(".changegate.json",), policy=load_policy(config))
        self.assertFalse(result.passed)

    def test_self_approval_option(self):
        policy = parse_policy({**BASE, "allow_author_vote": True})
        self.assertTrue(check(author="alice", reviews=[vote(1, "alice"), vote(2, "bob")],
                              policy=policy).passed)


if __name__ == "__main__":
    unittest.main()
