"""
Priority Ranking Agent - Agent 2 of 3
Scores and prioritizes technical debt by business impact using ML-based heuristics + Gemini.

Scoring factors:
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Business impact (security, performance, maintainability)
- Effort to fix (MINUTES/HOURS/DAYS)
- Code hotspot (frequently changed files)
- Age of debt (estimated)
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False

from tools.memory_bank import MemoryBank
from tools.observability import ObservabilityLayer

logger = logging.getLogger(__name__)

if _GENAI_AVAILABLE:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Scoring weights
SEVERITY_SCORES = {
    "CRITICAL": 100,
    "HIGH": 70,
    "MEDIUM": 40,
    "LOW": 15,
    "UNKNOWN": 10,
}

TYPE_IMPACT_SCORES = {
    "hardcoded_password": 95,
    "hardcoded_api_key": 95,
    "hardcoded_token": 90,
    "syntax_error": 90,
    "no_tests": 75,
    "god_class": 65,
    "god_file": 60,
    "long_method": 50,
    "bare_except": 45,
    "missing_requirements": 70,
    "unpinned_dependencies": 40,
    "no_cicd": 35,
    "missing_readme": 30,
    "missing_docstring": 20,
    "too_many_parameters": 35,
}

EFFORT_MULTIPLIERS = {
    "MINUTES": 1.5,   # Easy win — high priority boost
    "HOURS": 1.0,
    "DAYS": 0.7,      # High effort items ranked slightly lower
}

PRIORITY_THRESHOLDS = {
    "CRITICAL": 80,
    "HIGH": 55,
    "MEDIUM": 30,
    "LOW": 0,
}


RANKING_SYSTEM_PROMPT = """You are a senior engineering manager prioritizing technical debt for a sprint.
Given a list of technical debt items, your job is to:
1. Assess the REAL business impact of each item
2. Consider dependencies between issues
3. Identify quick wins (high impact, low effort)
4. Flag items that block other work

For each item, provide an adjusted priority and brief business justification.
Respond ONLY with a valid JSON array of objects with fields:
- id (original issue index)
- business_impact_score (0-100)
- blocks_other_work (true/false)
- quick_win (true/false)
- business_justification (1-2 sentences)
- recommended_sprint (1, 2, or 3)"""


class PriorityRankingAgent:
    """
    Agent 2: Priority Ranking

    Combines rule-based scoring with Gemini AI for nuanced business impact assessment.
    Uses RICE-inspired scoring: (Reach × Impact × Confidence) / Effort
    """

    def __init__(self, memory: Optional[MemoryBank] = None):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=RANKING_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        ) if _GENAI_AVAILABLE else None
        self.memory = memory or MemoryBank()
        self.obs = ObservabilityLayer(service_name="priority_ranking_agent")

    def rank(self, issues: List[Dict], repo_metadata: Dict = None) -> List[Dict[str, Any]]:
        """
        Rank and score all detected issues.

        Args:
            issues: List of detected technical debt issues
            repo_metadata: Repository context (stars, age, language, etc.)

        Returns:
            Sorted list of issues with priority scores and labels
        """
        with self.obs.trace("rank") as span:
            span.set_attribute("input_issues", len(issues))

            if not issues:
                return []

            # Step 1: Rule-based scoring (fast, deterministic)
            scored_issues = [self._score_issue(i, idx) for idx, i in enumerate(issues)]

            # Step 2: AI-powered business impact enrichment (top 20 issues)
            top_issues = sorted(scored_issues, key=lambda x: x["score"], reverse=True)[:20]
            ai_enrichment = self._get_ai_enrichment(top_issues, repo_metadata or {})

            # Step 3: Merge AI enrichment into scores
            enrichment_map = {item["id"]: item for item in ai_enrichment}
            for issue in scored_issues:
                enrichment = enrichment_map.get(issue["_rank_id"], {})
                if enrichment:
                    # Blend AI business impact score with rule-based score
                    ai_score = enrichment.get("business_impact_score", 50)
                    issue["score"] = round(issue["score"] * 0.6 + ai_score * 0.4)
                    issue["quick_win"] = enrichment.get("quick_win", False)
                    issue["blocks_other_work"] = enrichment.get("blocks_other_work", False)
                    issue["business_justification"] = enrichment.get("business_justification", "")
                    issue["recommended_sprint"] = enrichment.get("recommended_sprint", 2)

            # Step 4: Final sort and priority labeling
            ranked = sorted(scored_issues, key=lambda x: x["score"], reverse=True)
            for issue in ranked:
                issue["priority"] = self._score_to_priority(issue["score"])
                issue["rank"] = ranked.index(issue) + 1

            span.set_attribute("ranked_issues", len(ranked))
            logger.info(f"Ranked {len(ranked)} issues")
            return ranked

    def _score_issue(self, issue: Dict, idx: int) -> Dict:
        """Compute rule-based priority score for a single issue."""
        issue = dict(issue)  # copy

        severity = issue.get("severity", "UNKNOWN")
        issue_type = issue.get("type", "unknown")
        effort = issue.get("effort_to_fix", "HOURS")

        # Base score from severity
        base_score = SEVERITY_SCORES.get(severity, 10)

        # Type-specific impact score
        type_score = TYPE_IMPACT_SCORES.get(issue_type, 30)

        # Effort multiplier (quick wins get boosted)
        effort_mult = EFFORT_MULTIPLIERS.get(effort, 1.0)

        # Combined score
        raw_score = (base_score * 0.4 + type_score * 0.6) * effort_mult
        score = min(100, round(raw_score))

        issue["score"] = score
        issue["_rank_id"] = idx
        issue["quick_win"] = effort == "MINUTES" and score > 50
        issue["blocks_other_work"] = False
        issue["business_justification"] = ""
        issue["recommended_sprint"] = 1 if score > 70 else (2 if score > 40 else 3)

        return issue

    def _get_ai_enrichment(self, issues: List[Dict], repo_metadata: Dict) -> List[Dict]:
        """Use Gemini to assess business impact of top issues."""
        if not issues:
            return []

        # Prepare compact representation for context efficiency
        compact_issues = []
        for issue in issues:
            compact_issues.append({
                "id": issue.get("_rank_id"),
                "type": issue.get("type"),
                "severity": issue.get("severity"),
                "description": issue.get("description", "")[:200],
                "location": issue.get("location"),
                "effort_to_fix": issue.get("effort_to_fix"),
            })

        prompt = f"""Repository context:
- Name: {repo_metadata.get('name', 'Unknown')}
- Stars: {repo_metadata.get('stars', 0)}  
- Open Issues: {repo_metadata.get('open_issues', 0)}
- Language: {repo_metadata.get('language', 'Python')}

Technical debt items to prioritize:
{json.dumps(compact_issues, indent=2)}

Assess business impact and prioritization for each item."""

        if not self.model:
            return []
        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw)
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.warning(f"AI enrichment failed: {e}")
            return []

    def _score_to_priority(self, score: int) -> str:
        """Convert numeric score to priority label."""
        for priority, threshold in PRIORITY_THRESHOLDS.items():
            if score >= threshold:
                return priority
        return "LOW"

    def get_quick_wins(self, ranked_issues: List[Dict]) -> List[Dict]:
        """Filter and return quick win items (high impact, low effort)."""
        return [i for i in ranked_issues if i.get("quick_win", False)]

    def get_sprint_plan(self, ranked_issues: List[Dict]) -> Dict[int, List[Dict]]:
        """Group issues into sprint recommendations."""
        plan = {1: [], 2: [], 3: []}
        for issue in ranked_issues:
            sprint = issue.get("recommended_sprint", 2)
            plan[sprint].append(issue)
        return plan
