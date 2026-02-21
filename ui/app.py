"""
CodeDebt Guardian - Streamlit Web Interface
A beautiful, interactive UI for analyzing technical debt.
"""

import os
import sys
import json
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import CodeDebtOrchestrator

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeDebt Guardian",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .critical-badge { background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .high-badge { background: #fd7e14; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .medium-badge { background: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .low-badge { background: #198754; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .fix-card {
        background: #f0fff4;
        border-left: 4px solid #198754;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .issue-card {
        background: #fff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stProgress > div > div { background-color: #667eea; }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.2rem;">🤖 CodeDebt Guardian</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
        AI-Powered Technical Debt Detection, Prioritization & Remediation
    </p>
    <p style="margin: 0.25rem 0 0 0; opacity: 0.7; font-size: 0.85rem;">
        Powered by Google Gemini 2.0 + Multi-Agent Architecture
    </p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/Powered%20by-Gemini%202.0-4285F4?logo=google", use_column_width=True)
    st.markdown("---")

    st.header("⚙️ Configuration")

    google_api_key = st.text_input(
        "Google API Key",
        value=os.environ.get("GOOGLE_API_KEY", ""),
        type="password",
        help="Get yours at: https://aistudio.google.com/",
    )

    github_token = st.text_input(
        "GitHub Token",
        value=os.environ.get("GITHUB_TOKEN", ""),
        type="password",
        help="Settings > Developer settings > Personal access tokens",
    )

    st.markdown("---")
    st.header("📊 Analysis Options")

    branch = st.text_input("Branch", value="main", help="Branch to analyze")

    max_fixes = st.slider("Fix Proposals to Generate", 1, 20, 10)

    st.markdown("---")

    auto_fix = st.toggle(
        "🤖 Auto-Fix Mode",
        value=False,
        help="Automatically create GitHub PRs with fixes applied to the repo!",
    )
    if auto_fix:
        max_prs = st.slider("Max PRs to Create", 1, 5, 3)
        st.warning("⚠️ Auto-Fix will open real PRs on the repository. Make sure your token has write access.")
    else:
        max_prs = 3

    st.markdown("---")

    st.markdown("""
    **🤖 Agent Pipeline:**
    1. 🕵️ Debt Detection Agent
    2. 📊 Priority Ranking Agent
    3. 🔧 Fix Proposal Agent

    **📚 About:**
    Built for Google & Kaggle's
    5-Day AI Agents Intensive.
    Uses Google ADK + Gemini 2.0.
    """)


# ─── Main Content ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    repo_url = st.text_input(
        "🔗 GitHub Repository URL",
        placeholder="https://github.com/owner/repository",
        help="Enter any public GitHub repository URL",
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Analyze Repository", type="primary", use_container_width=True)


# Example repos
with st.expander("💡 Try an example repository"):
    example_repos = {
        "Flask (Python web framework)": "https://github.com/pallets/flask",
        "Requests (HTTP library)": "https://github.com/psf/requests",
        "FastAPI": "https://github.com/tiangolo/fastapi",
    }
    for name, url in example_repos.items():
        if st.button(f"📁 {name}", key=url):
            st.session_state["example_url"] = url
            st.rerun()

# Handle example selection
if "example_url" in st.session_state:
    repo_url = st.session_state.pop("example_url")


# ─── Analysis ─────────────────────────────────────────────────────────────────
if analyze_btn and repo_url:

    # Validate keys
    if not google_api_key:
        st.error("❌ Please enter your Google API Key in the sidebar")
        st.stop()
    if not github_token:
        st.warning("⚠️ No GitHub token — rate limits will be very low (60 req/hour)")

    # Set env vars from UI inputs
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["GITHUB_TOKEN"] = github_token

    # ── Progress Tracking ──
    progress_bar = st.progress(0, text="Initializing agents...")
    status = st.empty()

    results_container = st.container()

    try:
        orchestrator = CodeDebtOrchestrator()

        # Phase 1: Detection
        status.info("🕵️ **Agent 1/3: Debt Detection** — Scanning repository...")
        progress_bar.progress(10, text="Fetching repository contents...")

        with st.spinner("Fetching and analyzing code..."):
            detection_results = orchestrator.detect_debt(repo_url, branch)

        progress_bar.progress(40, text=f"Found {detection_results['total_issues']} issues...")
        status.info(f"🕵️ Detection complete: **{detection_results['total_issues']}** issues found in **{detection_results['files_scanned']}** files")
        time.sleep(0.5)

        # Phase 2: Ranking
        progress_bar.progress(50, text="Running priority ranking...")
        status.info("📊 **Agent 2/3: Priority Ranking** — Scoring by business impact...")

        with st.spinner("Calculating priorities..."):
            ranked_results = orchestrator.rank_debt(detection_results)

        critical_count = sum(1 for i in ranked_results if i.get("priority") == "CRITICAL")
        progress_bar.progress(75, text="Generating fix proposals...")
        status.info(f"📊 Ranking complete: **{critical_count}** CRITICAL issues identified")
        time.sleep(0.5)

        # Phase 3: Fixes
        status.info("🔧 **Agent 3/3: Fix Proposal** — Generating actionable fixes...")

        with st.spinner("Generating code fixes..."):
            fix_proposals = orchestrator.propose_fixes(ranked_results[:max_fixes])

        progress_bar.progress(90 if auto_fix else 100, text="Generating fix proposals...")
        status.success(f"✅ {len(fix_proposals)} fix proposals generated.")

        # Phase 4: Auto-Fix (optional)
        created_prs = []
        if auto_fix:
            progress_bar.progress(92, text="Creating GitHub Pull Requests...")
            status.info("🤖 **Auto-Fix** — Opening GitHub PRs with fixes applied...")
            with st.spinner("Creating Pull Requests..."):
                try:
                    created_prs = orchestrator.create_pull_requests(
                        repo_url=repo_url,
                        fix_proposals=fix_proposals,
                        ranked_issues=ranked_results,
                        max_prs=max_prs,
                        base_branch=branch,
                    )
                except Exception as e:
                    st.warning(f"Auto-fix encountered an issue: {e}")

        progress_bar.progress(100, text="Analysis complete!")
        if created_prs:
            status.success(f"🎉 Done! {len(fix_proposals)} fixes proposed, {len(created_prs)} PRs created!")
        else:
            status.success(f"✅ Analysis complete! {len(fix_proposals)} fix proposals generated.")

        # ── Store in session state ──
        st.session_state["report"] = {
            "detection": detection_results,
            "ranked": ranked_results,
            "fixes": fix_proposals,
            "prs": created_prs,
            "repo_url": repo_url,
            "branch": branch,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Analysis failed: {str(e)}")
        st.info("💡 Check your API keys and make sure the repository URL is correct and public.")
        st.stop()


# ─── Results Display ──────────────────────────────────────────────────────────
if "report" in st.session_state:
    report = st.session_state["report"]
    detection = report["detection"]
    ranked = report["ranked"]
    fixes = report["fixes"]
    prs = report.get("prs", [])

    st.markdown("---")
    # ── PR Success Banner ──
    if prs:
        st.success(f"🎉 **Auto-Fix created {len(prs)} Pull Request(s) on the repository!**")
        for pr in prs:
            st.markdown(f"- [#{pr['number']} {pr['title']}]({pr['html_url']})")
        st.markdown("---")

    st.header(f"📈 Results for `{report['repo_url'].split('/')[-1]}`")

    repo_meta = detection.get("repo_metadata", {})
    if repo_meta:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⭐ Stars", f"{repo_meta.get('stars', 0):,}")
        col2.metric("🍴 Forks", f"{repo_meta.get('forks', 0):,}")
        col3.metric("🐛 Open Issues", f"{repo_meta.get('open_issues', 0):,}")
        col4.metric("💻 Language", repo_meta.get("language", "Python"))

    st.markdown("---")

    # ── Key Metrics ──
    total = detection.get("total_issues", 0)
    critical = sum(1 for i in ranked if i.get("priority") == "CRITICAL")
    high = sum(1 for i in ranked if i.get("priority") == "HIGH")
    medium = sum(1 for i in ranked if i.get("priority") == "MEDIUM")
    low = sum(1 for i in ranked if i.get("priority") == "LOW")
    quick_wins = sum(1 for i in ranked if i.get("quick_win"))

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🔍 Total Issues", total)
    col2.metric("🔴 Critical", critical, delta=f"-{critical}" if critical else None, delta_color="inverse")
    col3.metric("🟠 High", high)
    col4.metric("🟡 Medium", medium)
    col5.metric("🟢 Low", low)
    col6.metric("⚡ Quick Wins", quick_wins)

    st.markdown("---")

    # ── Tabs ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔍 All Issues", "🔧 Fix Proposals", "🤖 Pull Requests", "📤 Export"])

    # ── Tab 1: Dashboard ──
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Severity donut chart
            severity_data = {
                "CRITICAL": critical, "HIGH": high, "MEDIUM": medium, "LOW": low
            }
            fig = go.Figure(data=[go.Pie(
                labels=list(severity_data.keys()),
                values=list(severity_data.values()),
                hole=0.5,
                marker_colors=["#dc3545", "#fd7e14", "#ffc107", "#198754"],
            )])
            fig.update_layout(title="Issues by Severity", height=350, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Type bar chart
            stats = detection.get("stats", {}).get("by_type", {})
            if stats:
                sorted_types = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
                fig = px.bar(
                    x=[s[1] for s in sorted_types],
                    y=[s[0] for s in sorted_types],
                    orientation="h",
                    title="Top Debt Types",
                    color=[s[1] for s in sorted_types],
                    color_continuous_scale="Reds",
                )
                fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

        # Priority score distribution
        if ranked:
            scores = [i.get("score", 0) for i in ranked]
            fig = px.histogram(
                x=scores,
                nbins=20,
                title="Priority Score Distribution",
                labels={"x": "Score", "y": "Count"},
                color_discrete_sequence=["#667eea"],
            )
            fig.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="CRITICAL threshold")
            fig.add_vline(x=55, line_dash="dash", line_color="orange", annotation_text="HIGH threshold")
            st.plotly_chart(fig, use_container_width=True)

        # Quick wins
        quick_win_items = [i for i in ranked if i.get("quick_win")]
        if quick_win_items:
            st.subheader("⚡ Quick Wins (High Impact, Low Effort)")
            for item in quick_win_items[:5]:
                with st.expander(f"🟢 {item.get('type', 'Unknown')} — {item.get('location', '')}"):
                    st.write(f"**Description:** {item.get('description', '')}")
                    st.write(f"**Score:** {item.get('score', 0)} | **Effort:** {item.get('effort_to_fix', '')}")
                    if item.get("business_justification"):
                        st.info(f"💼 {item['business_justification']}")

    # ── Tab 2: All Issues ──
    with tab2:
        st.subheader(f"🔍 All {len(ranked)} Issues (Ranked by Priority)")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            priority_filter = st.multiselect("Filter by Priority", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH"])
        with col2:
            type_filter = st.multiselect("Filter by Type", list(set(i.get("type", "") for i in ranked)))
        with col3:
            quick_wins_only = st.checkbox("⚡ Quick Wins Only")

        filtered = ranked
        if priority_filter:
            filtered = [i for i in filtered if i.get("priority") in priority_filter]
        if type_filter:
            filtered = [i for i in filtered if i.get("type") in type_filter]
        if quick_wins_only:
            filtered = [i for i in filtered if i.get("quick_win")]

        st.write(f"Showing {len(filtered)} issues")

        # Display as table
        if filtered:
            df = pd.DataFrame([{
                "Rank": i.get("rank", idx + 1),
                "Priority": i.get("priority", ""),
                "Type": i.get("type", ""),
                "Score": i.get("score", 0),
                "Location": i.get("location", "")[:40],
                "Description": i.get("description", "")[:60],
                "Effort": i.get("effort_to_fix", ""),
                "Quick Win": "⚡" if i.get("quick_win") else "",
            } for idx, i in enumerate(filtered)])

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
                    "Priority": st.column_config.TextColumn("Priority"),
                },
            )

            # Detail view
            selected_rank = st.number_input("View issue details (by rank)", min_value=1, max_value=len(filtered), value=1)
            if selected_rank <= len(filtered):
                issue = filtered[selected_rank - 1]
                with st.expander(f"📋 Issue #{selected_rank} Details", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Priority", issue.get("priority", ""))
                    col2.metric("Score", issue.get("score", 0))
                    col3.metric("Effort", issue.get("effort_to_fix", ""))

                    st.write(f"**Type:** `{issue.get('type', '')}`")
                    st.write(f"**Location:** `{issue.get('location', '')}`")
                    st.write(f"**Description:** {issue.get('description', '')}")
                    st.write(f"**Impact:** {issue.get('impact', '')}")
                    if issue.get("business_justification"):
                        st.info(f"💼 **Business Impact:** {issue['business_justification']}")
                    if issue.get("recommended_sprint"):
                        st.write(f"**Recommended Sprint:** Sprint {issue['recommended_sprint']}")

    # ── Tab 3: Fix Proposals ──
    with tab3:
        st.subheader(f"🔧 {len(fixes)} Fix Proposals")

        if not fixes:
            st.info("No fix proposals generated yet. Run an analysis first.")
        else:
            for idx, fix in enumerate(fixes, 1):
                priority = fix.get("original_issue", {}).get("priority", "MEDIUM")
                with st.expander(f"Fix #{idx}: {fix.get('issue_type', 'Unknown')} [{priority}]", expanded=idx == 1):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Problem:** {fix.get('problem_summary', '')}")
                        st.write(f"**Fix:** {fix.get('fix_summary', '')}")

                        if fix.get("before_code") and fix.get("after_code"):
                            st.markdown("**Before (problematic code):**")
                            st.code(fix["before_code"], language="python")
                            st.markdown("**After (fixed code):**")
                            st.code(fix["after_code"], language="python")

                    with col2:
                        st.write(f"**Estimated Time:** {fix.get('estimated_time', 'Unknown')}")
                        if fix.get("testing_tip"):
                            st.info(f"🧪 **Test Tip:** {fix['testing_tip']}")

                        if fix.get("steps"):
                            st.markdown("**Steps:**")
                            for step in fix["steps"]:
                                st.write(f"  • {step}")

                        if fix.get("references"):
                            st.markdown("**References:**")
                            for ref in fix["references"]:
                                st.markdown(f"  - [{ref}]({ref})")

    # ── Tab 4: Pull Requests ──
    with tab4:
        st.subheader("🤖 Autonomous Pull Requests")
        if not prs:
            st.info("No pull requests created yet. Enable **Auto-Fix Mode** in the sidebar and re-run analysis to automatically create PRs with fixes applied!")
            st.markdown("""
            ### How Auto-Fix works:
            1. Detects the top priority issues in your repo
            2. Generates a concrete code fix for each issue  
            3. Creates a new branch with the fix applied
            4. Opens a Pull Request with a detailed description
            
            > ⚠️ Requires your GitHub token to have **write access** to the repository.
            """)
        else:
            for pr in prs:
                with st.expander(f"PR #{pr['number']}: {pr['title']}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Branch:** `{pr.get('branch', 'N/A')}`")
                        st.markdown(f"**Status:** {pr.get('state', 'open').capitalize()}")
                    with col2:
                        st.link_button("🔗 View on GitHub", pr["html_url"], use_container_width=True)

    # ── Tab 5: Export ──
    with tab5:
        st.subheader("📤 Export Report")

        full_report = {
            "meta": {
                "repo_url": report["repo_url"],
                "branch": report["branch"],
                "generated_at": report["timestamp"],
                "tool": "CodeDebt Guardian v1.0",
            },
            "summary": {
                "total_issues": total,
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "quick_wins": quick_wins,
                "fixes_proposed": len(fixes),
            },
            "ranked_issues": ranked,
            "fix_proposals": fixes,
        }

        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(full_report, indent=2, default=str)
            st.download_button(
                "⬇️ Download Full Report (JSON)",
                data=json_str,
                file_name=f"debt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col2:
            # CSV export of issues
            if ranked:
                df = pd.DataFrame(ranked)
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Issues (CSV)",
                    data=csv,
                    file_name=f"debt_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.json(full_report["summary"])

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color: #6c757d; font-size: 0.85rem;'>"
    "🤖 CodeDebt Guardian | Built with Google ADK + Gemini 2.0 | "
    "<a href='https://github.com/Priyanshjain10/codedebt-guardian'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
