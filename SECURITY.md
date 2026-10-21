# Security policy

This is an early-stage project; security review is welcome. Do not put tokens,
secrets, or private repository details in public issues. Please use GitHub's
private vulnerability reporting feature if enabled by the repository owner.

## Safety model

- The gate uses only GitHub **read** endpoints.
- The GitHub Actions gate checks out code and policy from the **default branch**,
  not from the PR head, and does not execute PR-provided code.
- Only explicitly listed GitHub usernames can supply votes.
- Changes to protected paths (including the policy file itself) require up-to-date PR approvals.
- An approval alone does not prevent merging. Configure branch protection / a
  repository ruleset requiring the `ChangeGate / vote-gate` status check.

## Important limitations

- Repository administrators can modify branch rules or trusted policy. The tool
  cannot protect against compromised repository administrators.
- This is not a security scanner and does not evaluate the quality of changes.
- If the configuration file is accidentally removed from the default branch,
  the action fails instead of silently approving.
- Avoid allowing self-approvals for production-critical rules.
