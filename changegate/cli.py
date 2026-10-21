"""Command line interface for Codex ChangeGate."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .check import evaluate
from .github import GitHubClient, GitHubError
from .policy import PolicyError, load_policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Require trusted votes for protected PR changes")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Check approval policy against PR reviews")
    check.add_argument("--config", default=".changegate.json", help="Trusted JSON policy path")
    check.add_argument("--repo", help="GitHub owner/repo (required without --fixture)")
    check.add_argument("--pr", type=int, help="Pull request number (required without --fixture)")
    check.add_argument("--fixture", help="Offline example JSON file; does not connect to GitHub")
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = load_policy(args.config)
        if args.fixture:
            with Path(args.fixture).open(encoding="utf-8") as fh:
                fixture: dict[str, Any] = json.load(fh)
            author = fixture["author"]
            head_sha = fixture["head_sha"]
            files = fixture["files"]
            reviews = fixture["reviews"]
            if not (isinstance(files, list) and isinstance(reviews, list)):
                raise ValueError("Fixture files and reviews must be lists")
        else:
            if not args.repo or not args.pr:
                raise ValueError("Both --repo and --pr are required without --fixture")
            client = GitHubClient(os.getenv("GITHUB_TOKEN", ""), args.repo)
            pr = client.pull_request(args.pr)
            author = pr["user"]["login"]
            head_sha = pr["head"]["sha"]
            files = client.changed_files(args.pr)
            reviews = client.reviews(args.pr)

        result = evaluate(policy, author=author, head_sha=head_sha,
                          files=files, reviews=reviews)
        print("PASS" if result.passed else "BLOCK")
        print(result.explanation)
        if result.protected_files:
            print("Protected files: " + ", ".join(result.protected_files))
            print("Valid voters: " + (", ".join(result.approvals) or "none"))
        return 0 if result.passed else 1
    except (OSError, ValueError, KeyError, TypeError, GitHubError, PolicyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def main() -> int:
    return run()
