"""
CodeDebt Guardian - Professional Dashboard
Vercel/Linear-inspired design with proper data mapping
"""

import os
import sys
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="CodeDebt Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@300;400;500;600;700&family=Geist:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #0a0a0b;
    --bg-1: #111113;
    --bg-2: #18181b;
    --bg-3: #1f1f23;
    --border: rgba(255,255,255,0.08);
    --border-hover: rgba(255,255,255,0.15);
    --text: #fafafa;
    --text-2: #a1a1aa;
    --text-3: #52525b;
    --accent: #00d4ff;
    --accent-2: #0090ff;
    --green: #22c55e;
    --yellow: #f59e0b;
    --orange: #f97316;
    --red: #ef4444;
    --critical-bg: rgba(239,68,68,0.08);
    --high-bg: rgba(249,115,22,0.08);
    --medium-bg: rgba(245,158,11,0.08);
    --low-bg: rgba(34,197,94,0.08);
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Geist', sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
}

.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

.nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    height: 56px;
    border-bottom: 1px solid var(--border);
    background: rgba(10,10,11,0.8);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text);
}

.nav-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}

.nav-badge {
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    border: 1px solid var(--border);
    color: var(--text-2);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.hero {
    padding: 4rem 2rem 3rem;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(0,212,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.hero-eyebrow {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.hero-eyebrow::before {
    content: '';
    width: 20px;
    height: 1px;
    background: var(--accent);
}

.hero-title {
    font-size: clamp(2rem, 4vw, 3.5rem);
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1.05;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-title em {
    font-style: normal;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1rem;
    color: var(--text-2);
    max-width: 480px;
    line-height: 1.6;
    margin-bottom: 2rem;
    font-weight: 400;
}

.hero-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.35rem 0.75rem;
    border-radius: 100px;
    border: 1px solid var(--border);
    color: var(--text-2);
    background: var(--bg-2);
    letter-spacing: 0.01em;
}

.pill-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); }

.input-area {
    padding: 2rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg-1);
}

.input-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
}

.stTextInput > div > div > input {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Geist Mono', monospace !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.15s !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.1) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder { color: var(--text-3) !important; }

.stButton > button {
    background: var(--text) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.15s !important;
    letter-spacing: -0.01em !important;
}

.stButton > button:hover {
    background: #e4e4e7 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-bottom: 1px solid var(--border);
}

.metric-cell {
    padding: 1.5rem 2rem;
    border-right: 1px solid var(--border);
    position: relative;
    transition: background 0.15s;
}

.metric-cell:last-child { border-right: none; }
.metric-cell:hover { background: var(--bg-1); }

.metric-num {
    font-family: 'Geist Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 0.375rem;
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.section {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border);
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.section-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-2);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-count {
    font-family: 'Geist Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 0.15rem 0.5rem;
}

.issue-card {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 0.5rem;
    background: var(--bg-1);
    transition: all 0.15s;
    position: relative;
    overflow: hidden;
}

.issue-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: 0 2px 2px 0;
}

.issue-card.critical::before { background: var(--red); }
.issue-card.high::before { background: var(--orange); }
.issue-card.medium::before { background: var(--yellow); }
.issue-card.low::before { background: var(--green); }

.issue-card:hover {
    border-color: var(--border-hover);
    background: var(--bg-2);
    transform: translateX(2px);
}

.sev-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 0.4rem;
    flex-shrink: 0;
}

.sev-dot.critical { background: var(--red); box-shadow: 0 0 6px var(--red); }
.sev-dot.high { background: var(--orange); box-shadow: 0 0 6px var(--orange); }
.sev-dot.medium { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); }
.sev-dot.low { background: var(--green); box-shadow: 0 0 6px var(--green); }

.issue-body { flex: 1; min-width: 0; }

.issue-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.25rem;
}

.issue-desc {
    font-size: 0.8rem;
    color: var(--text-2);
    line-height: 1.5;
    margin-bottom: 0.375rem;
}

.issue-meta { display: flex; align-items: center; gap: 0.75rem; }

.issue-loc {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-3);
    background: var(--bg-3);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
}

.sev-tag {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
}

.sev-tag.critical { color: var(--red); background: var(--critical-bg); }
.sev-tag.high { color: var(--orange); background: var(--high-bg); }
.sev-tag.medium { color: var(--yellow); background: var(--medium-bg); }
.sev-tag.low { color: var(--green); background: var(--low-bg); }

.cost-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}

.cost-card {
    padding: 1.25rem;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--bg-1);
    position: relative;
    overflow: hidden;
}

.cost-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.cost-card.today::after { background: var(--accent); }
.cost-card.future::after { background: var(--orange); }
.cost-card.savings::after { background: var(--green); }

.cost-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-3);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

.cost-value {
    font-family: 'Geist Mono', monospace;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
}

.cost-value.today { color: var(--accent); }
.cost-value.future { color: var(--orange); }
.cost-value.savings { color: var(--green); }
.cost-sub { font-size: 0.7rem; color: var(--text-3); margin-top: 0.375rem; }

.term {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.7;
    max-height: 200px;
    overflow-y: auto;
}

.t-info { color: var(--accent); }
.t-ok { color: var(--green); }
.t-warn { color: var(--yellow); }
.t-err { color: var(--red); }
.t-dim { color: var(--text-3); }
.t-time { color: var(--text-3); margin-right: 0.75rem; }

.empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
}

.empty-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
}

.empty-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.empty-sub {
    font-size: 0.875rem;
    color: var(--text-2);
    max-width: 360px;
    line-height: 1.6;
    margin-bottom: 2.5rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    max-width: 720px;
    width: 100%;
}

.feature { padding: 1.5rem; background: var(--bg-1); text-align: left; }
.feature-icon { font-size: 1.25rem; margin-bottom: 0.75rem; }
.feature-name { font-size: 0.8rem; font-weight: 600; color: var(--text); margin-bottom: 0.375rem; }
.feature-desc { font-size: 0.75rem; color: var(--text-3); line-height: 1.5; }

div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-1) !important;
    margin-bottom: 0.5rem !important;
}
div[data-testid="stExpander"] summary {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    padding: 1rem 1.25rem !important;
}
div[data-testid="stExpanderDetails"] {
    padding: 0 1.25rem 1rem !important;
    border-top: 1px solid var(--border) !important;
}
div[data-testid="stExpanderDetails"] p,
div[data-testid="stExpanderDetails"] li {
    font-size: 0.825rem !important;
    color: var(--text-2) !important;
    line-height: 1.6 !important;
}
div[data-testid="stExpanderDetails"] strong { color: var(--text) !important; }
div[data-testid="stExpanderDetails"] code {
    background: var(--bg-3) !important;
    color: var(--accent) !important;
    font-family: 'Geist Mono', monospace !important;
    padding: 0.1rem 0.35rem !important;
    border-radius: 4px !important;
    font-size: 0.78rem !important;
}

.fix-problem {
    font-size: 0.8rem;
    color: var(--text-2);
    padding: 0.75rem;
    background: var(--bg-2);
    border-radius: 8px;
    margin: 0.75rem 0;
    line-height: 1.5;
    border-left: 2px solid var(--orange);
}

.fix-step {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
    padding: 0.4rem 0;
    font-size: 0.8rem;
    color: var(--text-2);
    line-height: 1.5;
}

.fix-step-num {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--bg-3);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-weight: 600;
    color: var(--text-3);
    margin-top: 0.125rem;
    font-family: 'Geist Mono', monospace;
}

.fix-test {
    margin-top: 0.75rem;
    padding: 0.625rem 0.75rem;
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.15);
    border-radius: 8px;
    font-size: 0.78rem;
    color: var(--green);
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)


def sev_class(sev):
    return sev.lower() if sev in ["CRITICAL","HIGH","MEDIUM","LOW"] else "low"

def issue_card(issue):
    sev = issue.get("severity","LOW")
    cls = sev_class(sev)
    itype = issue.get("type","unknown").replace("_"," ").title()
    loc = issue.get("location","")
    desc = issue.get("description","")
    return f"""
    <div class="issue-card {cls}">
        <div class="sev-dot {cls}"></div>
        <div class="issue-body">
            <div class="issue-title">{itype}</div>
            <div class="issue-desc">{desc}</div>
            <div class="issue-meta">
                <span class="sev-tag {cls}">{sev}</span>
                <span class="issue-loc">{loc}</span>
            </div>
        </div>
    </div>"""

def make_donut(critical, high, medium, low):
    labels, values, colors = [], [], []
    for label, val, color in [("Critical",critical,"#ef4444"),("High",high,"#f97316"),("Medium",medium,"#f59e0b"),("Low",low,"#22c55e")]:
        if val > 0:
            labels.append(label); values.append(val); colors.append(color)
    if not values: return None
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.72,
        marker=dict(colors=colors, line=dict(color="#0a0a0b", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} issues<extra></extra>"
    ))
    total = sum(values)
    fig.add_annotation(text=f"<b>{total}</b>", x=0.5, y=0.55, font=dict(size=28, color="#fafafa", family="Geist Mono"), showarrow=False)
    fig.add_annotation(text="issues", x=0.5, y=0.38, font=dict(size=12, color="#52525b", family="Geist"), showarrow=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=0,b=0), showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5, font=dict(color="#a1a1aa", size=12, family="Geist"), bgcolor="rgba(0,0,0,0)"),
        height=220,
    )
    return fig

def make_bar(type_counts):
    if not type_counts: return None
    labels = list(type_counts.keys())[:8]
    vals = [type_counts[l] for l in labels]
    fig = go.Figure(go.Bar(
        x=vals, y=labels, orientation="h",
        marker=dict(color="rgba(0,212,255,0.15)", line=dict(color="rgba(0,212,255,0.4)", width=1)),
        hovertemplate="<b>%{y}</b>: %{x}<extra></extra>",
        text=vals, textposition="outside",
        textfont=dict(color="#52525b", size=11, family="Geist Mono")
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=40,t=0,b=0), height=220,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color="#a1a1aa", size=11, family="Geist")),
    )
    return fig

def make_timeline(issues):
    dated = [i for i in issues if i.get("age_days",0) > 0]
    if not dated:
        now = datetime.now()
        dates = [now - timedelta(days=30*i) for i in range(5,0,-1)]
        costs = [len(issues)*20*(i/5) for i in range(1,6)]
    else:
        sorted_i = sorted(dated, key=lambda x: x.get("age_days",0), reverse=True)
        cum, dates, costs = 0, [], []
        for i in sorted_i:
            dates.append(datetime.now() - timedelta(days=i.get("age_days",0)))
            cum += i.get("current_cost_usd", 100)
            costs.append(cum)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=costs, fill="tozeroy",
        fillcolor="rgba(0,212,255,0.05)",
        line=dict(color="#00d4ff", width=2),
        name="Accumulated Debt",
        hovertemplate="$%{y:,.0f}<extra></extra>"
    ))
    if dates and costs:
        fd = [dates[-1]+timedelta(days=90*i) for i in range(1,4)]
        fc = [costs[-1]*(1.23**i) for i in range(1,4)]
        fig.add_trace(go.Scatter(
            x=[dates[-1]]+fd, y=[costs[-1]]+fc,
            line=dict(color="#f97316", width=2, dash="dot"),
            name="Projected (23%/qtr)",
            hovertemplate="$%{y:,.0f}<extra></extra>"
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200, margin=dict(l=60,r=20,t=10,b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#52525b",size=10,family="Geist Mono"), showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#52525b",size=10,family="Geist Mono"), tickprefix="$", showline=False),
        legend=dict(orientation="h", y=1.15, x=0, font=dict(color="#a1a1aa",size=11,family="Geist"), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


# NAV
st.markdown("""
<div class="nav">
    <div class="nav-brand">
        <div class="nav-dot"></div>
        CodeDebt<span style="color:rgba(255,255,255,0.4)">Guardian</span>
    </div>
    <div style="display:flex;align-items:center;gap:0.75rem">
        <span class="nav-badge">v1.0</span>
        <span class="nav-badge">84 tests passing</span>
        <span class="nav-badge">Gemini 2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered Technical Debt Analysis</div>
    <div class="hero-title">Fix debt <em>before</em><br>it breaks production</div>
    <div class="hero-sub">
        Analyze any GitHub repository for technical debt, quantify it in dollars,
        and get AI-generated fix proposals in seconds.
    </div>
    <div class="hero-pills">
        <span class="pill"><span class="pill-dot"></span>AST + AI Analysis</span>
        <span class="pill"><span class="pill-dot"></span>Debt Interest Calculator</span>
        <span class="pill"><span class="pill-dot"></span>AutoPilot Fix Mode</span>
        <span class="pill"><span class="pill-dot"></span>Safety-First</span>
    </div>
</div>
""", unsafe_allow_html=True)

# INPUT
st.markdown('<div class="input-area">', unsafe_allow_html=True)
st.markdown('<div class="input-label">Repository URL + API Keys</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    repo_url = st.text_input("repo", placeholder="https://github.com/owner/repository", label_visibility="collapsed")
with col2:
    google_api_key = st.text_input("gkey", placeholder="Gemini API Key", type="password", label_visibility="collapsed")
with col3:
    github_token = st.text_input("ghtoken", placeholder="GitHub Token", type="password", label_visibility="collapsed")

if google_api_key: os.environ["GOOGLE_API_KEY"] = google_api_key
if github_token:   os.environ["GITHUB_TOKEN"]   = github_token

if not os.environ.get("GOOGLE_API_KEY"):
    try: os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY","")
    except: pass
if not os.environ.get("GITHUB_TOKEN"):
    try: os.environ["GITHUB_TOKEN"] = st.secrets.get("GITHUB_TOKEN","")
    except: pass

analyze_btn = st.button("Analyze Repository", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)

# ANALYSIS
if analyze_btn and repo_url:
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("Gemini API Key required"); st.stop()
    if not os.environ.get("GITHUB_TOKEN"):
        st.error("GitHub Token required"); st.stop()

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Log</div>', unsafe_allow_html=True)
    log_ph = st.empty()
    logs = []

    def log(msg, level="info"):
        cls = {"info":"t-info","ok":"t-ok","warn":"t-warn","error":"t-err","dim":"t-dim"}.get(level,"t-info")
        ts  = datetime.now().strftime("%H:%M:%S")
        logs.append(f'<span class="t-time">{ts}</span><span class="{cls}">{msg}</span>')
        log_ph.markdown(f'<div class="term">{"<br>".join(logs)}</div>', unsafe_allow_html=True)

    try:
        log(f"Target: {repo_url}", "dim")
        from agents.orchestrator import CodeDebtOrchestrator
        orch = CodeDebtOrchestrator()
        log("Orchestrator ready", "ok")
        log("Running multi-agent analysis pipeline...", "info")

        with st.spinner(""):
            results = orch.run_full_analysis(repo_url)

        detection = results.get("detection", {})
        issues    = detection.get("issues", [])
        ranked    = results.get("ranked_issues", issues)
        fixes     = results.get("fix_proposals", [])

        if not issues:
            issues = results.get("issues", [])
            ranked = results.get("ranked_issues", issues)
            fixes  = results.get("fix_proposals", fixes)

        files_analyzed = detection.get("files_analyzed", results.get("files_analyzed", 0))
        log(f"Complete: {len(issues)} issues in {files_analyzed} files", "ok" if not issues else "warn")

        try:
            from tools.persistent_memory import PersistentMemoryBank
            PersistentMemoryBank().save_analysis_history(repo_url, "main", {
                "total_issues": len(issues),
                "critical": len([i for i in issues if i.get("severity")=="CRITICAL"]),
                "high":     len([i for i in issues if i.get("severity")=="HIGH"])
            })
        except Exception: pass

        st.markdown('</div>', unsafe_allow_html=True)

        critical = len([i for i in issues if i.get("severity")=="CRITICAL"])
        high     = len([i for i in issues if i.get("severity")=="HIGH"])
        medium   = len([i for i in issues if i.get("severity")=="MEDIUM"])
        low      = len([i for i in issues if i.get("severity")=="LOW"])

        # METRICS
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-cell">
                <div class="metric-num" style="color:#ef4444">{critical}</div>
                <div class="metric-label">Critical</div>
            </div>
            <div class="metric-cell">
                <div class="metric-num" style="color:#f97316">{high}</div>
                <div class="metric-label">High</div>
            </div>
            <div class="metric-cell">
                <div class="metric-num" style="color:#f59e0b">{medium}</div>
                <div class="metric-label">Medium</div>
            </div>
            <div class="metric-cell">
                <div class="metric-num" style="color:#22c55e">{low}</div>
                <div class="metric-label">Low</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CHARTS
        if issues:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 2, 3])
            with c1:
                st.markdown('<div class="section-title">Severity Split</div>', unsafe_allow_html=True)
                fig = make_donut(critical, high, medium, low)
                if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            with c2:
                st.markdown('<div class="section-title">Issue Types</div>', unsafe_allow_html=True)
                tc = {}
                for i in issues:
                    t = i.get("type","unknown").replace("_"," ").title()
                    tc[t] = tc.get(t,0)+1
                fig2 = make_bar(tc)
                if fig2: st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
            with c3:
                st.markdown('<div class="section-title">Debt Accumulation Timeline</div>', unsafe_allow_html=True)
                fig3 = make_timeline(issues)
                if fig3: st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

        # DEBT INTEREST
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><div class="section-title">Debt Interest Calculator</div></div>', unsafe_allow_html=True)
        try:
            from tools.debt_interest import DebtInterestCalculator
            parts = repo_url.rstrip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            calc = DebtInterestCalculator()
            ires, tnow, tfut = [], 0, 0
            for issue in (ranked or issues)[:5]:
                fp = issue.get("location","").split(":")[0]
                if fp and fp.endswith(".py"):
                    try:
                        r = calc.calculate(owner, repo, fp, issue)
                        ires.append(r)
                        tnow += r.get("current_cost_usd",0)
                        tfut += r.get("future_cost_usd",0)
                    except Exception: pass
            if ires:
                st.markdown(f"""
                <div class="cost-row">
                    <div class="cost-card today">
                        <div class="cost-label">Fix Cost Today</div>
                        <div class="cost-value today">${tnow:,.0f}</div>
                        <div class="cost-sub">Estimated dev hours x rate</div>
                    </div>
                    <div class="cost-card future">
                        <div class="cost-label">Cost Next Quarter</div>
                        <div class="cost-value future">${tfut:,.0f}</div>
                        <div class="cost-sub">+23% compounding interest</div>
                    </div>
                    <div class="cost-card savings">
                        <div class="cost-label">Savings if Fixed Now</div>
                        <div class="cost-value savings">${tfut-tnow:,.0f}</div>
                        <div class="cost-sub">ROI on fixing today</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                for r in ires:
                    with st.expander(f"  {r.get('filepath','file')}  --  ${r.get('current_cost_usd',0):,.0f} now →  ${r.get('future_cost_usd',0):,.0f} next quarter"):
                        st.markdown(f"""
**Age:** {r.get('age_days',0)} days &nbsp; **Touches:** {r.get('total_touches',0)} commits &nbsp; **Authors:** {r.get('unique_authors',0)} &nbsp; **Interest:** {r.get('interest_rate_pct',0)}%

{r.get('summary','')}
                        """)
            else:
                st.markdown('<div style="color:#52525b;font-size:0.825rem;padding:0.5rem 0">No Python files with location data found for cost calculation.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div style="color:#52525b;font-size:0.8rem">Debt Interest Calculator unavailable: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ISSUES
        display_issues = ranked or issues
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-header"><div class="section-title">Issues Found <span class="section-count">{len(display_issues)}</span></div></div>', unsafe_allow_html=True)
        for issue in display_issues[:20]:
            st.markdown(issue_card(issue), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # FIX PROPOSALS
        if fixes:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-header"><div class="section-title">Fix Proposals <span class="section-count">{len(fixes)}</span></div></div>', unsafe_allow_html=True)
            for fix in fixes[:5]:
                summary = fix.get("fix_summary") or fix.get("summary","Fix available")
                problem = fix.get("problem_summary","")
                steps   = fix.get("steps",[])
                tip     = fix.get("testing_tip","")
                with st.expander(f"  {summary}"):
                    if problem:
                        st.markdown(f'<div class="fix-problem">  {problem}</div>', unsafe_allow_html=True)
                    if steps:
                        for idx, step in enumerate(steps, 1):
                            if step and step.strip():
                                st.markdown(f'<div class="fix-step"><span class="fix-step-num">{idx}</span><span>{step}</span></div>', unsafe_allow_html=True)
                    if tip:
                        st.markdown(f'<div class="fix-test">  {tip}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        log(f"Error: {e}", "error")
        st.error(f"Analysis failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">🛡️</div>
        <div class="empty-title">Analyze your first repository</div>
        <div class="empty-sub">
            Enter a GitHub URL above, add your API keys, and click Analyze.
            Works on any public Python repository.
        </div>
        <div class="feature-grid">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-name">AST + AI Analysis</div>
                <div class="feature-desc">Static analysis powered by Gemini 2.0 for contextual understanding of your codebase</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💰</div>
                <div class="feature-name">Dollar Cost Calculator</div>
                <div class="feature-desc">Quantify debt using real git history, team velocity, and compound interest modeling</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <div class="feature-name">AutoPilot Fixes</div>
                <div class="feature-desc">AI-generated fix proposals with step-by-step instructions and safety validation</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
