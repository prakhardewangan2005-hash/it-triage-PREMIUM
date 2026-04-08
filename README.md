---
title: IT Helpdesk Triage & Incident Management
emoji: 🎫
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags:
  - openenv
  - reinforcement-learning
  - enterprise-ai
  - it-operations
license: apache-2.0
---

# 🎫 IT Helpdesk Triage & Incident Management — OpenEnv

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-brightgreen)](https://huggingface.co/openenv)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange)](LICENSE)

A **production-grade OpenEnv RL training environment** that simulates a real enterprise IT Service Desk. An AI agent receives incoming IT support tickets and must make triage decisions across five dimensions — culminating in the management of a cascading database outage spanning seven simultaneous tickets.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   OpenEnv Interface                      │
│  POST /reset  ──►  Observation (first ticket in queue)  │
│  POST /step   ──►  StepResult (obs + reward + done)     │
│  GET  /state  ──►  EnvironmentState (full snapshot)     │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │   ITTriageEnvironment (core)   │
         │                                │
         │  Task Registry                 │
         │  ├─ basic_triage    (easy)     │
         │  ├─ priority_routing (medium)  │
         │  └─ incident_escalation (hard) │
         │                                │
         │  Dense Reward Engine           │
         │  ├─ Category score (exact)     │
         │  ├─ Priority score (partial)   │
         │  ├─ Routing score  (exact)     │
         │  ├─ Incident score (bonus)     │
         │  ├─ Escalation score           │
         │  └─ Resolution score (NLP)     │
         └────────────────────────────────┘
```

---

## 🗂️ Environment Description

### Real-world motivation
Every enterprise runs an IT service desk. Triage quality — getting the right ticket to the right team at the right priority — directly affects business continuity, SLA compliance, and employee productivity. Training AI agents on realistic triage tasks produces models immediately applicable to production helpdesk automation.

### Episode structure
Each episode processes a queue of IT support tickets. The agent sees **one ticket per step** and must return a `TriageAction`. The episode ends when the queue is exhausted or `max_steps` is reached.

---

## 📐 Action Space

```python
class TriageAction(BaseModel):
    ticket_id:              str             # Ticket being triaged
    category:               TicketCategory  # hardware|software|network|security|access|database|performance|other
    priority:               TicketPriority  # P1|P2|P3|P4
    assigned_team:          AssignedTeam    # infrastructure|application_support|network_ops|security_ops|database_admin|helpdesk
    is_part_of_incident:    bool            # Incident linkage flag
    incident_id:            str | None      # e.g. "INC-MAJOR-01"
    resolution_steps:       list[str]|None  # Ordered remediation steps (P1 hard-task)
    escalate_to_management: bool            # Page senior management
```

---

## 👁️ Observation Space

```python
class Observation(BaseModel):
    task_id:          str            # Active task
    current_ticket:   Ticket | None  # Ticket to triage (None = queue empty)
    queue_remaining:  int            # Tickets still waiting
    processed_count:  int            # Tickets processed this episode
    step_number:      int
    action_feedback:  str | None     # Correctness feedback on previous action
    cumulative_score: float          # Running mean reward (0.0-1.0)
    episode_done:     bool
    active_incidents: list[str]      # Incident IDs declared so far
    hints:            list[str]      # Task-level guidance
```

---

## 🎯 Tasks

| Task ID | Difficulty | Tickets | Max Steps | Key Challenge |
|---|---|---|---|---|
| `basic_triage` | 🟢 Easy | 5 | 10 | Category + Priority + Routing |
| `priority_routing` | 🟡 Medium | 5 | 10 | Incident detection + Escalation |
| `incident_escalation` | 🔴 Hard | 7 | 15 | Cascading DB outage + Noise filtering + Remediation |

### Hard task: INC-MAJOR-01

The hard task simulates a **PostgreSQL WAL-corruption event** at 14:32. Five of seven tickets are incident symptoms (primary DB down, auth service failing, e-commerce checkout dead, analytics frozen, reporting job failed). Two tickets are unrelated noise (team lunch reminder, routine cert renewal). The agent must distinguish signal from noise, group the five linked tickets under `INC-MAJOR-01`, and provide specific remediation steps for each P1 ticket.

---

## 💰 Reward Function

Rewards are **dense** — computed per step (not just at episode end). All values are strictly bounded to `[0.0, 1.0]`.

### Weight profiles by difficulty

| Dimension | Easy | Medium | Hard |
|---|---|---|---|
| Category classification | 0.40 | 0.28 | 0.20 |
| Priority assignment | 0.35 | 0.22 | 0.18 |
| Team routing | 0.25 | 0.18 | 0.14 |
| Incident detection | — | 0.18 | 0.20 |
| Escalation decision | — | 0.14 | 0.12 |
| Resolution quality | — | — | 0.16 |

**Priority partial credit:** adjacent level (e.g., P2 when P1 expected) scores `0.5` instead of `0.0`, providing a learning gradient rather than a cliff.

**Resolution scoring:** Uses keyword-recall + step-level recall over domain-critical tokens, rewarding agents that cover the right remediation concepts even with paraphrased wording.

**Penalties:** Escalating a P4 cosmetic ticket to senior management incurs a -0.15 penalty.

---

## 🚀 Quick Start

### Local development

```bash
# Clone and set up
git clone https://huggingface.co/spaces/<your-username>/it-triage-env
cd it-triage-env
pip install -r requirements.txt

# Start the server
uvicorn app:app --host 0.0.0.0 --port 7860 --reload

# In a separate terminal — run the baseline agent
export OPENAI_API_KEY="sk-..."
export API_BASE_URL="http://localhost:7860"
export MODEL_NAME="gpt-4o"
python inference.py
```

### Docker

```bash
docker build -t it-triage-env .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY="sk-..." \
  -e MODEL_NAME="gpt-4o" \
  it-triage-env
```

### Interact manually with curl

```bash
# Reset to the hard task
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "incident_escalation"}'

# Submit a triage action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TKT-H001",
    "category": "database",
    "priority": "P1",
    "assigned_team": "database_admin",
    "is_part_of_incident": true,
    "incident_id": "INC-MAJOR-01",
    "escalate_to_management": true,
    "resolution_steps": [
      "Promote db-prod-replica-01 using pg_promote()",
      "Update all app DB_HOST configs to replica",
      "Preserve original primary for WAL forensics"
    ]
  }'
```

---

## 📊 Baseline Scores

| Task | Model | Score |
|---|---|---|
| `basic_triage` | GPT-4o | **0.87** |
| `priority_routing` | GPT-4o | **0.74** |
| `incident_escalation` | GPT-4o | **0.61** |
| **Overall** | GPT-4o | **0.74** |

---

## 🔌 API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check + task list |
| `POST` | `/reset` | Reset episode `{"task_id": "..."}` |
| `POST` | `/step` | Submit `TriageAction`, receive `StepResult` |
| `GET` | `/state` | Full `EnvironmentState` snapshot |
| `GET` | `/tasks` | All tasks with metadata |
| `GET` | `/docs` | Swagger UI (interactive) |
| `GET` | `/redoc` | ReDoc UI |

---

## 📦 File Structure

```
it-triage-env/
├── models.py         # Pydantic Action / Observation / State models
├── environment.py    # Core environment logic + reward engine + graders
├── app.py            # FastAPI server (OpenEnv REST interface)
├── client.py         # Typed HTTP client
├── inference.py      # Baseline LLM inference script
├── openenv.yaml      # OpenEnv specification file
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `API_BASE_URL` | inference only | `http://localhost:7860` | OpenEnv server URL |
| `MODEL_NAME` | inference only | `gpt-4o` | LLM model identifier |
| `OPENAI_API_KEY` | inference only | — | OpenAI / compatible API key |
| `HF_TOKEN` | HF deploy | — | Hugging Face token |
| `PORT` | optional | `7860` | Server port override |

---

## 🏅 Citation

```bibtex
@misc{it-helpdesk-triage-openenv,
  title  = {IT Helpdesk Triage & Incident Management — OpenEnv},
  year   = {2024},
  url    = {https://huggingface.co/spaces/<username>/it-triage-env}
}
```
