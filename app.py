"""
app.py — FastAPI server for IT Helpdesk Triage OpenEnv environment.
Premium redesigned landing page for hackathon judges.
"""

from __future__ import annotations
import logging, os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from environment import ITTriageEnvironment
from models import EnvironmentState, Observation, StepResult, TriageAction

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IT Helpdesk Triage & Incident Management — OpenEnv",
    description="Production-grade OpenEnv RL environment simulating an enterprise IT service desk.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

env = ITTriageEnvironment()

class ResetRequest(BaseModel):
    task_id: str = "basic_triage"

# ─────────────────────────────────────────────────────────────────────────────
LANDING_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IT Helpdesk Triage — OpenEnv</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #060811;
  --surface: #0c1020;
  --card: #111827;
  --card2: #0f172a;
  --border: #1e2d4a;
  --border2: #243352;
  --accent: #3b82f6;
  --accent2: #6366f1;
  --green: #10b981;
  --yellow: #f59e0b;
  --red: #ef4444;
  --text: #f1f5f9;
  --muted: #64748b;
  --muted2: #94a3b8;
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Inter', system-ui, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  line-height: 1.6;
  overflow-x: hidden;
}

/* ── NOISE TEXTURE ── */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

/* ── HERO ── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 6rem 2rem 4rem;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  width: 900px; height: 900px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, rgba(99,102,241,0.06) 40%, transparent 70%);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  animation: breathe 8s ease-in-out infinite;
}
.hero::after {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%);
  bottom: 10%; right: 10%;
  pointer-events: none;
  animation: breathe 6s ease-in-out infinite reverse;
}

@keyframes breathe {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
  50%       { transform: translate(-50%, -50%) scale(1.1); opacity: 0.7; }
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  border: 1px solid;
}
.badge-blue   { background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.3); color: #93c5fd; }
.badge-green  { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.3); color: #6ee7b7; }
.badge-purple { background: rgba(99,102,241,0.12); border-color: rgba(99,102,241,0.3); color: #c4b5fd; }
.live-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

.hero h1 {
  font-size: clamp(2.4rem, 6vw, 4.5rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  position: relative;
}
.hero h1 .line1 { display: block; color: var(--text); }
.hero h1 .line2 {
  display: block;
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero h1 .line3 { display: block; color: var(--text); }

.hero-sub {
  font-size: 1.1rem;
  color: var(--muted2);
  max-width: 580px;
  margin: 0 auto 3rem;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.8rem;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  box-shadow: 0 4px 24px rgba(59,130,246,0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(59,130,246,0.45); }
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.6rem;
  background: rgba(255,255,255,0.04);
  color: var(--muted2);
  border: 1px solid var(--border2);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}
.btn-secondary:hover { border-color: var(--accent); color: var(--text); background: rgba(59,130,246,0.06); }

/* ── STATS STRIP ── */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}
.stat {
  background: var(--card2);
  padding: 1.5rem 1.2rem;
  text-align: center;
}
.stat-num {
  font-size: 2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  line-height: 1.2;
}
.stat-label { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; font-weight: 500; letter-spacing: 0.04em; }

/* ── SECTION ── */
section { position: relative; padding: 5rem 2rem; }
.container { max-width: 1100px; margin: 0 auto; }
.section-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}
.section-tag::before {
  content: '';
  display: inline-block;
  width: 20px;
  height: 2px;
  background: var(--accent);
  border-radius: 2px;
}
h2 { font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
.section-sub { color: var(--muted2); margin-bottom: 3rem; font-size: 1rem; }

/* ── TASK CARDS ── */
.tasks-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 1.5rem; }
.task-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
  cursor: default;
}
.task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.task-card.easy:hover   { border-color: var(--green); box-shadow: 0 20px 60px rgba(16,185,129,0.15); }
.task-card.medium:hover { border-color: var(--yellow); box-shadow: 0 20px 60px rgba(245,158,11,0.15); }
.task-card.hard:hover   { border-color: var(--red); box-shadow: 0 20px 60px rgba(239,68,68,0.15); }

.task-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.task-card.easy::after   { background: linear-gradient(90deg, var(--green), transparent); }
.task-card.medium::after { background: linear-gradient(90deg, var(--yellow), transparent); }
.task-card.hard::after   { background: linear-gradient(90deg, var(--red), transparent); }

.task-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin-bottom: 1.2rem;
}
.easy   .task-icon { background: rgba(16,185,129,0.12); }
.medium .task-icon { background: rgba(245,158,11,0.12); }
.hard   .task-icon { background: rgba(239,68,68,0.12); }

.diff-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}
.easy   .diff-badge { background: rgba(16,185,129,0.15); color: #34d399; }
.medium .diff-badge { background: rgba(245,158,11,0.15); color: #fbbf24; }
.hard   .diff-badge { background: rgba(239,68,68,0.15); color: #f87171; }

.task-card h3 { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.75rem; }
.task-card p  { font-size: 0.875rem; color: var(--muted2); line-height: 1.65; margin-bottom: 1.5rem; }

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: var(--muted);
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

/* ── REWARD SECTION ── */
.reward-section { background: var(--surface); }
.reward-layout  { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: start; }
@media(max-width:768px) { .reward-layout { grid-template-columns: 1fr; gap: 2rem; } }

.reward-bars { display: flex; flex-direction: column; gap: 1rem; }
.rbar-item {}
.rbar-header { display: flex; justify-content: space-between; margin-bottom: 0.4rem; }
.rbar-label  { font-size: 0.85rem; font-weight: 600; }
.rbar-pct    { font-size: 0.85rem; color: var(--accent); font-weight: 700; font-family: var(--mono); }
.rbar-track  { height: 8px; background: rgba(255,255,255,0.06); border-radius: 99px; overflow: hidden; }
.rbar-fill   { height: 100%; border-radius: 99px; transition: width 1s ease; }
.rbar-sub    { font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; }

.reward-desc h3   { font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; }
.reward-desc p    { color: var(--muted2); font-size: 0.9rem; line-height: 1.7; margin-bottom: 1rem; }
.signal-list { list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }
.signal-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--muted2);
}
.signal-list li::before { content: '▸'; color: var(--accent); flex-shrink: 0; margin-top: 2px; }

/* ── ENDPOINTS ── */
.ep-grid { display: flex; flex-direction: column; gap: 2px; }
.ep-row {
  display: grid;
  grid-template-columns: 70px 180px 1fr;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 1.25rem;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  transition: border-color 0.2s, background 0.2s;
}
.ep-row:hover { border-color: var(--border2); background: var(--card2); }
.method {
  font-family: var(--mono);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  text-align: center;
  letter-spacing: 0.05em;
}
.m-get  { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.m-post { background: rgba(59,130,246,0.12); color: #93c5fd; border: 1px solid rgba(59,130,246,0.25); }
.ep-path { font-family: var(--mono); font-size: 0.9rem; color: var(--accent); font-weight: 500; }
.ep-desc { font-size: 0.83rem; color: var(--muted2); }

/* ── CODE DEMO ── */
.code-section { background: var(--surface); }
.code-layout  { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
@media(max-width:768px) { .code-layout { grid-template-columns: 1fr; } }

.code-panel {
  background: #040810;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
}
.code-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 1.25rem;
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid var(--border);
}
.code-dots { display: flex; gap: 6px; }
.code-dots span {
  width: 12px; height: 12px;
  border-radius: 50%;
}
.code-dots span:nth-child(1) { background: #ff5f57; }
.code-dots span:nth-child(2) { background: #febc2e; }
.code-dots span:nth-child(3) { background: #28c840; }
.code-title { font-size: 0.78rem; color: var(--muted); font-family: var(--mono); margin-left: 0.5rem; }

.code-body {
  padding: 1.25rem 1.5rem;
  font-family: var(--mono);
  font-size: 0.8rem;
  line-height: 2;
  overflow-x: auto;
}
.c  { color: #4a5568; }
.s  { color: #68d391; }
.k  { color: #76e4f7; }
.kw { color: #b794f4; }
.n  { color: #fbb6ce; }
.v  { color: #f6ad55; }

/* ── LIVE RESPONSE ── */
.json-panel {
  background: #040810;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
}
.json-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid var(--border);
}
.json-title { font-size: 0.78rem; color: var(--muted); font-family: var(--mono); }
.json-status {
  font-size: 0.7rem;
  background: rgba(16,185,129,0.15);
  color: #34d399;
  border: 1px solid rgba(16,185,129,0.3);
  padding: 0.15rem 0.5rem;
  border-radius: 5px;
  font-family: var(--mono);
}
.json-body {
  padding: 1.25rem 1.5rem;
  font-family: var(--mono);
  font-size: 0.78rem;
  line-height: 1.9;
  overflow-x: auto;
  color: var(--muted2);
}
.jk { color: #76e4f7; }
.js { color: #68d391; }
.jn { color: #f6ad55; }
.jb { color: #b794f4; }

/* ── FLOW ── */
.flow-steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; position: relative; }
.flow-step {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.75rem 1.5rem;
  text-align: center;
  position: relative;
  transition: border-color 0.2s, transform 0.2s;
}
.flow-step:hover { border-color: var(--accent); transform: translateY(-3px); }
.step-num {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  font-weight: 800;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  box-shadow: 0 4px 16px rgba(59,130,246,0.35);
}
.flow-step h4 { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem; }
.flow-step p  { font-size: 0.8rem; color: var(--muted2); line-height: 1.5; }

/* ── FOOTER ── */
footer {
  text-align: center;
  padding: 3rem 2rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.85rem;
}
footer a { color: var(--accent); text-decoration: none; }
footer a:hover { text-decoration: underline; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── DIVIDER ── */
.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border2), transparent);
  margin: 0;
}
</style>
</head>
<body>

<!-- ═══════════════════ HERO ═══════════════════ -->
<section class="hero">
  <div class="badge-row">
    <span class="badge badge-blue"><span class="live-dot"></span> Running on HF Spaces</span>
    <span class="badge badge-green">OpenEnv Compliant</span>
    <span class="badge badge-purple">Meta × Hugging Face Hackathon</span>
  </div>

  <h1>
    <span class="line1">IT Helpdesk</span>
    <span class="line2">Triage &amp; Incident</span>
    <span class="line3">Management</span>
  </h1>

  <p class="hero-sub">
    A production-grade OpenEnv RL environment where AI agents classify, prioritise, route,
    and escalate real enterprise IT tickets — including cascading major incident detection
    with dense, multi-dimensional reward shaping.
  </p>

  <div class="hero-actions">
    <a class="btn-primary" href="/docs">📖 Interactive API Docs</a>
    <a class="btn-secondary" href="/health">🔍 Health Check</a>
    <a class="btn-secondary" href="/tasks">🗂 All Tasks</a>
  </div>

  <div class="stats-strip">
    <div class="stat">
      <span class="stat-num">3</span>
      <span class="stat-label">Difficulty Tiers</span>
    </div>
    <div class="stat">
      <span class="stat-num">17</span>
      <span class="stat-label">Curated Tickets</span>
    </div>
    <div class="stat">
      <span class="stat-num">6</span>
      <span class="stat-label">Reward Dimensions</span>
    </div>
    <div class="stat">
      <span class="stat-num">1.0</span>
      <span class="stat-label">Max Score</span>
    </div>
    <div class="stat">
      <span class="stat-num">35</span>
      <span class="stat-label">Total Max Steps</span>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════ TASKS ═══════════════════ -->
<section>
  <div class="container">
    <div class="section-tag">Tasks</div>
    <h2>Three Tiers of Challenge</h2>
    <p class="section-sub">Progressive difficulty — from routine helpdesk triage to managing a live production database incident.</p>

    <div class="tasks-grid">

      <div class="task-card easy">
        <div class="task-icon">🎫</div>
        <span class="diff-badge">EASY</span>
        <h3>Basic Triage</h3>
        <p>Classify 5 realistic IT support tickets across category (hardware, network, security, access, software), priority P1–P4, and the correct resolver team. Perfect for warming up an agent's ITIL reasoning.</p>
        <div class="task-meta">
          <span class="meta-chip">🎫 5 tickets</span>
          <span class="meta-chip">⏱ 10 max steps</span>
          <span class="meta-chip">📊 3 grader dims</span>
        </div>
      </div>

      <div class="task-card medium">
        <div class="task-icon">⚡</div>
        <span class="diff-badge">MEDIUM</span>
        <h3>Priority Routing</h3>
        <p>5 high-stakes tickets: a payroll batch missing bank cut-off, e-commerce 503s with $800/min revenue loss, and a multi-vector security breach. Agent must detect incidents and escalate to C-suite.</p>
        <div class="task-meta">
          <span class="meta-chip">🎫 5 tickets</span>
          <span class="meta-chip">⏱ 10 max steps</span>
          <span class="meta-chip">📊 5 grader dims</span>
        </div>
      </div>

      <div class="task-card hard">
        <div class="task-icon">🚨</div>
        <span class="diff-badge">HARD</span>
        <h3>Incident Escalation</h3>
        <p>Cascading PostgreSQL WAL-corruption: 7 tickets, 5 are symptoms of the same root cause. Identify the incident, declare INC-MAJOR-01, and provide ordered DB failover remediation steps per P1 ticket.</p>
        <div class="task-meta">
          <span class="meta-chip">🎫 7 tickets</span>
          <span class="meta-chip">⏱ 15 max steps</span>
          <span class="meta-chip">📊 6 grader dims</span>
        </div>
      </div>

    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════ REWARD ═══════════════════ -->
<section class="reward-section">
  <div class="container">
    <div class="reward-layout">

      <div>
        <div class="section-tag">Reward Function</div>
        <h2>Dense, Shaped Signal</h2>
        <p class="section-sub">Not just binary win/loss. Every step provides partial-credit feedback across 6 independent dimensions.</p>

        <div class="reward-bars">
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Category Classification</span><span class="rbar-pct">40%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:40%;background:linear-gradient(90deg,#3b82f6,#6366f1)"></div></div>
            <div class="rbar-sub">Easy primary signal / 20% in Hard</div>
          </div>
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Priority Assignment</span><span class="rbar-pct">35%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:35%;background:linear-gradient(90deg,#6366f1,#8b5cf6)"></div></div>
            <div class="rbar-sub">Partial credit for ±1 level miss</div>
          </div>
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Team Routing</span><span class="rbar-pct">25%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:25%;background:linear-gradient(90deg,#8b5cf6,#a78bfa)"></div></div>
            <div class="rbar-sub">6 specialist teams — exact match</div>
          </div>
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Incident Detection</span><span class="rbar-pct">20%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:20%;background:linear-gradient(90deg,#10b981,#34d399)"></div></div>
            <div class="rbar-sub">Medium + Hard only</div>
          </div>
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Escalation Decision</span><span class="rbar-pct">14%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:14%;background:linear-gradient(90deg,#f59e0b,#fbbf24)"></div></div>
            <div class="rbar-sub">Penalises over-escalation of P4 tickets</div>
          </div>
          <div class="rbar-item">
            <div class="rbar-header"><span class="rbar-label">Remediation Steps</span><span class="rbar-pct">16%</span></div>
            <div class="rbar-track"><div class="rbar-fill" style="width:16%;background:linear-gradient(90deg,#ef4444,#f87171)"></div></div>
            <div class="rbar-sub">Hard only — NLP keyword + step recall scoring</div>
          </div>
        </div>
      </div>

      <div class="reward-desc">
        <h3>Why this reward design?</h3>
        <p>Most RL environments reward only final success. Our grader signals progress <em>throughout</em> the episode, making it suitable for policy gradient and GRPO training without sparse reward hacking.</p>
        <ul class="signal-list">
          <li>Scores bounded [0.0, 1.0] per step — deterministic and reproducible</li>
          <li>Partial credit means agents learn from near-misses, not just failures</li>
          <li>Weighted by task difficulty — harder tasks unlock more reward dimensions</li>
          <li>Escalation penalty prevents reward hacking via always-escalate strategies</li>
          <li>NLP-graded remediation steps reward semantic coverage, not exact string match</li>
          <li>Resolution steps scored on keyword recall + ordered step matching (0.35 + 0.65)</li>
        </ul>
      </div>

    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════ ENDPOINTS ═══════════════════ -->
<section>
  <div class="container">
    <div class="section-tag">API</div>
    <h2>OpenEnv Spec Compliant</h2>
    <p class="section-sub">Full reset / step / state interface. Every endpoint returns typed Pydantic models.</p>

    <div class="ep-grid">
      <div class="ep-row">
        <span class="method m-get">GET</span>
        <span class="ep-path">/health</span>
        <span class="ep-desc">JSON health check — automated validation gate (returns 200 + tasks list)</span>
      </div>
      <div class="ep-row">
        <span class="method m-post">POST</span>
        <span class="ep-path">/reset</span>
        <span class="ep-desc">Start a new episode — accepts <code>task_id</code>, returns typed <code>Observation</code> with first ticket</span>
      </div>
      <div class="ep-row">
        <span class="method m-post">POST</span>
        <span class="ep-path">/step</span>
        <span class="ep-desc">Submit <code>TriageAction</code> — returns <code>(Observation, reward∈[0,1], done, info)</code> with reward breakdown</span>
      </div>
      <div class="ep-row">
        <span class="method m-get">GET</span>
        <span class="ep-path">/state</span>
        <span class="ep-desc">Full serialisable <code>EnvironmentState</code> — action history, reward history, declared incidents</span>
      </div>
      <div class="ep-row">
        <span class="method m-get">GET</span>
        <span class="ep-path">/tasks</span>
        <span class="ep-desc">All tasks with difficulty, ticket count, max_steps, and grader weight breakdowns</span>
      </div>
      <div class="ep-row">
        <span class="method m-get">GET</span>
        <span class="ep-path">/docs</span>
        <span class="ep-desc">Interactive Swagger UI — test every endpoint live with real request/response</span>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════ CODE DEMO ═══════════════════ -->
<section class="code-section">
  <div class="container">
    <div class="section-tag">Quick Start</div>
    <h2>Try it in 3 steps</h2>
    <p class="section-sub">Standard OpenEnv interface — works with any OpenAI-compatible agent.</p>

    <div class="code-layout">
      <div class="code-panel">
        <div class="code-header">
          <div class="code-dots"><span></span><span></span><span></span></div>
          <span class="code-title">curl / terminal</span>
        </div>
        <div class="code-body">
<span class="c"># 1 — Reset for easy task</span>
<span class="kw">curl</span> -X POST \
  <span class="s">https://hyperlinken-triage.hf.space/reset</span> \
  -H <span class="s">'Content-Type: application/json'</span> \
  -d <span class="s">'{"task_id":"basic_triage"}'</span>

<span class="c"># 2 — Submit a triage decision</span>
<span class="kw">curl</span> -X POST \
  <span class="s">https://hyperlinken-triage.hf.space/step</span> \
  -H <span class="s">'Content-Type: application/json'</span> \
  -d <span class="s">'{
  "ticket_id": "TKT-E001",
  "category":  "hardware",
  "priority":  "P3",
  "assigned_team": "helpdesk",
  "is_part_of_incident": false,
  "escalate_to_management": false
}'</span>

<span class="c"># 3 — Inspect full state</span>
<span class="kw">curl</span> <span class="s">https://hyperlinken-triage.hf.space/state</span>
        </div>
      </div>

      <div class="json-panel">
        <div class="json-header">
          <span class="json-title">POST /step → response</span>
          <span class="json-status">200 OK</span>
        </div>
        <div class="json-body">
{
  <span class="jk">"observation"</span>: {
    <span class="jk">"task_id"</span>: <span class="js">"basic_triage"</span>,
    <span class="jk">"current_ticket"</span>: {
      <span class="jk">"id"</span>: <span class="js">"TKT-E002"</span>,
      <span class="jk">"subject"</span>: <span class="js">"Cannot log into Salesforce"</span>,
      <span class="jk">"priority_hint"</span>: <span class="js">"SLA: 4h"</span>
    },
    <span class="jk">"queue_remaining"</span>: <span class="jn">3</span>,
    <span class="jk">"cumulative_score"</span>: <span class="jn">1.0</span>,
    <span class="jk">"action_feedback"</span>: <span class="js">"category=correct(hardware)
  priority=correct(P3)
  team=correct(helpdesk)
  reward=1.000"</span>
  },
  <span class="jk">"reward"</span>: <span class="jn">1.0</span>,
  <span class="jk">"done"</span>: <span class="jb">false</span>,
  <span class="jk">"info"</span>: {
    <span class="jk">"reward_breakdown"</span>: {
      <span class="jk">"category_score"</span>: <span class="jn">1.0</span>,
      <span class="jk">"priority_score"</span>:  <span class="jn">1.0</span>,
      <span class="jk">"routing_score"</span>:   <span class="jn">1.0</span>
    }
  }
}
        </div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════ FLOW ═══════════════════ -->
<section>
  <div class="container">
    <div class="section-tag">How It Works</div>
    <h2>The RL Loop</h2>
    <p class="section-sub">Standard OpenEnv interface compatible with TRL, SkyRL, and any GRPO trainer.</p>

    <div class="flow-steps">
      <div class="flow-step">
        <div class="step-num">1</div>
        <h4>POST /reset</h4>
        <p>Agent receives first ticket in queue as typed <code>Observation</code></p>
      </div>
      <div class="flow-step">
        <div class="step-num">2</div>
        <h4>Read Ticket</h4>
        <p>Subject, description, affected systems, SLA, reporter department</p>
      </div>
      <div class="flow-step">
        <div class="step-num">3</div>
        <h4>POST /step</h4>
        <p>Submit <code>TriageAction</code> — category, priority, team, incident flag</p>
      </div>
      <div class="flow-step">
        <div class="step-num">4</div>
        <h4>Receive Reward</h4>
        <p>Dense per-step reward [0–1] with breakdown across all 6 dimensions</p>
      </div>
      <div class="flow-step">
        <div class="step-num">5</div>
        <h4>Repeat</h4>
        <p>Until queue exhausted or max steps — then check cumulative score</p>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════ FOOTER ═══════════════════ -->
<footer>
  <p style="margin-bottom:.5rem">
    <strong style="color:var(--text)">IT Helpdesk Triage OpenEnv</strong> &nbsp;·&nbsp; v1.0.0 &nbsp;·&nbsp;
    Built for <strong>Meta × Hugging Face AI Hackathon</strong>
  </p>
  <p>
    <a href="/docs">Swagger UI</a> &nbsp;·&nbsp;
    <a href="/redoc">ReDoc</a> &nbsp;·&nbsp;
    <a href="/health">Health</a> &nbsp;·&nbsp;
    <a href="/tasks">Tasks</a>
  </p>
</footer>

</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing():
    return HTMLResponse(content=LANDING_HTML)

@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok", "environment": "IT Helpdesk Triage & Incident Management", "version": "1.0.0", "tasks": env.list_tasks()}

@app.post("/reset", response_model=Observation, summary="Reset environment")
def reset(request: ResetRequest):
    try:
        obs = env.reset(task_id=request.task_id)
        logger.info("Episode reset | task=%s", request.task_id)
        return obs
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/step", response_model=StepResult, summary="Execute triage action")
def step(action: TriageAction):
    try:
        result = env.step(action)
        logger.info("Step %d | ticket=%s | reward=%.4f | done=%s", result.observation.step_number, action.ticket_id, result.reward, result.done)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/state", response_model=EnvironmentState, summary="Get environment state")
def state():
    return env.state()

@app.get("/tasks", summary="List available tasks")
def list_tasks():
    return env.list_tasks()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False, log_level="info")
