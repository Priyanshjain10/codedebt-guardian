# 🤖 CodeDebt Guardian

<div align="center">

<img src="https://img.shields.io/badge/AI-Powered-blueviolet?style=for-the-badge&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/Gemini_2.0-Flash-blue?style=for-the-badge&logo=google&logoColor=white"/>
<img src="https://github.com/Priyanshjain10/codedebt-guardian/actions/workflows/ci.yml/badge.svg?style=for-the-badge"/>
<img src="https://img.shields.io/badge/tests-84_passing-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"/>

<br/>
<br/>

### The AI agent that monitors your codebase 24/7, automatically fixes technical debt, and tells you exactly what ignoring it is costing you — in dollars.

<br/>

> **SonarQube tells you what's broken. CodeDebt Guardian fixes it while you sleep.**

</div>

---

## Why this exists

Every engineering team knows technical debt is expensive. Nobody does anything about it because:

- Tools only **report** problems — humans still have to fix them
- Nobody knows the **actual cost** of ignoring each issue
- Manual debt review happens once a quarter, if ever

CodeDebt Guardian closes all three gaps.

---

## What makes it different

### 🤖 AutoPilot Mode
Set it up once. It runs forever. Every time code is pushed, it detects new debt and opens draft fix PRs automatically — without anyone asking.
```python
from agents.autopilot_agent import AutoPilotAgent, AutoPilotConfig

agent = AutoPilotAgent(AutoPilotConfig(
    max_prs_per_day=3,
    draft_prs_only=True,   # Always — human reviews first
    dry_run=False
))
agent.run("https://github.com/your/repo")
# Finds issues → validates fixes → opens draft PRs → done
```

### 💰 Debt Interest Calculator
Uses real git history to show the business cost of each issue — and how that cost compounds over time.
```
⚠️  bare_except in auth.py
    Age:          8 months (touched 23 times by 4 engineers)  
    Fix now:      2h  →  $100
    Fix next Q:   3h  →  $150  (+23% interest)
    Recommendation: Fix this sprint. It's getting more expensive.
```

No other tool shows this. Engineering managers understand dollars. Now you can speak their language.

### 🔒 Safety-First Auto-Fixing
Every fix is validated before any PR is created:
- ✅ AST syntax check
- ✅ Code structure preserved (no functions deleted)
- ✅ Dangerous pattern detection
- ✅ Draft PRs only — no auto-merge, ever

---

## Architecture
```
┌─────────────────────────────────────────────────┐
│                 AutoPilot Agent                  │
│         Runs on push — no human needed           │
└───────────────────────┬─────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    Change          Debt           Fix
    Detector      Detection      Proposal
  (new code        Agent          Agent
    only)        (AST + AI)   (templates
                                 + AI)
          └─────────────┼─────────────┘
                        ▼
                  Safety Layer
             (validate before PR)
                        │
                        ▼
                 Draft PR Created
            ✅ human reviews first
                        │
                        ▼
            Debt Interest Calculator
           (what did this cost you?)
```

---

## What it detects

| Issue | Severity | Auto-fixable |
|-------|----------|-------------|
| Bare except clauses | HIGH | ✅ Yes |
| Hardcoded credentials | CRITICAL | ✅ Yes |
| Missing docstrings | LOW | ✅ Yes |
| Long functions >50 lines | MEDIUM | ✅ Yes |
| God classes >300 lines | HIGH | 🔧 Draft PR |
| Missing type hints | LOW | ✅ Yes |
| Duplicate code | MEDIUM | 🔧 Draft PR |

---

## Quick Start
```bash
git clone https://github.com/Priyanshjain10/codedebt-guardian
cd codedebt-guardian
pip install -r requirements.txt
cp .env.example .env
# Add GOOGLE_API_KEY and GITHUB_TOKEN to .env
```

**Analyze a repo once:**
```bash
python main.py --repo https://github.com/your/repo
```

**AutoPilot — runs on every push:**
```python
from agents.autopilot_agent import AutoPilotAgent, AutoPilotConfig

AutoPilotAgent(AutoPilotConfig(max_prs_per_day=3)).run("https://github.com/your/repo")
```

**Debt cost for a specific file:**
```python
from tools.debt_interest import DebtInterestCalculator

result = DebtInterestCalculator().calculate("owner", "repo", "path/file.py", issue)
print(result["summary"])
# "This bare except is 8 months old. Fix costs $100 today, $150 next quarter."
```

---

## Stack

| Component | Technology |
|-----------|-----------|
| AI Analysis | Google Gemini 2.0 Flash |
| Agent Framework | Google ADK |
| Data Models | Pydantic v2 |
| GitHub Integration | REST API + PR automation |
| Code Validation | AST + libcst |
| Testing | pytest — 84 tests |

---

## Tests
```bash
pytest tests/ -v
# 84 passed across agents, tools, schemas, autopilot, safety layer
```

---

## Roadmap

- [ ] JavaScript / TypeScript support
- [ ] Slack notifications for AutoPilot reports
- [ ] VS Code extension
- [ ] Dashboard UI (Streamlit — coming soon)
- [ ] Cross-repo debt propagation tracking

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

---

<div align="center">

Built by [Priyansh Jain](https://github.com/Priyanshjain10)

⭐ Star this repo if it saves you time

</div>
