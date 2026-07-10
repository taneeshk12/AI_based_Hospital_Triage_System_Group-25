# 🩺 OmniHealth Diagnostics — Multi-Agent Clinical Triage System

> A production-ready clinical decision support dashboard powered by a multi-agent ML pipeline, RAG-based symptom chatbot, and a human-in-the-loop safety layer.

---

## 📐 System Architecture

```
┌────────────────────────────────────────────┐
│         Patient Triage Intake Form         │
│     (Vitals · Labs · Medical History)      │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          Rule-Based Safety Layer           │
│  (flags critical vitals before ML runs)   │
└──────┬──────────┬────────────┬─────────────┘
       │          │            │            │
       ▼          ▼            ▼            ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
 │Respiratory│ │ Cardiac  │ │  Sepsis  │ │ General  │
 │ Sub-Agent │ │ Sub-Agent│ │ Sub-Agent│ │ Sub-Agent│
 │  (RF+DNN) │ │(XGBoost) │ │(XGBoost) │ │(XGBoost) │
 └─────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
       └────────────┴────────────┴─────────────┘
                         │
                         ▼
       ┌────────────────────────────────────┐
       │     Output Aggregator & Fusion     │
       │  (confidence · SHAP · ESI score)  │
       └──────────────────┬─────────────────┘
                          │
                          ▼
       ┌────────────────────────────────────┐
       │    Clinical Telemetry Dashboard    │
       │       React + Vite Frontend        │
       └──────────────────┬─────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
 ┌────────────────────┐   ┌────────────────────┐
 │  Attestation &     │   │  RAG Symptom       │
 │  Feedback Log      │   │  Chatbot (FAISS +  │
 │  (feedback_log)    │   │  Groq LLaMA 3.3)   │
 └────────────────────┘   └────────────────────┘
```

---

## 📁 Project Structure

```
hcai_project/
│
├── api_server.py                      # Main Flask backend — all API endpoints
│
├── START_SYSTEM.sh                    # Unified one-command startup (Mac/Linux)
├── requirements.txt                   # Python dependencies
├── .env                               # API keys (not committed to git)
├── README.md                          # This file
├── setup.md                           # Detailed installation guide
│
├── agents/                            # All AI agent modules
│   ├── cardiac_agent_api.py           # Cardiac XGBoost ML agent
│   ├── sepsis_agent_api.py            # Sepsis XGBoost ML agent
│   ├── respiratory_agent_api.py       # Respiratory RF ensemble ML agent
│   ├── general_agent_api_xgboost.py   # General triage XGBoost ML agent
│   ├── confidence_agent.py            # Prediction confidence scoring
│   ├── llm_agent.py                   # Groq LLM narrative generation
│   ├── safety_agent.py                # Rule-based safety checks
│   ├── summary_agent.py               # Patient summary reports
│   ├── symptom_agent.py               # Free-text symptom processor
│   ├── trust_agent.py                 # Human-in-the-loop trust scoring
│   └── Rag_Chatbot/                   # RAG symptom chatbot
│       ├── knowledge_base_new.json    # Active medical knowledge base (~189KB)
│       ├── vector_store/              # FAISS index + metadata (pre-built)
│       └── rag/                       # RAG engine
│           ├── retrieval.py           # FAISS semantic search
│           ├── llm_agent.py           # Groq LLM response generation
│           ├── prompts.py             # Prompt templates
│           └── build_index.py        # One-time index builder (run if KB changes)
│
├── models/                            # Trained ML model weights
│   ├── xgboost_cardiac_model.pkl
│   ├── sepsis_xgb_model.pkl
│   ├── general_xgb_model.joblib
│   ├── respiratory_rf_pipeline.joblib
│   ├── respiratory_rf_ensemble.joblib
│   ├── respiratory_classifier.joblib
│   └── respiratory_preprocessor.joblib
│
├── data/                              # Runtime data files
│   ├── triage_registry.db             # SQLite patient triage database
│   ├── data_engineered.csv            # Training dataset
│   ├── safety_audit_log.csv           # Safety event log
│   ├── feedback_log.csv               # Clinician feedback log
│   └── example_patient_*.json         # API test payloads
│
├── ui/                                # React frontend (Vite)
│   ├── src/                           # React source code
│   ├── dist/                          # Production build output
│   ├── package.json
│   └── vite.config.js
│
├── notebooks/                         # Jupyter notebooks
│   ├── HCAI_MULTIMODAL.ipynb          # Multimodal research notebook
│   ├── respiratory_agent_training.ipynb
│   └── 01_respiratory_research_complete.ipynb
│
├── scripts/                           # Utility & training scripts
│   └── retrain_general_model.py       # Retrain the general XGBoost model
│
├── tests/                             # API & integration tests
│   └── test_api.py                    # Smoke test for /unified/predict
│
├── reports/                           # Report generation module
├── evaluation/                        # Safety metrics scripts
├── research/                          # Research notes and README
└── outputs/                           # Training charts and CSVs
```

---

## 🤖 ML Models

| Agent | Algorithm | Task |
|---|---|---|
| **Respiratory** | Random Forest Ensemble + Classifier | Respiratory distress risk + uncertainty |
| **Cardiac** | XGBoost (5-class) | ESI cardiac risk classification |
| **Sepsis** | XGBoost | Sepsis probability scoring |
| **General** | XGBoost | Undifferentiated triage risk |

All models load automatically when the backend starts.

---

## 💬 RAG Symptom Chatbot

The chatbot uses **FAISS** for semantic retrieval over a curated medical knowledge base (`knowledge_base_new.json`, ~189KB) and **Groq's LLaMA 3.3-70B** for response generation.

- **Endpoint**: `POST /rag/chat`
- **Input**: `{ "patient_info": "65yo male, chest pain, diaphoresis, SpO2 94%" }`
- **Output**: Clinical narrative + top-5 source documents

> If you update the knowledge base, re-run `agents/Rag_Chatbot/rag/build_index.py` to rebuild the FAISS index.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health + model status |
| `POST` | `/unified/predict` | Multi-agent triage prediction |
| `POST` | `/rag/chat` | RAG symptom chatbot |
| `POST` | `/feedback` | Submit clinician override/feedback |
| `GET` | `/registry` | List all triage records |
| `GET` | `/registry/<id>` | Fetch single patient record |
| `GET` | `/safety/audit` | Safety audit log |

### Example: `/unified/predict`

```json
{
  "age": 65,
  "sex": "M",
  "chest_pain": 1,
  "spo2": 94,
  "respiratory_rate": 22,
  "temperature": 37.2,
  "heart_rate": 105,
  "systolic_bp": 95,
  "diastolic_bp": 60,
  "wbc": 14.0,
  "hemoglobin": 12.5,
  "platelet_count": 180,
  "sodium": 138,
  "potassium": 4.2,
  "creatinine": 1.4,
  "glucose": 140,
  "troponin": 0.08,
  "bnp": 320,
  "lactate": 2.8,
  "inr": 1.3,
  "altered_mentation": 0,
  "diabetes": 1
}
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

---

## 🚀 Quick Start

See **[setup.md](./setup.md)** for full installation instructions for Mac and Windows.

**TL;DR (Mac/Linux):**
```bash
cd hcai_project
./START_SYSTEM.sh
```
Then open **http://localhost:5173** in your browser.

---

## ⚙️ Clinical Auto-Calculations

The system automatically computes several derived features — you do **not** enter these manually:

| Feature | How it's computed |
|---|---|
| **Pain Score** | Real-time formula from tachycardia, hypoxia, BP deviation, and temperature flags |
| **Age Group** | `pediatric / adult / senior / elderly` derived from numeric age |
| **SHAP Values** | Computed natively on every inference via XGBoost `pred_contribs=True` |

---

## 📓 Notebooks

| Notebook | Purpose |
|---|---|
| `HCAI_MULTIMODAL.ipynb` | Multimodal data exploration and model experiments |
| `respiratory_agent_training.ipynb` | Training pipeline for the respiratory agent |
| `01_respiratory_research_complete.ipynb` | Full respiratory research analysis |

---

## 👥 Human-in-the-Loop

Clinicians can **accept** or **override** any AI triage decision through the dashboard. All decisions — both AI-generated and clinician-modified — are logged to:
- `data/feedback_log.csv` — override history
- `data/safety_audit_log.csv` — safety rule triggers
- `data/triage_registry.db` — full patient record store
