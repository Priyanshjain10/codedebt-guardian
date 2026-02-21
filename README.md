# 🤖 CodeDebt Guardian

<div align="center">

**The only AI agent that autonomously monitors, prioritizes, and fixes technical debt — while calculating its true business cost**

[![CI](https://github.com/Priyanshjain10/codedebt-guardian/actions/workflows/ci.yml/badge.svg)](https://github.com/Priyanshjain10/codedebt-guardian/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-84%20passing-brightgreen.svg)](tests/)

</div>

---

## What makes this different

Every tool (SonarQube, CodeClimate, DeepSource) tells you **what** the debt is. You still have to remember to check, prioritize, and fix it yourself.

CodeDebt Guardian does three things no other tool does:

**1. AutoPilot Mode** — runs continuously in the background, detects new debt on every push, and opens draft fix PRs automatically. Like a senior engineer working 24/7.

**2. Debt Interest Calculator** — uses real git history to show the *business cost* of ignoring each issue. "This bare except clause is 8 months old, touched by 3 teams, and costs $200 to fix today. Wait one quarter and it costs $340."

**3. Safety-First Auto-fixing** — every fix is validated (AST check, structure check, dangerous pattern detection) before any PR is created. Draft PRs only. No auto-merge. Ever.

---

## Architecture
```
┌─────────────────────────────────────────┐
│           AutoPilot Agent               │
│  Runs on schedule — no human needed     │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
Change       Debt         Fix
Detector  Detection    Proposal
(new code   Agent       Agent
 only)    (3 agents)  (templates
                       + AI)
                 │
                 ▼
         Safety Layer
     (AST + structure +
      dangerous pattern
         validation)
                 │
                 ▼
         Draft PR Created
      (human reviews first)
```

## Agents

- **Debt Detection Agent** — AST-based static analysis + Gemini AI semantic analysis
- **Priority Ranking Agent** — RICE-inspired scoring with severity weights  
- **Fix Proposal Agent** — 6 fix templates + AI fallback
- **AutoPilot Agent** — orchestrates everything on a schedule
- **Safety Layer** — validates every fix before PR creation
- **Change Detector** — analyzes only files changed in recent commits
- **Debt Interest Calculator** — calculates business cost from git history

## What it detects

- Bare except clauses
- Long functions (>50 lines)
- God classes (>300 lines)
- Hardcoded credentials
- Missing docstrings
- Missing type hints
- Duplicate code

## Quick Start
```bash
git clone https://github.com/Priyanshjain10/codedebt-guardian
cd codedebt-guardian
pip install -r requirements.txt
cp .env.example .env  # Add your GOOGLE_API_KEY and GITHUB_TOKEN
```

**Run once:**
```bash
python main.py --repo https://github.com/your/repo
```

**AutoPilot mode (runs continuously):**
```python
from agents.autopilot_agent import AutoPilotAgent, AutoPilotConfig

config = AutoPilotConfig(
    max_prs_per_day=3,
    draft_prs_only=True,  # Always
    dry_run=False
)
agent = AutoPilotAgent(config=config)
agent.run("https://github.com/your/repo")
```

**Debt Interest Report:**
```python
from tools.debt_interest import DebtInterestCalculator

calc = DebtInterestCalculator()
result = calc.calculate("owner", "repo", "path/to/file.py", issue)
print(result["summary"])
# "This bare except is 8 months old, touched 23 times.
#  Fix costs $100 today. Wait one quarter: $340."
```

## Tech Stack

- **Google ADK + Gemini 2.0** — AI analysis and fix generation
- **Pydantic v2** — type-safe data models
- **GitHub REST API** — repo access and PR creation
- **AST** — syntax validation and code structure analysis
- **pytest** — 84 tests across all components

## Tests
```bash
pytest tests/ -v
# 84 passed
```

## Project Status

Active development. Core features working. AutoPilot and Debt Interest Calculator are new — feedback welcome.

Built by [Priyansh Jain](https://github.com/Priyanshjain10) — Sem 2, Applied AI & Data Science, IIT Jodhpur.
