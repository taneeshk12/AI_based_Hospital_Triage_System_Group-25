# Installation & Setup Guide

This guide covers everything you need to install and run the OmniHealth Diagnostics system on both **macOS/Linux** and **Windows**.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| **Python** | 3.9 or higher | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 16 or higher | [nodejs.org](https://nodejs.org/) |
| **NPM** | 8 or higher | Comes bundled with Node.js |
| **Git** | Any recent version | For cloning the repo |

---

## Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd hcai_project
```

---

## Step 2 — Set Up Your API Key

Create a `.env` file in the `hcai_project/` root directory:

**Mac/Linux:**
```bash
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

**Windows (Command Prompt):**
```cmd
echo GROQ_API_KEY=your_groq_api_key_here > .env
```

**Windows (PowerShell):**
```powershell
"GROQ_API_KEY=your_groq_api_key_here" | Out-File -Encoding utf8 .env
```

> Get a free key at [console.groq.com](https://console.groq.com).

---

## Step 3 — Set Up the Python Virtual Environment

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (Command Prompt)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> **Windows PowerShell note:** If you get an "execution policy" error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Step 4 — Install Frontend Dependencies

```bash
cd ui
npm install
cd ..
```

This is the same on Mac, Linux, and Windows.

---

## Option A: Run the Entire System (Recommended)

### Mac / Linux

```bash
./START_SYSTEM.sh
```

> If you get a "permission denied" error, make the script executable first:
> ```bash
> chmod +x START_SYSTEM.sh
> ./START_SYSTEM.sh
> ```

### Windows

Windows does not run `.sh` scripts natively. Use **one of these options**:

**Option 1 — Git Bash** (recommended, comes with Git for Windows):
```bash
bash START_SYSTEM.sh
```

**Option 2 — WSL (Windows Subsystem for Linux):**
```bash
bash START_SYSTEM.sh
```

**Option 3 — Run components manually** (see Option B below).

---

Once the system starts, you will see:

```
==========================================================
🩺 OmniHealth Diagnostics: Multi-Agent Triage Dashboard
==========================================================
✅ Backend API is running in background (PID: XXXX)

🚀 System is launching!
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:5173

Press Ctrl+C to stop both servers.
```

Open **http://localhost:5173** in your browser.

---

## Option B: Manual Setup (Two Terminals)

Use this if you prefer running components separately, or if you are on Windows without Git Bash/WSL.

### Terminal 1 — Start the Backend

**Mac / Linux:**
```bash
source .venv/bin/activate
python3 api_server.py
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate
python api_server.py
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
python api_server.py
```

The backend will start at **http://localhost:8000**.

---

### Terminal 2 — Start the Frontend

```bash
cd ui
npm run dev
```

This is identical on Mac, Linux, and Windows.

The frontend will start at **http://localhost:5173**.

---

## Verifying the System is Running

Check the backend health endpoint:

**Mac / Linux:**
```bash
curl http://localhost:8000/health
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod http://localhost:8000/health
```

You should see a response like:
```json
{
  "status": "healthy",
  "agents": {
    "cardiac": true,
    "respiratory": true,
    "sepsis": true,
    "general": true
  }
}
```

---

## Stopping the System

- **If using `START_SYSTEM.sh`:** Press `Ctrl+C` in the terminal. Both backend and frontend will shut down automatically.
- **If running manually:** Press `Ctrl+C` in each terminal window.

---

## Rebuilding the RAG Knowledge Base Index

Only needed if you update `agents/Rag_Chatbot/knowledge_base_new.json`:

**Mac / Linux:**
```bash
source .venv/bin/activate
python agents/Rag_Chatbot/rag/build_index.py
```

**Windows:**
```cmd
.venv\Scripts\activate
python agents\Rag_Chatbot\rag\build_index.py
```

Then restart the backend.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `source: no such file or directory: venv/bin/activate` | Use `.venv` not `venv`: `source .venv/bin/activate` |
| `ModuleNotFoundError` | Make sure the venv is activated before running Python |
| Port 8000 or 5173 already in use | Kill the existing process: `lsof -ti:8000 \| xargs kill` (Mac/Linux) or `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` (Windows) |
| Frontend shows blank page | Run `cd ui && npm install` then restart |
| RAG chatbot returns "unavailable" | Install missing packages: `pip install faiss-cpu sentence-transformers` |
| PowerShell execution policy error | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
