
""" Change Detector — finds only files changed in recent commits. """
import logging, os, requests
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class ChangeDetector:
    SKIP_PATTERNS = ["test_", "_test.py", "tests/", "migrations/", "setup.py"]

    def get_changed_files(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        try:
            token = os.environ.get("GITHUB_TOKEN", "")
            headers = {"Authorization": f"token {token}"} if token else {}
            
            # Get latest commit
            r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits", 
                           params={"per_page": 1}, headers=headers, timeout=10)
            if r.status_code != 200:
                return []
            sha = r.json()[0]["sha"]
            
            # Get files in that commit
            r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}",
                           headers=headers, timeout=10)
            if r.status_code != 200:
                return []
            files = r.json().get("files", [])
            
            result = []
            for f in files:
                if not self._should_analyze(f):
                    continue
                # Get content
                r2 = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{f['filename']}",
                                headers=headers, timeout=10)
                if r2.status_code == 200:
                    import base64
                    content = base64.b64decode(r2.json()["content"]).decode("utf-8", errors="ignore")
                    result.append({
                        "name": f["filename"].split("/")[-1],
                        "path": f["filename"],
                        "content": content,
                        "additions": f.get("additions", 0),
                    })
            logger.info(f"Found {len(result)} changed files to analyze")
            return result[:10]
        except Exception as e:
            logger.error(f"Change detection failed: {e}")
            return []

    def _should_analyze(self, f: Dict) -> bool:
        name = f.get("filename", "")
        if not name.endswith(".py"): return False
        if f.get("status") == "removed": return False
        return not any(p in name for p in self.SKIP_PATTERNS)
