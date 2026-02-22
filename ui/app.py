"""
CodeDebt Guardian - Professional Developer Dashboard
Features: Command palette, interactive code viewer, debt timeline, real-time status
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="CodeDebt Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@400;500;600;700&display=swap');
:root {
    --bg-primary: #0a0a0a; --bg-secondary: #0f0f0f; --bg-tertiary: #151515;
    --border: #1e1e1e; --text-primary: #e0e0e0; --text-muted: #555;
    --accent: #00ff88; --accent-dim: rgba(0,255,136,0.1);
    --critical: #ff3232; --high: #ff8c00; --medium: #ffc800; --low: #00ff88;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg-primary); color: var(--text-primary); }
.stApp { background-color: var(--bg-primary); }
section[data-testid="stSidebar"] { background-color: var(--bg-secondary); border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
#MainMenu, footer, header { visibility: hidden; }
.hero {
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at top left, var(--accent-dim) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title { font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; margin: 0 0 0.5rem 0; }
.hero-title span { color: var(--accent); }
.metric-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    padding: 1.5rem;
    position: relative;
    border-radius: 6px;
    transition: all 0.2s;
    margin-bottom: 1rem;
}
.metric-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 0.25rem; }
.metric-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; }
.code-viewer {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    overflow-x: auto;
}
.code-line { display: flex; min-height: 1.6rem; }
.code-line:hover { background: var(--bg-tertiary); }
.line-number {
    width: 50px;
    padding: 0.25rem 0.75rem;
    color: var(--text-muted);
    text-align: right;
    border-right: 1px solid var(--border);
    user-select: none;
}
.line-content { flex: 1; padding: 0.25rem 0.75rem; color: var(--text-primary); white-space: pre; }
.line-highlight-critical { background: rgba(255,50,50,0.1); border-left: 3px solid var(--critical); }
.line-highlight-high { background: rgba(255,140,0,0.1); border-left: 3px solid var(--high); }
.line-highlight-medium { background: rgba(255,200,0,0.1); border-left: 3px solid var(--medium); }
.line-highlight-low { background: rgba(0,255,136,0.1); border-left: 3px solid var(--low); }
.sev-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.sev-critical { background: rgba(255,50,50,0.15); color: var(--critical); border: 1px solid rgba(255,50,50,0.3); }
.sev-high { background: rgba(255,140,0,0.15); color: var(--high); border: 1px solid rgba(255,140,0,0.3); }
.sev-medium { background: rgba(255,200,0,0.15); color: var(--medium); border: 1px solid rgba(255,200,0,0.3); }
.sev-low { background: rgba(0,255,136,0.1); color: var(--low); border: 1px solid rgba(0,255,136,0.2); }
.terminal {
    background: #050505;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    max-height: 300px;
    overflow-y: auto;
}
.log-info { color: var(--accent); }
.log-warn { color: var(--medium); }
.log-error { color: var(--critical); }
.log-dim { color: var(--text-muted); }
.cost-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    padding: 1.5rem;
    border-radius: 6px;
}
.cost-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--accent); }
.stTextInput input {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 6px !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px var(--accent-dim) !important; }
.stButton button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
.stButton button:hover { background: #00cc6a !important; }
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
</style>
<script>
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const p = document.getElementById('cmd-palette');
        if (p) p.style.display = p.style.display === 'none' ? 'block' : 'none';
    }
    if (e.key === 'Escape') {
        const p = document.getElementById('cmd-palette');
        if (p) p.style.display = 'none';
    }
});
</script>
""", unsafe_allow_html=True)

def severity_badge(sev):
    cls = {"CRITICAL": "sev-critical", "HIGH": "sev-high", "MEDIUM": "sev-medium", "LOW": "sev-low"}.get(sev, "sev-low")
    icon = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "🔶", "LOW": "ℹ️"}.get(sev, "ℹ️")
    return f'<span class="sev-badge {cls}">{icon} {sev}</span>'

def interactive_code_viewer(code, highlights):
    lines = code.split("\n")
    hmap = {ln: (sev, msg) for ln, sev, msg in highlights}
    rows = []
    for i, line in enumerate(lines, 1):
        h = hmap.get(i)
        cls = f"code-line line-highlight-{h[0].lower()}" if h else "code-line"
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(f'<div class="{cls}"><div class="line-number">{i}</div><div class="line-content">{safe}</div></div>')
    return f'<div class="code-viewer">{"".join(rows)}</div>'

def debt_timeline(issues):
    if not issues:
        return None
    sorted_issues = sorted(issues, key=lambda x: x.get("age_days", 0), reverse=True)
    dates, costs, cum = [], [], 0
    for issue in sorted_issues:
        dates.append(datetime.now() - timedelta(days=issue.get("age_days", 0)))
        cum += issue.get("current_cost_usd", 100)
        costs.append(cum)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=costs, fill="tozeroy", fillcolor="rgba(0,255,136,0.08)", line=dict(color="#00ff88", width=2), name="Historical Debt"))
    if dates:
        fd = [dates[-1] + timedelta(days=90*i) for i in range(1, 4)]
        fc = [costs[-1] * (1.23**i) for i in range(1, 4)]
        fig.add_trace(go.Scatter(x=[dates[-1]]+fd, y=[costs[-1]]+fc, line=dict(color="#ff8c00", width=2, dash="dash"), name="Projected (unfixed)"))
    fig.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0f0f0f",
        font=dict(family="JetBrains Mono", color="#888", size=11),
        xaxis=dict(gridcolor="#1a1a1a", title="Time"),
        yaxis=dict(gridcolor="#1a1a1a", title="Cumulative Cost ($)", tickprefix="$"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=80, b=60),
        title=dict(text="Technical Debt Accumulation Over Time", font=dict(color="#fff", size=14), x=0.5)
    )
    return fig

with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0;border-bottom:1px solid #1a1a1a;margin-bottom:1.5rem">
        <div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:#fff">
            🛡️ CodeDebt<span style="color:#00ff88">Guardian</span>
        </div>
        <div style="font-size:0.65rem;color:#444;margin-top:0.25rem;letter-spacing:0.1em">AUTONOMOUS DEBT REMEDIATION</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔐 API Keys", expanded=True):
        google_api_key = st.text_input("GOOGLE_API_KEY", value="", type="password", placeholder="AIza...")
        github_token = st.text_input("GITHUB_TOKEN", value="", type="password", placeholder="ghp_...")
        if google_api_key: os.environ["GOOGLE_API_KEY"] = google_api_key
        if github_token: os.environ["GITHUB_TOKEN"] = github_token
    
    with st.expander("⚙️ Configuration", expanded=False):
        mode = st.selectbox("Mode", ["Full Analysis", "AutoPilot (Dry Run)", "Debt Interest Only"])
        max_files = st.slider("Max Files", 5, 100, 20)
        st.toggle("Auto-create PRs", value=False, disabled=True, help="Coming in v2.0")
    
    with st.expander("📊 Recent Analyses", expanded=False):
        try:
            from tools.persistent_memory import PersistentMemoryBank
            mem = PersistentMemoryBank()
            history = mem.get_all_history(limit=5)
            if history:
                for item in history:
                    rn = item["repo_url"].split("/")[-1]
                    st.markdown(f"""
                    <div style="font-size:0.8rem;color:#888;padding:0.5rem;background:#0f0f0f;border-radius:4px;margin-bottom:0.5rem">
                        <div style="color:#fff">{rn}</div>
                        <div style="font-size:0.7rem">{item["total_issues"]} issues</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#555;font-size:0.8rem">No recent analyses</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div style="color:#555;font-size:0.8rem">History unavailable</div>', unsafe_allow_html=True)

st.markdown("""
<div id="cmd-palette" style="display:none;position:fixed;top:20%;left:50%;transform:translateX(-50%);width:560px;max-width:90vw;background:#0f0f0f;border:1px solid #1e1e1e;border-radius:8px;z-index:9999;box-shadow:0 25px 80px rgba(0,0,0,0.9)">
    <div style="padding:1rem;border-bottom:1px solid #1e1e1e">
        <input type="text" placeholder="Type a command..." style="width:100%;background:transparent;border:none;color:#fff;font-family:JetBrains Mono;font-size:1rem;outline:none">
    </div>
    <div style="padding:0.5rem">
        <div style="padding:0.75rem 1rem;color:#888;font-size:0.85rem;cursor:pointer" onmouseover="this.style.background='#1a1a1a'" onmouseout="this.style.background='transparent'">
            <span style="color:#00ff88;margin-right:0.5rem">⚡</span> Analyze repository
        </div>
        <div style="padding:0.75rem 1rem;color:#888;font-size:0.85rem;cursor:pointer" onmouseover="this.style.background='#1a1a1a'" onmouseout="this.style.background='transparent'">
            <span style="color:#00ff88;margin-right:0.5rem">💰</span> Debt Interest Calculator
        </div>
        <div style="padding:0.75rem 1rem;color:#888;font-size:0.85rem;cursor:pointer" onmouseover="this.style.background='#1a1a1a'" onmouseout="this.style.background='transparent'">
            <span style="color:#00ff88;margin-right:0.5rem">🤖</span> AutoPilot mode
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">CodeDebt<span>Guardian</span></div>
    <div style="color:#888;font-size:0.9rem;margin-top:0.5rem">Autonomous technical debt detection, prioritization and remediation</div>
    <div style="margin-top:1rem;display:flex;gap:0.5rem;flex-wrap:wrap">
        <span style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);color:#00ff88;font-size:0.7rem;padding:0.25rem 0.75rem;border-radius:4px;text-transform:uppercase">AutoPilot</span>
        <span style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);color:#00ff88;font-size:0.7rem;padding:0.25rem 0.75rem;border-radius:4px;text-transform:uppercase">Debt Interest Calculator</span>
        <span style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);color:#00ff88;font-size:0.7rem;padding:0.25rem 0.75rem;border-radius:4px;text-transform:uppercase">Safety-First Auto-Fix</span>
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([5, 1])
with c1:
    repo_url = st.text_input("repo", placeholder="https://github.com/owner/repository ", label_visibility="collapsed")
with c2:
    analyze_btn = st.button("⚡ ANALYZE", use_container_width=True)

st.markdown("---")

if analyze_btn and repo_url:
    if not google_api_key: st.error("🔐 GOOGLE_API_KEY required"); st.stop()
    if not github_token: st.error("🔐 GITHUB_TOKEN required"); st.stop()
    
    st.markdown('<div class="section-header">// System Log</div>', unsafe_allow_html=True)
    log_ph = st.empty()
    logs = []
    
    def log(msg, level="info"):
        cls = {"info":"log-info","warn":"log-warn","error":"log-error","dim":"log-dim"}.get(level,"log-info")
        ts = datetime.now().strftime("%H:%M:%S")
        logs.append(f'<span style="color:#444">[{ts}]</span> <span class="{cls}">{msg}</span>')
        log_ph.markdown(f'<div class="terminal">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
    
    try:
        log(f"Target: {repo_url}", "dim")
        from agents.orchestrator import CodeDebtOrchestrator
        orchestrator = CodeDebtOrchestrator()
        log("✓ Orchestrator ready")
        
        with st.spinner(""):
            log("Running debt detection...")
            results = orchestrator.analyze(repo_url, max_files=max_files)
        
        issues = results.get("issues", [])
        fixes = results.get("fix_proposals", [])
        ranked = results.get("ranked_issues", issues)
        log(f"✓ {len(issues)} issues found in {results.get('files_analyzed',0)} files", "warn" if issues else "info")
        
        try:
            from tools.persistent_memory import PersistentMemoryBank
            PersistentMemoryBank().save_analysis_history(repo_url, "main", {
                "total_issues": len(issues),
                "critical": len([i for i in issues if i.get("severity")=="CRITICAL"]),
                "high": len([i for i in issues if i.get("severity")=="HIGH"])
            })
        except Exception:
            pass
        
        st.markdown("---")
        
        st.markdown('<div class="section-header">// Overview</div>', unsafe_allow_html=True)
        critical = len([i for i in issues if i.get("severity")=="CRITICAL"])
        high = len([i for i in issues if i.get("severity")=="HIGH"])
        medium = len([i for i in issues if i.get("severity")=="MEDIUM"])
        low = len([i for i in issues if i.get("severity")=="LOW"])
        
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff3232">{critical}</div><div class="metric-label">Critical</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff8c00">{high}</div><div class="metric-label">High</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ffc800">{medium}</div><div class="metric-label">Medium</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#00ff88">{low}</div><div class="metric-label">Low</div></div>', unsafe_allow_html=True)
        
        if issues:
            st.markdown("<br>", unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown('<div class="section-header">// Severity Distribution</div>', unsafe_allow_html=True)
                sd = {k:v for k,v in {"CRITICAL":critical,"HIGH":high,"MEDIUM":medium,"LOW":low}.items() if v>0}
                fig = px.pie(values=list(sd.values()), names=list(sd.keys()),
                    color_discrete_map={"CRITICAL":"#ff3232","HIGH":"#ff8c00","MEDIUM":"#ffc800","LOW":"#00ff88"}, hole=0.6)
                fig.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0f0f0f",
                    font=dict(family="JetBrains Mono",color="#888"),
                    legend=dict(orientation="h",yanchor="bottom",y=-0.2))
                st.plotly_chart(fig, use_container_width=True)
            with cc2:
                st.markdown('<div class="section-header">// Issue Types</div>', unsafe_allow_html=True)
                tc = {}
                for i in issues:
                    t = i.get("type","unknown").replace("_"," ").title()
                    tc[t] = tc.get(t,0)+1
                fig2 = px.bar(x=list(tc.values()), y=list(tc.keys()), orientation="h", color_discrete_sequence=["#00ff88"])
                fig2.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0f0f0f",
                    font=dict(family="JetBrains Mono",color="#888"),
                    xaxis=dict(gridcolor="#1a1a1a"), yaxis=dict(gridcolor="#1a1a1a"),
                    showlegend=False, margin=dict(l=150,r=20,t=30,b=20))
                st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">// Debt Accumulation Timeline</div>', unsafe_allow_html=True)
        tl = debt_timeline(issues)
        if tl: st.plotly_chart(tl, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">// 💰 Debt Interest Calculator</div>', unsafe_allow_html=True)
        try:
            from tools.debt_interest import DebtInterestCalculator
            parts = repo_url.rstrip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            calc = DebtInterestCalculator()
            ires, tnow, tfut = [], 0, 0
            for issue in issues[:5]:
                fp = issue.get("location","").split(":")[0]
                if fp and fp.endswith(".py"):
                    try:
                        r = calc.calculate(owner, repo, fp, issue)
                        ires.append(r); tnow += r["current_cost_usd"]; tfut += r["future_cost_usd"]
                    except Exception: pass
            if ires:
                dc1,dc2,dc3 = st.columns(3)
                with dc1: st.markdown(f'<div class="cost-card"><div style="font-size:0.7rem;color:#555;text-transform:uppercase;margin-bottom:0.5rem">Fix Cost Today</div><div class="cost-value">${tnow:,.0f}</div></div>', unsafe_allow_html=True)
                with dc2: st.markdown(f'<div class="cost-card" style="border-top-color:#ff8c00"><div style="font-size:0.7rem;color:#555;text-transform:uppercase;margin-bottom:0.5rem">Cost Next Quarter</div><div class="cost-value" style="color:#ff8c00">${tfut:,.0f}</div></div>', unsafe_allow_html=True)
                with dc3: st.markdown(f'<div class="cost-card" style="border-top-color:#ffc800"><div style="font-size:0.7rem;color:#555;text-transform:uppercase;margin-bottom:0.5rem">Save if Fixed Now</div><div class="cost-value" style="color:#ffc800">${tfut-tnow:,.0f}</div></div>', unsafe_allow_html=True)
                for r in ires:
                    with st.expander(f"📁 {r['filepath']} -- ${r['current_cost_usd']:,.0f} today → ${r['future_cost_usd']:,.0f} next quarter"):
                        st.markdown(f"""
                        <div style="background:#0f0f0f;border:1px solid #1a1a1a;padding:1rem;border-radius:6px">
                            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1rem;font-size:0.8rem">
                                <div><div style="color:#555;font-size:0.7rem;text-transform:uppercase">Age</div><div style="color:#fff">{r['age_days']} days</div></div>
                                <div><div style="color:#555;font-size:0.7rem;text-transform:uppercase">Touches</div><div style="color:#fff">{r['total_touches']} commits</div></div>
                                <div><div style="color:#555;font-size:0.7rem;text-transform:uppercase">Authors</div><div style="color:#fff">{r['unique_authors']} people</div></div>
                                <div><div style="color:#555;font-size:0.7rem;text-transform:uppercase">Interest</div><div style="color:#ff8c00">{r['interest_rate_pct']}%</div></div>
                            </div>
                            <div style="color:#888;font-size:0.85rem;line-height:1.6">{r['summary']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div style="color:#444;font-size:0.8rem">Debt Interest unavailable: {e}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">// 🔍 Issues Found</div>', unsafe_allow_html=True)
        for issue in ranked[:20]:
            sev = issue.get("severity","LOW")
            itype = issue.get("type","").replace("_"," ").title()
            loc = issue.get("location","")
            desc = issue.get("description","")
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #1e1e1e;padding:1.25rem;margin-bottom:0.75rem;border-radius:6px">
                <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem">
                    {severity_badge(sev)}
                    <span style="font-size:0.9rem;font-weight:600;color:#fff">{itype}</span>
                    <span style="font-size:0.75rem;color:#555">{loc}</span>
                </div>
                <div style="font-size:0.8rem;color:#888;line-height:1.6">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if issue.get("before_code"):
                with st.expander("View Code"):
                    hl = [(issue.get("line",1), sev, desc)]
                    st.markdown(interactive_code_viewer(issue["before_code"], hl), unsafe_allow_html=True)
                    if issue.get("after_code"):
                        st.markdown('<div style="color:#00ff88;font-size:0.75rem;margin:0.5rem 0">Fixed version:</div>', unsafe_allow_html=True)
                        st.markdown(interactive_code_viewer(issue["after_code"], []), unsafe_allow_html=True)
        
        if fixes:
            st.markdown("---")
            st.markdown('<div class="section-header">// 🔧 Fix Proposals</div>', unsafe_allow_html=True)
            for fix in fixes[:5]:
                with st.expander(fix.get("fix_summary","Fix available")):
                    if fix.get("problem_summary"): st.markdown(f"**Problem:** {fix['problem_summary']}")
                    if fix.get("steps"):
                        for step in fix["steps"]: st.markdown(f"- {step}")
                    if fix.get("testing_tip"): st.markdown(f"**Test:** {fix['testing_tip']}")
        
        if mode == "AutoPilot (Dry Run)":
            st.markdown("---")
            st.markdown('<div class="section-header">// 🤖 AutoPilot Simulation</div>', unsafe_allow_html=True)
            try:
                from agents.autopilot_agent import AutoPilotAgent, AutoPilotConfig
                ap = AutoPilotAgent(AutoPilotConfig(dry_run=True, max_prs_per_day=3))
                apr = ap.run(repo_url)
                a1,a2,a3 = st.columns(3)
                with a1: st.markdown(f'<div class="metric-card"><div class="metric-value">{apr.get("files_analyzed",0)}</div><div class="metric-label">Files Scanned</div></div>', unsafe_allow_html=True)
                with a2: st.markdown(f'<div class="metric-card"><div class="metric-value">{apr.get("issues_found",0)}</div><div class="metric-label">Issues Found</div></div>', unsafe_allow_html=True)
                with a3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(apr.get("prs_created",[]))}</div><div class="metric-label">PRs Simulated</div></div>', unsafe_allow_html=True)
                ss = apr.get("safety_stats",{})
                if ss:
                    st.markdown(f"""
                    <div style="background:#0f0f0f;border:1px solid #1a1a1a;padding:1rem;border-radius:6px;margin-top:1rem">
                        <div style="font-size:0.75rem;color:#555;text-transform:uppercase;margin-bottom:0.5rem">Safety Layer</div>
                        <div style="display:flex;gap:2rem;font-size:0.85rem">
                            <span style="color:#00ff88">{ss.get('passed',0)} passed</span>
                            <span style="color:#ff8c00">{ss.get('rejected',0)} rejected</span>
                            <span style="color:#888">{ss.get('pass_rate',0)}% pass rate</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AutoPilot failed: {e}")
        
        log("✓ Analysis complete")
        
    except Exception as e:
        log(f"Error: {e}", "error")
        st.error(f"Analysis failed: {e}")

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem">
        <div style="font-size:3rem;margin-bottom:1rem">🛡️</div>
        <div style="font-family:JetBrains Mono,monospace;font-size:1.5rem;font-weight:700;color:#fff;margin-bottom:0.5rem">Ready to analyze</div>
        <div style="font-size:0.85rem;color:#555;max-width:400px;margin:0 auto 2rem;line-height:1.6">
            Enter a GitHub repository URL above and click <b>ANALYZE</b>.<br>Add your API keys in the sidebar first.
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;max-width:700px;margin:0 auto">
            <div style="background:#0f0f0f;border:1px solid #1a1a1a;padding:1.5rem;border-radius:6px;text-align:left">
                <div style="color:#00ff88;font-size:1.5rem;margin-bottom:0.5rem">⚡</div>
                <div style="font-size:0.8rem;color:#888;line-height:1.5"><b style="color:#fff">AST + AI Analysis</b><br>Static analysis with Gemini 2.0</div>
            </div>
            <div style="background:#0f0f0f;border:1px solid #1a1a1a;padding:1.5rem;border-radius:6px;text-align:left">
                <div style="color:#00ff88;font-size:1.5rem;margin-bottom:0.5rem">💰</div>
                <div style="font-size:0.8rem;color:#888;line-height:1.5"><b style="color:#fff">Debt Cost Calculator</b><br>Real git history dollar costs</div>
            </div>
            <div style="background:#0f0f0f;border:1px solid #1a1a1a;padding:1.5rem;border-radius:6px;text-align:left">
                <div style="color:#00ff88;font-size:1.5rem;margin-bottom:0.5rem">🤖</div>
                <div style="font-size:0.8rem;color:#888;line-height:1.5"><b style="color:#fff">AutoPilot Mode</b><br>Auto draft PRs on every push</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)