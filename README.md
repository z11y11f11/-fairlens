# FairLens AI Audit System

**AI Bias Accountability Platform for Financial Institutions**

> Built with IBM Bob IDE | IBM AI Fairness 360 | EU AI Act Compliant

---

## What is FairLens?

FairLens helps financial institutions systematically detect discrimination risks in AI-powered credit decision models. Generate standardized audit reports that demonstrate compliance with EU AI Act before its mandatory enforcement in August 2026.

## Who is it for?

- **Chief Compliance Officers** — Monitor bias alerts, generate regulatory reports
- **AI & Model Risk Teams** — Analyze fairness metrics, track trends
- **Regulators & Auditors** — Review compliance status, access audit reports

---

## Features

- 🚨 **Alert Center** — Real-time bias alerts from connected institutional systems
- 📊 **Dashboard** — Historical DI trend analysis (Monthly/Quarterly/Yearly)
- 📋 **Audit** — Upload CSV/Excel or manual input → instant PDF report
- ⚖️ **Regulations** — EU AI Act, ECOA, GDPR compliance cross-reference

---

## System Architecture

### Production Mode (Full Integration)
Alert Center and Dashboard connect to institutional data via API:
- Bank core system pushes loan decision data periodically
- Automatic DI calculation on new data batches
- Real-time alerts when DI drops below threshold
- Monthly/Quarterly/Annual reports generated automatically
- Annual ESG reporting integration

### Demo Mode (This Hackathon)
- **Alert Center (Page 1)**: Simulated data showing real-time bias detection alerts
- **Dashboard (Page 2)**: Simulated 12-month DI trend data across gender, ethnicity, zip code
- **Audit (Page 3)**: Fully functional — upload CSV/Excel or manual input → real DI calculation → PDF report
- **Regulations (Page 4)**: Static compliance reference with live audit result cross-reference

> Page 3 (Audit) demonstrates the complete working pipeline end-to-end.
> Pages 1, 2, 4 show the production integration vision when connected to institutional data systems.

---

## Core Methodology

- **Disparate Impact (4/5 Rule)**: DI = min_rate / max_rate across all groups
  - DI < 0.8 → 🔴 VIOLATION
  - DI 0.8–0.9 → 🟡 WARNING
  - DI > 0.9 → 🟢 COMPLIANT
- **Multi-group analysis**: Gender, Ethnicity (5+ groups), Zip Code (10 areas)
- **Powered by**: IBM AI Fairness 360 methodology

---

## Demo Scenario

**City Commercial Bank** uses an XGBoost model for personal loan approval,
trained on historical data from 2015–2020.

FairLens audit detected:
- 🔴 **Gender DI = 0.362** — Female approval rate (11.4%) vs Male (31.4%)
  → Severe violation of 4/5 Rule, below 0.8 threshold
  → Violates ECOA and EU AI Act Article 6
- 🟡 **Zip Code** — Detected as proxy variable for race/ethnicity
- 🔴 **Age** — Protected attribute directly used in model

**Validation data**: UCI Adult Dataset (30,162 records, 1994 US Census)
Used as public benchmark to demonstrate bias detection capability.
In production, real institutional data is uploaded via CSV/Excel.

---

## Regulatory Framework

| Regulation | Region | Requirement |
|-----------|--------|-------------|
| EU AI Act Article 6 | EU | High-risk AI mandatory audit |
| ECOA | US | Equal credit opportunity |
| GDPR Article 5 | EU | Data minimization |
| FCRA | US | Fair credit reporting |
| IBM AIF360 | Global | Fairness metrics standard |

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000

---

## Sample Data

Ready-to-use test datasets in `sample_data/`:
- `sample_bank_data.csv` / `.xlsx`
- `sample_bank_data-1.csv` / `.xlsx`
- `sample_bank_data-2.csv` / `.xlsx`

Required columns: `gender`, `ethnicity`, `zip_code`, `loan_approved`

Upload directly in the Audit page (Page 3) to generate a real report.

---

## Project Structure

```
fairlens/
├── backend/
│   ├── app.py                  # Flask API
│   ├── audit/
│   │   ├── bias_detector.py    # DI calculation engine
│   │   ├── report_generator.py # PDF report generation
│   │   └── accountability.py   # RACI matrix
│   └── templates/
│       └── loan_approval.py    # Audit template
├── frontend/
│   └── src/
│       ├── Overview.jsx        # Product overview
│       ├── AlertCenter.jsx     # Bias alerts
│       ├── Dashboard.jsx       # Trend analysis
│       ├── AuditForm.jsx       # Data input & report
│       └── Regulations.jsx     # Compliance reference
├── sample_data/                # Test datasets
├── bob_sessions/               # IBM Bob IDE task records
└── README.md
```

---

## IBM Bob Dev Day Hackathon 2026

**Theme: Turn Idea Into Impact Faster**

FairLens demonstrates how IBM Bob IDE accelerates development
from idea to working product. What would traditionally take
weeks of engineering work was completed in under 24 hours:

- Bob understood our business intent and planned the architecture
- Bob wrote core algorithms, frontend components, and PDF generation
- Bob autonomously debugged complex cross-file issues
- Human judgment directed Bob's implementation at every step

The result: a fully functional AI bias audit platform, complete
with real data analysis, professional PDF reports, and a
4-page compliance dashboard — built in one hackathon session.

Bob task session reports available in `bob_sessions/`.

---

*FairLens v4 | IBM Bob Dev Day Hackathon 2026*
