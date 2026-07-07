# 🧠 MeetingMind AI — Meeting Productivity Analyzer

> An AI-powered system that analyzes meeting notes, extracts action items, scores meeting effectiveness, and detects recurring issues — built for enterprise technology teams.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)
![NLP](https://img.shields.io/badge/NLP-NLTK-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📌 Project Overview

Companies like **Microsoft, WSO2, and IFS** run hundreds of internal meetings every week. Research shows that up to **50% of meeting time is unproductive** — action items go untracked, decisions are forgotten, and teams repeatedly discuss the same unresolved problems.

**MeetingMind AI** solves this by:

- 🔍 **Automatically extracting** action items, owners, and deadlines from raw meeting notes
- 📊 **Scoring** each meeting from 0–100 based on a defined effectiveness model
- ⚠️ **Detecting recurring issues** that appear across multiple meetings
- 📈 **Visualizing** team productivity trends through an interactive React dashboard

This project was built as a **full Business Analysis + AI development portfolio project**, demonstrating skills directly relevant to **Business Analyst** and **Project Manager** internship roles.

---

## 🎯 Problem Statement

| Pain Point | Impact |
|---|---|
| Action items recorded manually or not at all | Missed follow-ups, zero accountability |
| No way to measure meeting quality | No data to improve meeting culture |
| Same topics discussed in multiple meetings | Wasted time, unresolved root causes |
| Post-meeting summaries take 30–60 minutes | Reduced productive work time |

---

## ✅ Solution Architecture

```
Meeting Notes (text)
        │
        ▼
┌─────────────────────┐
│   NLP Engine        │  ← Python + NLTK
│   action_extractor  │  → Extracts tasks, owners, deadlines
│   scorer            │  → Calculates 0-100 effectiveness score
│   pattern_detector  │  → Flags recurring issues
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   Flask REST API    │  ← 13 endpoints
│   /auth             │  → JWT authentication
│   /meetings         │  → Analyze, save, retrieve
│   /analytics        │  → Dashboard stats, trends
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   React Dashboard   │  ← Recharts + Tailwind
│   Dashboard screen  │  → Score trends, recent meetings
│   Analyze screen    │  → Live NLP analysis
│   Meetings screen   │  → Full history
│   Analytics screen  │  → Charts and insights
└─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| NLP Engine | Python 3.12, NLTK | Action extraction, scoring, pattern detection |
| Backend API | Flask 3.1, PyJWT, bcrypt | REST API, authentication |
| Database | MongoDB (in-memory fallback) | Meeting storage, user management |
| Frontend | React 18, Recharts | Interactive dashboard |
| BA Documentation | Word, draw.io | AS-IS/TO-BE, requirements, stakeholder analysis |

---

## 📂 Project Structure

```
meetingmind/
│
├── nlp/                        # NLP Engine (Phase 2)
│   ├── action_extractor.py     # Extracts action items, owners, deadlines
│   ├── scorer.py               # Meeting effectiveness score (0-100)
│   ├── pattern_detector.py     # Recurring issue detection
│   └── analyzer.py             # Main pipeline combining all 3 modules
│
├── api/                        # Flask Backend (Phase 3)
│   ├── routes/
│   │   ├── auth.py             # Register, login, JWT
│   │   ├── meetings.py         # Analyze, save, retrieve meetings
│   │   └── analytics.py        # Dashboard stats, trends, action stats
│   ├── middleware/
│   │   └── auth.py             # JWT decorator
│   ├── database.py             # MongoDB + in-memory fallback
│   └── config.py               # App configuration
│
├── frontend/                   # React Dashboard (Phase 4)
│   └── MeetingMind_Dashboard.jsx
│
├── tests/                      # Test suites
│   ├── test_nlp.py             # 5 NLP tests (all passing ✅)
│   └── test_api.py             # 13 API tests (all passing ✅)
│
├── docs/                       # BA Documentation (Phase 1)
│   ├── MeetingMind_BA_Phase1.docx
│   └── BPMN_Diagrams/
│
├── run.py                      # App entry point
└── requirements.txt
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/meetingmind-ai.git
cd meetingmind-ai
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the backend API
```bash
python run.py
# API running at http://localhost:5000
# Health check: http://localhost:5000/api/health
```

### 4. Run the frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

### 5. Run the test suites
```bash
# NLP tests
python tests/test_nlp.py

# API tests
python tests/test_api.py
```

---

## 📊 Meeting Effectiveness Score Model

The scoring algorithm is defined in the BA document (Phase 1, Section 5.2):

| Criterion | Weight | How it is measured |
|---|---|---|
| Action items with named owners | 30 pts | NLP detects assignment phrases |
| Decisions documented | 25 pts | Keywords: decided, agreed, confirmed |
| Deadlines assigned to tasks | 20 pts | Date/time entities in action items |
| Clear agenda present | 15 pts | Agenda keywords at start of notes |
| No recurring unresolved issues | 10 pts | Cross-referenced against history |
| **Total** | **100 pts** | |

**Grade bands:** Excellent (80–100) · Good (60–79) · Fair (40–59) · Poor (0–39)

---

## 🔌 API Reference

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/health` | Health check | No |
| POST | `/api/auth/register` | Create account | No |
| POST | `/api/auth/login` | Login → JWT token | No |
| GET | `/api/auth/me` | Get current user | ✅ |
| POST | `/api/meetings/analyze` | Analyze meeting notes | ✅ |
| POST | `/api/meetings/save` | Save analyzed meeting | ✅ |
| GET | `/api/meetings` | List all meetings | ✅ |
| GET | `/api/meetings/<id>` | Get single meeting | ✅ |
| PUT | `/api/meetings/<id>/action/<i>` | Mark action complete | ✅ |
| DELETE | `/api/meetings/<id>` | Delete meeting | ✅ |
| GET | `/api/analytics/dashboard` | Summary stats | ✅ |
| GET | `/api/analytics/trend` | Score trend over time | ✅ |
| GET | `/api/analytics/action-stats` | Action item breakdown | ✅ |

---

## 📋 Business Analysis Documentation

This project includes a complete **Phase 1 BA document** covering:

- ✅ Executive Summary with before/after comparison
- ✅ Project Charter (objectives, scope, timeline)
- ✅ Stakeholder Analysis (6 stakeholder groups)
- ✅ AS-IS Process Analysis (current manual workflow)
- ✅ TO-BE Process Design (AI-optimised workflow)
- ✅ Gap Analysis (6 capability gaps with solutions)
- ✅ Functional Requirements (8 requirements)
- ✅ Non-Functional Requirements (6 requirements)
- ✅ Risk Analysis (5 risks with mitigation plans)
- ✅ User Stories with Acceptance Criteria
- ✅ KPIs and Success Metrics
- ✅ AS-IS and TO-BE BPMN Diagrams

---

## 🧪 Test Results

```
🧠 MeetingMind AI — NLP Engine Test Suite
==========================================
✅ Test 1: Action Item Extraction — PASSED
✅ Test 2: Meeting Effectiveness Scoring — PASSED
✅ Test 3: Recurring Issue Detection — PASSED
✅ Test 4: Full Analysis Pipeline — PASSED
✅ Test 5: Edge Cases — PASSED

🧠 MeetingMind AI — API Test Suite
==========================================
✅ Test 1:  Health Check — PASSED
✅ Test 2:  Auth Register — PASSED
✅ Test 3:  Auth Login — PASSED
✅ Test 4:  Auth Get Profile — PASSED
✅ Test 5:  Meetings Analyze — PASSED
✅ Test 6:  Meetings Save — PASSED
✅ Test 7:  Meetings Get All — PASSED
✅ Test 8:  Meetings Get Single — PASSED
✅ Test 9:  Action Item Update — PASSED
✅ Test 10: Analytics Dashboard — PASSED
✅ Test 11: Analytics Trend — PASSED
✅ Test 12: Analytics Action Stats — PASSED
✅ Test 13: Meetings Delete — PASSED

ALL 18 TESTS PASSED ✅
```

---

## 💡 Skills Demonstrated

**Business Analysis**
- AS-IS / TO-BE process modeling
- Stakeholder analysis and management
- Functional and non-functional requirements gathering
- User story writing with acceptance criteria
- Gap analysis and risk assessment
- KPI definition and success measurement
- BPMN workflow diagramming

**Technical Development**
- Python NLP with NLTK (rule-based text analysis)
- REST API development with Flask
- JWT authentication and bcrypt password hashing
- React component architecture with hooks
- Data visualization with Recharts
- End-to-end test suite design

---

## 🏢 Target Industry

This project is designed to demonstrate value for technology companies including **Microsoft**, **WSO2**, and **IFS** — all of which operate large engineering teams with significant internal meeting overhead.

---

## 👤 Author

**Dinu Sathsarani Ranasingha**
Information Systems Engineering — SLIIT
📧 [Your Email]
💼 [LinkedIn Profile]
🐙 [GitHub Profile]

---

## 📄 License

MIT License — free to use and modify with attribution.
