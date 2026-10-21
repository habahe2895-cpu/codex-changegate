"""Pure vote evaluation logic. No tokens or network calls here."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import Any, Mapping, Sequence

from .policy import Policy


@dataclass(frozen=True)
class Decision:
    passed: bool
    protected_files: tuple[str, ...]
    approvals: tuple[str, ...]
    minimum_approvals: int
    explanation: str


def _login(review: Mapping[str, Any]) -> str:
    user = review.get("user")
    if not isinstance(user, dict):
        return ""
    login = user.get("login")
    return login.casefold() if isinstance(login, str) else ""


def evaluate(
    policy: Policy, *, author: str, head_sha: str,
    files: Sequence[str], reviews: Sequence[Mapping[str, Any]],
) -> Decision:
    """Evaluate GitHub reviews for protected files.

    Only the latest *decisive* review (APPROVED, CHANGES_REQUESTED or
    DISMISSED) per person is considered. COMMENTED is ignored.
    Reviews are sorted by GitHub review ID to handle out-of-order API results.
    """
    if not author or not head_sha:
        raise ValueError("PR author and head_sha are required")

    protected = tuple(sorted({name for name in files if any(
        fnmatchcase(name, pattern) for pattern in policy.protected_patterns
    )}))
    if not protected:
        return Decision(True, (), (), policy.minimum_approvals,
                        "No protected files changed; vote gate is not required.")

    latest: dict[str, Mapping[str, Any]] = {}
    ordered = sorted(reviews, key=lambda item: int(item.get("id") or 0))
    for review in ordered:
        who = _login(review)
        state = str(review.get("state") or "").upper()
        if who and state in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[who] = review

    approvals = []
    for who, review in latest.items():
        if who not in policy.voters:
            continue
        if not policy.allow_author_vote and who == author.casefold():
            continue
        if str(review.get("state") or "").upper() != "APPROVED":
            continue
        if policy.require_latest_commit and review.get("commit_id") != head_sha:
            continue
        approvals.append(who)

    approvals.sort()
    passed = len(approvals) >= policy.minimum_approvals
    explanation = (
        f"Protected changes require {policy.minimum_approvals} trusted approval(s); "
        f"received {len(approvals)} valid approval(s)."
    )
    return Decision(passed, protected, tuple(approvals),
                    policy.minimum_approvals, explanation)
