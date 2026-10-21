"""Validate the repository's trusted change approval policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Policy:
    protected_patterns: tuple[str, ...]
    voters: frozenset[str]
    minimum_approvals: int
    require_latest_commit: bool
    allow_author_vote: bool


class PolicyError(ValueError):
    """An invalid approval policy."""


def parse_policy(raw: object) -> Policy:
    if not isinstance(raw, dict):
        raise PolicyError("Policy must be a JSON object")

    if raw.get("version") != 1 or type(raw.get("version")) is not int:
        raise PolicyError("Policy version must be the integer 1")

    patterns = raw.get("protected_patterns")
    voters = raw.get("voters")
    quorum = raw.get("minimum_approvals")
    fresh = raw.get("require_latest_commit", True)
    allow_author = raw.get("allow_author_vote", False)

    if not isinstance(patterns, list) or not patterns or any(
        not isinstance(p, str) or not p.strip() or p.startswith("/") for p in patterns
    ):
        raise PolicyError("protected_patterns must contain nonempty relative glob strings")
    if not isinstance(voters, list) or not voters or any(
        not isinstance(v, str) or not v.strip() for v in voters
    ):
        raise PolicyError("voters must be a nonempty list of GitHub usernames")

    normalized = [v.strip().casefold() for v in voters]
    if len(set(normalized)) != len(normalized):
        raise PolicyError("voters must be unique (case-insensitive)")
    if type(quorum) is not int or quorum < 1 or quorum > len(normalized):
        raise PolicyError("minimum_approvals must be between 1 and the number of voters")
    if type(fresh) is not bool or type(allow_author) is not bool:
        raise PolicyError("require_latest_commit and allow_author_vote must be booleans")
    unknown = set(raw).difference({
        "version", "protected_patterns", "voters", "minimum_approvals",
        "require_latest_commit", "allow_author_vote",
    })
    if unknown:
        raise PolicyError("Unknown policy fields: " + ", ".join(sorted(unknown)))
    return Policy(
        protected_patterns=tuple(patterns),
        voters=frozenset(normalized),
        minimum_approvals=quorum,
        require_latest_commit=fresh,
        allow_author_vote=allow_author,
    )


def load_policy(path: str | Path) -> Policy:
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return parse_policy(json.load(stream))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"Cannot read policy file {path}: {exc}") from exc
