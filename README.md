# Codex ChangeGate

**Require trusted human approval for sensitive pull requests in AI-assisted teams.**

![Status](https://img.shields.io/badge/status-early%20prototype-orange)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Codex ChangeGate is a small, open-source GitHub pull-request voting gate. It can
be used with Codex or any other AI coding tool; no OpenAI account, paid API or
AI provider is required to run it.

## The problem

When AI coding tools make it easy to submit large changes quickly, teams still
need explicit human review of changes to infrastructure, CI, authentication,
and security-critical code. ChangeGate can **block a required CI check** until a
configurable number of trusted reviewers approve the current PR commit.

This is an independent community project and is not affiliated with OpenAI.

## Features

- Protect paths using glob patterns (e.g. `infra/**`).
- Maintain an explicit list of trusted GitHub reviewer usernames.
- Require N valid approvals on protected changes.
- Ignore stale approvals after new commits, by default.
- Prevent the PR author from voting on their own changes, by default.
- Handle changes-requested/dismissed reviews and renamed paths.
- Use the standard GitHub pull request review UI; no bot installation required.
- Python standard library only at runtime; read-only GitHub API calls.
- Offline test fixtures for demonstrations and unit tests.

## Quick demonstration (no GitHub token needed)

From the repository root:

```bash
python -m changegate check \
  --config examples/sample-policy.json \
  --fixture examples/approved-pr.json
# PASS — 2 trusted approvals

python -m changegate check \
  --config examples/sample-policy.json \
  --fixture examples/blocked-pr.json
# BLOCK — 0 valid fresh approvals (exit code 1)

python -m unittest discover -s tests -v
```

**The example approvals above are synthetic fixture data, not actual user reviews.**

## Guided onboarding and observed checks

For a step-by-step installation with real human reviewers and enforced branch rules,
see the [setup guide](docs/SETUP.md) and [verification checklist](docs/VERIFY.md).

The maintainer's initial public end-to-end checks are documented in GitHub:

- [PR #1](https://github.com/habahe2895-cpu/codex-changegate/pull/1):
  documentation-only change, with successful `unit-tests` and `vote-gate` checks.
- [PR #2](https://github.com/habahe2895-cpu/codex-changegate/pull/2):
  protected policy change with successful unit tests and intentionally failed
  `vote-gate` while no eligible independent reviewer has approved it.

These demonstrations do not establish production security or external adoption.
For feedback or volunteer testing, see [issue #3](https://github.com/habahe2895-cpu/codex-changegate/issues/3).

## Using in a GitHub repository

1. Copy `changegate/`, `.changegate.json` and
   `.github/workflows/changegate.yml` into the repository's default branch.
2. Edit `.changegate.json` to add **real trusted GitHub reviewers**. The bundled
   default is an initial example for the project's creator; for a team,
   configure the actual members and your desired quorum.
3. Open a PR touching a protected path. ChangeGate runs and blocks until the
   required reviewers submit `Approve` on the current PR commit.
4. **Mandatory:** In repository Settings, create a branch ruleset / branch
   protection for `main`, requiring the **`vote-gate`** status check from the
   `ChangeGate` workflow before merge. Without this, an authorized collaborator
   may still merge even if the workflow reports `BLOCK`.
5. The bundled `.changegate.json` is itself a protected path. Keep it protected
   in your own policy too, so PRs cannot modify the trusted voter list without
   valid approvals.

For public repositories, GitHub Actions supports this workflow subject to
GitHub's normal plan and permissions rules.

### Example policy

```json
{
  "version": 1,
  "protected_patterns": ["infra/**", ".github/workflows/**"],
  "voters": ["alice", "bob", "carol"],
  "minimum_approvals": 2,
  "require_latest_commit": true,
  "allow_author_vote": false
}
```

A modified PR must get two approvals from the named people. Approvals are
counted only when each review belongs to the PR's current head commit.
`CHANGES_REQUESTED` and `DISMISSED` are treated as revoking that reviewer's
previous approval. A `COMMENTED` review does not change their approval state.

**One-maintainer note:** If you authored the PR and only you are in `voters`,
the gate intentionally cannot approve your own protected PR. Invite a trusted
collaborator and edit the voter list before using this on solo-authored PRs.

### Manual command for real pull requests

```bash
export GITHUB_TOKEN="<read-only GitHub token>"
python -m changegate check --repo OWNER/REPO --pr 123 --config .changegate.json
```

The token should have read access to pull requests and contents. In the
included workflow GitHub provides the limited `GITHUB_TOKEN` automatically;
you do **not** need to create or paste a personal access token.

## Threat model and limitations

- Always run the gate from trusted default-branch code, not the PR branch.
- The gate never executes submitted code or makes write API calls.
- Repository owners/admins can change rules; this is a workflow approval guard,
  not an independent security boundary.
- GitHub review and job permissions determine who can act in a given repository.
- It is **not** a replacement for code review, security scanning, or branch
  protection. See [SECURITY.md](SECURITY.md).

## Roadmap

- [ ] Web UI to track voters and pending approvals across multiple PRs.
- [ ] GitHub App distribution and improved installation flow.
- [ ] Teams/org voter policy without manually enumerating usernames.
- [ ] Signed policy and richer audit-log export.
- [ ] Test against production repositories and gather feedback.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues, bug reports and code contributions
are welcome. See also [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
