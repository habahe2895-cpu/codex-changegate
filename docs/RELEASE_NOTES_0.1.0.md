# v0.1.0 — Release notes (draft)

**Status:** Alpha prototype. This document is release preparation, not evidence that a GitHub Release has already been published.

## Features

- Rules-based high-risk PR file protection (JSON policy).
- Trusted GitHub reviewer quorum and self-vote protection.
- Current-commit approval validation and review revocation.
- GitHub Actions ChangeGate checks on pull requests.
- Read-only GitHub API integration with no runtime third-party Python dependencies.
- MIT-licensed Python source, English/Chinese README and onboarding docs.

## Validation

- 20 automated unit and CLI integration tests currently pass on the default branch.
- PR #1: live GitHub `unit-tests` and `vote-gate` checks passed for unprotected changes.
- PR #2: live `unit-tests` passed and `vote-gate` failed as expected for an unapproved protected policy change; this PR intentionally remains open.
- Independent human-approval transition **not yet validated**. Branch ruleset enforcement **not yet verified**.

## Known limitations

- Manual installation into each repository; not yet a distributed GitHub App.
- Voters are a manually maintained list of GitHub usernames.
- A solo maintainer cannot approve their own protected PR if `allow_author_vote` is false.
- Branch ruleset/protection must explicitly require the `vote-gate` check.
- No external user adoption or production rollout established.

## Installation

Follow [docs/SETUP.md](SETUP.md) and [docs/VERIFY.md](VERIFY.md).

## Before publishing a GitHub Release

Create a tag `v0.1.0` pointing to the final audited default-branch commit, mark the release **Pre-release**, and use the above notes. Verify the final Actions run first. Do not include open PR #2 code in the release unless it has actually been merged.
