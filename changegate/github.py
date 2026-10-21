"""Minimal read-only GitHub REST API client using the Python standard library."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class GitHubError(RuntimeError):
    """GitHub API data cannot be retrieved safely."""


class GitHubClient:
    def __init__(self, token: str, repo: str):
        if not token:
            raise GitHubError("GITHUB_TOKEN is required for online checks")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise GitHubError("--repo must be owner/repo")
        self.repo = repo
        self.token = token

    def _get(self, endpoint: str) -> Any:
        url = "https://api.github.com" + endpoint
        request = Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-changegate/0.1",
        })
        try:
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise GitHubError(f"GitHub API request failed for {endpoint}: {exc}") from exc

    def pull_request(self, number: int) -> dict:
        payload = self._get(self._pr_path(number))
        if not isinstance(payload, dict):
            raise GitHubError("Unexpected pull request response")
        return payload

    def _pr_path(self, number: int) -> str:
        if number <= 0:
            raise GitHubError("Pull request number must be positive")
        owner, name = self.repo.split("/", 1)
        return f"/repos/{quote(owner)}/{quote(name)}/pulls/{number}"

    def _paged(self, endpoint: str, *, max_pages: int = 30) -> list[dict]:
        items: list[dict] = []
        for page in range(1, max_pages + 1):
            response = self._get(f"{endpoint}?per_page=100&page={page}")
            if not isinstance(response, list) or any(not isinstance(x, dict) for x in response):
                raise GitHubError("Unexpected list response")
            items.extend(response)
            if len(response) < 100:
                return items
        raise GitHubError("GitHub pagination limit reached; refusing to approve incomplete data")

    def changed_files(self, number: int) -> list[str]:
        rows = self._paged(self._pr_path(number) + "/files")
        files: list[str] = []
        for row in rows:
            path = row.get("filename")
            if not isinstance(path, str):
                raise GitHubError("Missing filename in changed files")
            files.append(path)
            # GitHub returns 'previous_filename' for renamed files.
            # Both the old and the new path must be checked.
            previous = row.get("previous_filename")
            if isinstance(previous, str):
                files.append(previous)
        return files

    def reviews(self, number: int) -> list[dict]:
        return self._paged(self._pr_path(number) + "/reviews", max_pages=50)
