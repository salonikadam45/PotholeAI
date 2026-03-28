# 🛣️ PotholeAI — Multi-Agent Complaint Management System

An AI-powered, multi-agent system for managing citizen pothole complaints end-to-end. Built with **Python/FastAPI** backend and **React/Vite** premium dashboard.

## 🏗️ Architecture

```
Citizen Input (Text/Image/Audio)
        │
        ▼
┌──────────────────┐
│  Agent 1: Intake  │ ──→ Parse & normalize multimodal input
│    & Parser       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 2: Vision   │ ──→ Analyze images for damage classification
│  & Multimodal AI  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 3: Severity │ ──→ Score severity 1-10 (weighted formula)
│   Classifier      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 4: Router   │ ──→ Route to correct department, set SLA
│  & Decision Maker │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 5: Workflow  │ ──→ Monitor SLA, detect stalls, escalate
│  Monitor & SLA     │
└──────────────────┘
```

## 🚀 Quick Start

### 1. Start Backend (FastAPI)
```bash
cd "agentic ai"
pip install fastapi uvicorn pydantic
py -m uvicorn backend.main:app --port 8001
```

### 2. Start Frontend (React)
```bash
cd "agentic ai/dashboard"
npm install
npm run dev
```

### 3. Seed Demo Data
Click **"⚡ Seed Demo Data"** button in the dashboard, or:
```bash
curl -X POST http://localhost:8001/api/demo/seed?count=20
```

Dashboard opens at **http://localhost:5173/**

## 📊 Dashboard Views

| Tab | Description |
|-----|-------------|
| **Overview** | KPI metrics, status distribution, department load, agent pipeline |
| **Agent Pipeline** | Visual 5-node agent flow with processing counts and self-correction indicators |
| **Complaints Feed** | Filterable/searchable table with severity badges, SLA status |
| **SLA Tracker** | Breached, stalled, and approaching-deadline complaints |
| **Departments** | Per-department workload cards, completion rates, summary table |
| **Audit Trail** | Timeline of every agent decision with expandable reasoning |
| **Notifications** | Citizen notification log with delivery status |
| **New Complaint** | Submit form with text, image upload, and audio recording |

## 🤖 Agent Details

### Agent 1: Intake & Parser
- Accepts text, images, and audio
- Extracts location via regex patterns
- Classifies complaint type (pothole, crack, sinkhole, etc.)
- Identifies urgency keywords

### Agent 2: Vision & Multimodal AI
- Damage classification (pothole, crack, sinkhole, flooding, manhole)
- Area estimation (small/medium/large)
- Hazard detection (school zone, high traffic, etc.)
- Self-correction: flags low-confidence results for human review

### Agent 3: Severity Classifier
- Weighted formula: `0.3×text + 0.4×vision + 0.2×location + 0.1×recurrence`
- Cross-validates text vs vision scores
- Self-correction: if mismatch >3 points, triggers Agent 2 re-analysis

### Agent 4: Router & Decision Maker
- Routes to 5 departments based on multi-signal decision tree
- Sets SLA deadlines (Critical: 24h, High: 48h, Medium: 7d, Low: 14d)
- Full decision auditability

### Agent 5: Workflow Monitor & SLA Tracker
- SLA breach detection
- Stall detection at 50% SLA window
- Auto-reroute at 25% SLA window
- Escalation ladder: Supervisor → Dept Head → City Admin
- Citizen notifications at key milestones

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/complaints` | GET/POST | List or submit complaints |
| `/api/complaints/{id}` | GET | Complaint detail |
| `/api/complaints/{id}/audit` | GET | Audit trail |
| `/api/complaints/{id}/resolve` | POST | Mark resolved |
| `/api/pipeline/status` | GET | Pipeline health metrics |
| `/api/departments` | GET | Department stats |
| `/api/sla/breaches` | GET | SLA breaches |
| `/api/audit` | GET | Audit log |
| `/api/notifications` | GET | Notification log |
| `/api/demo/seed` | POST | Seed demo data |

## 🧠 Key Features

- **Process Orchestration**: Master controller chains agents with retry logic
- **Self-Correction**: Agents detect inconsistencies and trigger re-analysis
- **Error Recovery**: 3-retry loop with failure escalation
- **Audit Trail**: Append-only log of every decision with reasoning
- **SLA Tracking**: Real-time compliance with escalation ladder
- **Citizen Notifications**: Automated updates at key milestones
- **100% Autonomous Success Rate**: All processing without human involvement

## 📁 Project Structure

```
agentic ai/
├── backend/
│   ├── main.py                    # FastAPI app (14 REST endpoints)
│   ├── models.py                  # 15+ Pydantic data models
│   ├── orchestrator.py            # Process orchestration agent
│   ├── requirements.txt
│   ├── agents/
│   │   ├── agent1_intake.py       # Multimodal intake parser
│   │   ├── agent2_vision.py       # Vision & damage classification
│   │   ├── agent3_severity.py     # Weighted severity scorer
│   │   ├── agent4_router.py       # Department routing engine
│   │   └── agent5_monitor.py      # SLA monitor & escalation
│   └── services/
│       ├── audit_logger.py        # Append-only audit trail
│       ├── sla_engine.py          # SLA compliance engine
│       └── notification_service.py # Citizen notifications
│
├── dashboard/                     # React + Vite frontend
│   └── src/
│       ├── App.jsx                # Main app (8 views)
│       ├── index.css              # Design system
│       ├── components/            # 10 React components
│       └── hooks/useApi.js        # API integration
│
├── ARCHITECTURE.md                # Architecture document
├── IMPACT_MODEL.md                # Business impact analysis
└── README.md                      # This file
```

## 📄 Submission Documents

| Document | File | Description |
|----------|------|-------------|
| **Architecture Document** | [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Agent roles, communication flow, error handling, tool integrations |
| **Impact Model** | [`IMPACT_MODEL.md`](./IMPACT_MODEL.md) | Quantified cost savings (₹2.4 Cr/yr), time saved, revenue recovery |
| **Source Code** | This repository | Full backend + frontend with setup instructions |
| **Pitch Video** | See `pitch_video/` or linked | 3-min walkthrough of agent workflow |

## 📜 License

This project was built as an academic submission for the Multi-Agent AI course.

