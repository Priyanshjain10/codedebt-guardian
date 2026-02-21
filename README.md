# 🤖 CodeDebt Guardian

<div align="center">

**AI-Powered Multi-Agent System for Autonomous Technical Debt Detection, Prioritization & Remediation**

[![CI](https://github.com/Priyanshjain10/codedebt-guardian/actions/workflows/ci.yml/badge.svg)](https://github.com/Priyanshjain10/codedebt-guardian/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini%202.0-4285F4?logo=google)](https://ai.google.dev/)

**Built by Priyansh Jain | IIT Jodhpur — Applied AI & Data Science**

</div>

---

## 🎯 What is this?

Technical debt costs organizations **$3.61 per line of code** and consumes **40–60% of developer sprint time**.

Traditional tools like SonarQube only **detect** problems. CodeDebt Guardian **detects, prioritizes, AND autonomously fixes them** by opening real GitHub Pull Requests.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🕵️ **3-Agent Pipeline** | Detection → Ranking → Fix Proposal, orchestrated sequentially |
| 🤖 **Auto-Fix PRs** | Opens real GitHub PRs with code fixes applied autonomously |
| 📊 **RICE Scoring** | Business-impact-weighted priority ranking |
| 💾 **Persistent Memory** | SQLite-backed cache — no re-analyzing the same repo |
| 🌐 **Web UI** | Streamlit dashboard with Plotly charts |
| 🔭 **Observability** | Span tracing + per-operation metrics for every agent call |
| ✅ **40+ Tests** | Full pytest suite with CI on Python 3.10/3.11/3.12 |

---

## 🏛️ Architecture
```
┌─────────────────────────────────┐
│      Orchestrator Agent         │
│  Session Management             │
│  PersistentMemoryBank (SQLite)  │
│  ObservabilityLayer             │
└──────────┬──────────────────────┘
           │
┌──────────┼──────────────────┐
│          │                  │
▼          ▼                  ▼
Agent 1         Agent 2            Agent 3
Debt Detection  Priority Ranking   Fix Proposal
- Python AST    • RICE Score       • 6 Templates
- Gemini 2.0    • AI Impact        • Gemini AI
- Regex rules   • Sprint Plan      • Before/After
           │
           ▼
     PRGenerator
Branch → Patch → Commit → Pull Request
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Google AI Studio API Key](https://aistudio.google.com/app/apikey) (free)
- [GitHub Personal Access Token](https://github.com/settings/tokens)

### Installation
```bash
git clone https://github.com/Priyanshjain10/codedebt-guardian.git
cd codedebt-guardian
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

### Usage
```bash
# Launch web UI
python main.py --ui

# CLI analysis
python main.py --repo https://github.com/owner/repo

# Auto-fix mode — creates real GitHub PRs
python main.py --repo https://github.com/owner/repo --auto-fix --max-prs 3
```

### Python API
```python
from agents.orchestrator import CodeDebtOrchestrator

guardian = CodeDebtOrchestrator()
detection = guardian.detect_debt("https://github.com/owner/repo")
ranked    = guardian.rank_debt(detection)
fixes     = guardian.propose_fixes(ranked[:10])

# Auto-fix: create real PRs
prs = guardian.create_pull_requests(
    repo_url="https://github.com/owner/repo",
    fix_proposals=fixes,
    ranked_issues=ranked,
    max_prs=3,
)
for pr in prs:
    print(f"#{pr['number']}: {pr['html_url']}")
```

---

## 🔍 What Gets Detected

**Security 🔴** — Hardcoded passwords, API keys, bare except clauses
**Structure 🟠** — God classes, long functions, too many parameters
**Maintainability 🟡** — Missing docstrings, no type hints, high cyclomatic complexity
**Project Health 🟢** — No tests, no CI/CD, unpinned dependencies, missing README

---

## 📁 Project Structure
```
codedebt-guardian/
├── agents/
│   ├── orchestrator.py           # Master coordinator
│   ├── debt_detection_agent.py   # AST + Gemini scanning
│   ├── priority_ranking_agent.py # RICE scoring
│   └── fix_proposal_agent.py     # Fix generator
├── tools/
│   ├── pr_generator.py           # Autonomous GitHub PR creation
│   ├── persistent_memory.py      # SQLite-backed memory
│   ├── github_tool.py            # GitHub REST API
│   ├── code_analyzer.py          # AST metrics
│   └── observability.py          # Span tracing
├── models/
│   └── schemas.py                # Pydantic v2 data models
├── ui/app.py                     # Streamlit web UI
├── tests/                        # 40+ unit tests
├── .github/workflows/ci.yml      # GitHub Actions CI
└── main.py                       # CLI entry point
```

---

## 🧪 Running Tests
```bash
pytest tests/ -v --cov=agents --cov=tools
```

---

## 🗺️ Roadmap

- [x] 3-agent detection & fix pipeline
- [x] RICE-based priority scoring
- [x] Auto-Fix PR generation
- [x] SQLite persistent memory
- [x] Streamlit web UI
- [x] GitHub Actions CI
- [ ] GitHub Action (auto-analyze on PR)
- [ ] Support for JavaScript/TypeScript
- [ ] Slack/Discord notifications
- [ ] VS Code extension

---

## 🤝 Contributing

PRs welcome! Fork → Branch → Test → PR.

---

## 📝 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

⭐ **Star this repo** if it helped you!

**[Priyansh Jain](https://github.com/Priyanshjain10)** | IIT Jodhpur

</div>
