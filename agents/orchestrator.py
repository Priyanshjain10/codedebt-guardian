"""
Orchestrator Agent - Coordinates the multi-agent pipeline.
Manages session state, memory, and agent communication.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .debt_detection_agent import DebtDetectionAgent
from .priority_ranking_agent import PriorityRankingAgent
from .fix_proposal_agent import FixProposalAgent
from tools.persistent_memory import PersistentMemoryBank
from tools.memory_bank import MemoryBank
from tools.observability import ObservabilityLayer
from tools.pr_generator import PRGenerator

logger = logging.getLogger(__name__)


class SessionState:
    """Manages conversation and analysis state across agent calls."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.history: List[Dict] = []
        self.metadata: Dict[str, Any] = {}

    def add_event(self, agent: str, event_type: str, data: Any):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "event": event_type,
            "data": data,
        })

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "history": self.history,
            "metadata": self.metadata,
        }


class CodeDebtOrchestrator:
    """
    Master orchestrator that coordinates the three specialized agents:
    1. DebtDetectionAgent - scans code for technical debt
    2. PriorityRankingAgent - scores and ranks issues by business impact
    3. FixProposalAgent - generates actionable fix suggestions

    Uses sequential agent coordination with shared memory and observability.
    """

    def __init__(self, use_persistent_memory: bool = True):
        # Use SQLite-backed memory if available, else fallback to in-memory
        try:
            self.memory = PersistentMemoryBank() if use_persistent_memory else MemoryBank()
        except Exception:
            logger.warning("PersistentMemoryBank failed, falling back to in-memory")
            self.memory = MemoryBank()

        self.obs = ObservabilityLayer(service_name="orchestrator")

        # Initialize all specialized agents
        self.detection_agent = DebtDetectionAgent(memory=self.memory)
        self.ranking_agent = PriorityRankingAgent(memory=self.memory)
        self.fix_agent = FixProposalAgent(memory=self.memory)

        # PR generator (lazy-initialized when needed)
        self._pr_generator: PRGenerator = None

        # Session management
        self._sessions: Dict[str, SessionState] = {}

        logger.info("CodeDebt Orchestrator initialized with 3 agents")

    def _get_or_create_session(self, repo_url: str) -> SessionState:
        """Get existing or create new session for a repo."""
        session_id = f"session_{hash(repo_url) % 100000}"
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id)
            logger.info(f"Created new session: {session_id}")
        return self._sessions[session_id]

    def detect_debt(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Phase 1: Run the Debt Detection Agent.
        Scans the repository for technical debt patterns.
        """
        session = self._get_or_create_session(repo_url)

        with self.obs.trace("detect_debt") as span:
            span.set_attribute("repo_url", repo_url)
            span.set_attribute("branch", branch)

            # Check memory for cached results
            cache_key = f"detection_{repo_url}_{branch}"
            cached = self.memory.get(cache_key)
            if cached:
                logger.info(f"Cache hit for detection: {cache_key}")
                span.set_attribute("cache_hit", True)
                session.add_event("orchestrator", "cache_hit", {"key": cache_key})
                return cached

            # Run detection agent
            results = self.detection_agent.analyze(repo_url=repo_url, branch=branch)

            # Store in memory bank
            self.memory.set(cache_key, results, ttl_seconds=3600)
            session.add_event("detection_agent", "completed", {
                "total_issues": results.get("total_issues", 0),
                "files_scanned": results.get("files_scanned", 0),
            })

            span.set_attribute("issues_found", results.get("total_issues", 0))
            return results

    def rank_debt(self, detection_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Phase 2: Run the Priority Ranking Agent.
        Scores each debt item by impact, effort, and risk.
        """
        with self.obs.trace("rank_debt") as span:
            issues = detection_results.get("issues", [])
            span.set_attribute("input_issues", len(issues))

            ranked = self.ranking_agent.rank(issues=issues, repo_metadata=detection_results.get("repo_metadata", {}))

            span.set_attribute("ranked_issues", len(ranked))
            return ranked

    def propose_fixes(self, ranked_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phase 3: Run the Fix Proposal Agent.
        Generates concrete fix suggestions for top priority issues.
        """
        with self.obs.trace("propose_fixes") as span:
            span.set_attribute("issues_to_fix", len(ranked_issues))

            proposals = self.fix_agent.propose(issues=ranked_issues)

            span.set_attribute("proposals_generated", len(proposals))
            return proposals

    def run_full_analysis(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """
        Run the complete multi-agent pipeline end-to-end.
        Returns a comprehensive analysis report.
        """
        start = datetime.now()
        logger.info(f"Starting full analysis: {repo_url}")

        detection_results = self.detect_debt(repo_url, branch)
        ranked_results = self.rank_debt(detection_results)
        fix_proposals = self.propose_fixes(ranked_results[:10])

        duration = (datetime.now() - start).total_seconds()

        return {
            "repo_url": repo_url,
            "branch": branch,
            "analyzed_at": start.isoformat(),
            "duration_seconds": round(duration, 2),
            "detection": detection_results,
            "ranked_issues": ranked_results,
            "fix_proposals": fix_proposals,
            "summary": {
                "total_issues": detection_results.get("total_issues", 0),
                "critical": sum(1 for i in ranked_results if i.get("priority") == "CRITICAL"),
                "high": sum(1 for i in ranked_results if i.get("priority") == "HIGH"),
                "medium": sum(1 for i in ranked_results if i.get("priority") == "MEDIUM"),
                "low": sum(1 for i in ranked_results if i.get("priority") == "LOW"),
                "fixes_proposed": len(fix_proposals),
            },
        }

    def get_session_history(self, repo_url: str) -> Dict:
        """Get full session history for a repository analysis."""
        session = self._get_or_create_session(repo_url)
        return session.to_dict()

    def get_metrics(self) -> Dict[str, Any]:
        """Get observability metrics from all agents."""
        return {
            "orchestrator": self.obs.get_metrics(),
            "detection_agent": self.detection_agent.obs.get_metrics(),
            "ranking_agent": self.ranking_agent.obs.get_metrics(),
            "fix_agent": self.fix_agent.obs.get_metrics(),
            "memory_stats": self.memory.stats(),
        }

    def create_pull_requests(
        self,
        repo_url: str,
        fix_proposals: List[Dict],
        ranked_issues: List[Dict],
        max_prs: int = 3,
        base_branch: str = "main",
    ) -> List[Dict]:
        """
        Autonomously create GitHub Pull Requests with fixes applied.
        This is the key differentiator — not just detecting debt, but FIXING it.

        Args:
            repo_url: GitHub repository URL
            fix_proposals: Fix proposals from FixProposalAgent
            ranked_issues: Ranked issues from PriorityRankingAgent
            max_prs: Maximum number of PRs to create
            base_branch: Branch to base PRs on

        Returns:
            List of created PR info dicts with URLs
        """
        if not self._pr_generator:
            self._pr_generator = PRGenerator()

        with self.obs.trace("create_pull_requests") as span:
            span.set_attribute("max_prs", max_prs)
            prs = self._pr_generator.create_batch_prs(
                repo_url=repo_url,
                fix_proposals=fix_proposals,
                ranked_issues=ranked_issues,
                max_prs=max_prs,
                base_branch=base_branch,
            )
            span.set_attribute("prs_created", len(prs))
            logger.info(f"Created {len(prs)} pull requests")
            return prs

    def get_analysis_history(self, repo_url: str) -> List[Dict]:
        """Get historical analysis results for a repository."""
        if hasattr(self.memory, "get_analysis_history"):
            return self.memory.get_analysis_history(repo_url)
        return []
