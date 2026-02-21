"""
GitHub Tool - Fetches repository contents using GitHub REST API.
Handles authentication, rate limiting, and content decoding.
"""

import os
import re
import base64
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
MAX_FILE_SIZE_BYTES = 100_000  # 100KB max per file
MAX_FILES = 50


class GitHubTool:
    """
    Tool for interacting with the GitHub REST API.

    Handles:
    - Repository metadata fetching
    - File content retrieval and decoding
    - Rate limit management
    - Error handling
    """

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeDebt-Guardian/1.0",
        })
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
        else:
            logger.warning("No GITHUB_TOKEN set — API rate limits will be very low (60 req/hour)")

    def parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from a GitHub URL."""
        # Handle formats: github.com/owner/repo, https://github.com/owner/repo
        repo_url = repo_url.rstrip("/")
        patterns = [
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
            r"^([^/]+)/([^/]+)$",  # owner/repo shorthand
        ]
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1), match.group(2)
        raise ValueError(f"Cannot parse GitHub URL: {repo_url}")

    def fetch_repo_contents(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Fetch repository metadata and all Python files.

        Args:
            repo_url: Full GitHub repository URL
            branch: Branch to analyze

        Returns:
            Dict with repo_metadata and list of files with content
        """
        owner, repo = self.parse_repo_url(repo_url)

        # Fetch repo metadata
        repo_metadata = self._fetch_repo_metadata(owner, repo)

        # Try branch, fall back to default branch
        try:
            files = self._fetch_tree(owner, repo, branch)
        except Exception:
            default_branch = repo_metadata.get("default_branch", "main")
            logger.info(f"Branch '{branch}' not found, using '{default_branch}'")
            files = self._fetch_tree(owner, repo, default_branch)

        # Fetch content for relevant files
        enriched_files = []
        for file_info in files[:MAX_FILES]:
            if self._should_analyze(file_info):
                content = self._fetch_file_content(owner, repo, file_info["path"])
                enriched_files.append({
                    "name": file_info["path"],
                    "size": file_info.get("size", 0),
                    "content": content,
                })

        logger.info(f"Fetched {len(enriched_files)} files from {owner}/{repo}")

        return {
            "repo_metadata": repo_metadata,
            "files": enriched_files,
            "owner": owner,
            "repo": repo,
        }

    def _fetch_repo_metadata(self, owner: str, repo: str) -> Dict:
        """Fetch basic repository metadata."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = self._get(url)
        data = response.json()

        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "size_kb": data.get("size", 0),
            "default_branch": data.get("default_branch", "main"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "topics": data.get("topics", []),
            "has_wiki": data.get("has_wiki", False),
            "license": data.get("license", {}).get("name") if data.get("license") else None,
        }

    def _fetch_tree(self, owner: str, repo: str, branch: str) -> List[Dict]:
        """Fetch the full file tree for a branch."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = self._get(url)
        data = response.json()

        if data.get("truncated"):
            logger.warning("Repository tree was truncated (>100k files). Analyzing subset.")

        return [
            item for item in data.get("tree", [])
            if item.get("type") == "blob"
        ]

    def _fetch_file_content(self, owner: str, repo: str, path: str) -> str:
        """Fetch and decode content of a single file."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
        try:
            response = self._get(url)
            data = response.json()

            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                return content[:MAX_FILE_SIZE_BYTES]  # Truncate large files
            elif data.get("download_url"):
                # Fall back to downloading directly
                dl_response = self.session.get(data["download_url"], timeout=10)
                return dl_response.text[:MAX_FILE_SIZE_BYTES]

        except Exception as e:
            logger.debug(f"Could not fetch {path}: {e}")

        return ""

    def _should_analyze(self, file_info: Dict) -> bool:
        """Determine if a file should be included in analysis."""
        path = file_info.get("path", "")
        size = file_info.get("size", 0)

        # Skip binary, large, and irrelevant files
        if size > MAX_FILE_SIZE_BYTES:
            return False

        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".eggs"}
        for skip in skip_dirs:
            if f"/{skip}/" in f"/{path}/" or path.startswith(f"{skip}/"):
                return False

        # Include Python files, config files, and docs
        include_extensions = {".py", ".txt", ".md", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".json"}
        ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        return ext in include_extensions

    def _get(self, url: str, retries: int = 3) -> requests.Response:
        """Make a GET request with rate limit handling and retries."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=15)

                # Handle rate limiting
                if response.status_code == 403 and "rate limit" in response.text.lower():
                    reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                    wait = max(0, reset_time - int(time.time())) + 1
                    logger.warning(f"Rate limited. Waiting {wait}s...")
                    time.sleep(min(wait, 60))
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"GitHub API error for {url}: {e}") from e

        raise RuntimeError(f"Failed after {retries} attempts: {url}")
