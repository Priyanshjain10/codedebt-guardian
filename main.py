"""
CodeDebt Guardian - AI-Powered Technical Debt Detection & Remediation
Main orchestrator that coordinates all agents.
"""

import os
import sys
import argparse
import json
from typing import Optional
from datetime import datetime

from agents.orchestrator import CodeDebtOrchestrator
from tools.github_tool import GitHubTool
from tools.reporter import ReportGenerator


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║          🤖 CodeDebt Guardian v1.0                        ║
║   AI-Powered Technical Debt Detection & Remediation       ║
║   Built with Google ADK + Gemini 2.0                      ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_env():
    """Validate required environment variables."""
    missing = []
    if not os.getenv("GOOGLE_API_KEY"):
        missing.append("GOOGLE_API_KEY")
    if not os.getenv("GITHUB_TOKEN"):
        missing.append("GITHUB_TOKEN")
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Set them with: export GOOGLE_API_KEY=... GITHUB_TOKEN=...")
        sys.exit(1)


def run_analysis(repo_url: str, branch: str = "main", output_format: str = "rich", save_report: bool = False, auto_fix: bool = False, max_prs: int = 3):
    """Run full technical debt analysis on a repository."""
    print_banner()
    validate_env()

    print(f"\n🔍 Analyzing repository: {repo_url} (branch: {branch})")
    print("─" * 60)

    orchestrator = CodeDebtOrchestrator()

    print("\n[1/3] 🕵️  Running Debt Detection Agent...")
    detection_results = orchestrator.analyze(repo_url, branch=branch)
    print(f"      Found {detection_results['total_issues']} technical debt issues")

    print("\n[2/3] 📊 Running Priority Ranking Agent...")
    ranked_results = # rank_debt removed - analyze() handles this
    critical = sum(1 for item in ranked_results if item.get("priority") == "CRITICAL")
    high = sum(1 for item in ranked_results if item.get("priority") == "HIGH")
    print(f"      {critical} CRITICAL | {high} HIGH priority items identified")

    print("\n[3/3] 🔧 Running Fix Proposal Agent...")
    fix_proposals = # propose_fixes removed - analyze() handles this
    print(f"      Generated {len(fix_proposals)} fix proposals")

    # Auto-fix: create actual GitHub PRs
    created_prs = []
    if auto_fix:
        print(f"\n[4/4] 🤖 Running Auto-Fix — Creating GitHub PRs...")
        try:
            created_prs = []  # Use AutoPilotAgent for PR creation
            if created_prs:
                print(f"\n      ✅ Created {len(created_prs)} Pull Request(s):")
                for pr in created_prs:
                    print(f"         #{pr['number']} {pr['title'][:50]}")
                    print(f"         🔗 {pr['html_url']}")
            else:
                print("      ⚠️  No PRs created (check permissions or file paths)")
        except Exception as e:
            print(f"      ❌ Auto-fix failed: {e}")
            print("         Make sure your GITHUB_TOKEN has write access to the repo")

    report_gen = ReportGenerator()
    report = report_gen.generate(
        repo_url=repo_url,
        branch=branch,
        detection_results=detection_results,
        ranked_results=ranked_results,
        fix_proposals=fix_proposals,
    )
    report["pull_requests"] = created_prs

    # Save analysis history
    if hasattr(orchestrator.memory, "save_analysis_history"):
        orchestrator.memory.save_analysis_history(repo_url, branch, report.get("summary", {}))

    print("\n" + "═" * 60)
    report_gen.print_summary(report, output_format)

    if save_report:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debt_report_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Full report saved to: {filename}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="🤖 CodeDebt Guardian - AI-Powered Technical Debt Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --repo https://github.com/owner/repo
  python main.py --repo https://github.com/owner/repo --branch develop
  python main.py --repo https://github.com/owner/repo --save --format json
  python main.py --ui   # Launch web interface
        """,
    )

    parser.add_argument("--repo", type=str, help="GitHub repository URL to analyze")
    parser.add_argument("--branch", type=str, default="main", help="Branch to analyze (default: main)")
    parser.add_argument("--format", choices=["rich", "json", "simple"], default="rich", help="Output format")
    parser.add_argument("--save", action="store_true", help="Save report to JSON file")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit web interface")
    parser.add_argument("--auto-fix", action="store_true", help="🚀 Autonomously create GitHub PRs with fixes applied")
    parser.add_argument("--max-prs", type=int, default=3, help="Max PRs to create with --auto-fix (default: 3)")

    args = parser.parse_args()

    if args.ui:
        print("🌐 Launching CodeDebt Guardian Web UI...")
        os.system("streamlit run ui/app.py")
        return

    if not args.repo:
        parser.print_help()
        print("\n💡 Tip: Use --ui to launch the web interface")
        print("💡 Tip: Use --auto-fix to autonomously create GitHub PRs with fixes!")
        sys.exit(0)

    run_analysis(
        repo_url=args.repo,
        branch=args.branch,
        output_format=args.format,
        save_report=args.save,
        auto_fix=args.auto_fix,
        max_prs=args.max_prs,
    )


if __name__ == "__main__":
    main()
