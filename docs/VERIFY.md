# Manual validation checklist

This checklist is intentionally reproducible. It does **not** claim a production deployment or external user adoption.

## Prerequisites

- [ ] GitHub Actions enabled in the repository
- [ ] Trusted default-branch workflow installed
- [ ] Current default-branch `.changegate.json` has real reviewer usernames
- [ ] An enforced branch ruleset requires the `vote-gate` check

## Case A — Unprotected documentation PR

1. Open a PR touching only a file under `docs/` (not protected by the sample policy).
2. Inspect the `ChangeGate / vote-gate` job in the PR Checks tab.
3. Expect status **PASS** with the message `No protected files changed; vote gate is not required.`
4. Record the real workflow URL and whether the PR could be merged.

## Case B — Protected code PR without approvals

1. Open a PR editing `changegate/check.py` (or a path matching your policy).
2. Confirm there are **zero eligible current approvals**.
3. Expect status **BLOCK** and a nonzero exit code. Do not bypass the gate.
4. Record the real workflow URL.

## Case C — Protected PR with valid human approval

1. Invite a real second maintainer or collaborator and add them to the *trusted policy on the default branch* before testing.
2. Have that person review and explicitly approve the current PR head commit.
3. Inspect the next `ChangeGate / vote-gate` run; expect PASS if the required vote count is satisfied.
4. Push another commit to the PR; expect previous approval to become stale and the check to block again (if `require_latest_commit` is true).

Do not manufacture review accounts, stars, external downloads or user testimonials to claim adoption. Link to observed GitHub checks when documenting test outcomes.
