# Installation & Setup Guide

This document contains everything you need to know to run the OmniHealth Diagnostics system.

## Prerequisites
- **Python** (v3.9 or higher)
- **Node.js** (v16 or higher) and **NPM** (v8 or higher)

The system is launched seamlessly using a single unified bash script, but you can also run the components manually.

## Option 1: Run the Entire System (Recommended)

You can launch both the Python Backend API and the React Frontend simultaneously using the startup script:

1. Open your terminal.
2. Navigate to the project root directory (`hcai_project`).
3. Run the startup script:
   ```bash
   ./START_SYSTEM.sh
   ```

This will automatically:
- Start the Flask backend on **`http://localhost:8000`** in the background.
- Start the Vite React frontend server on **`http://localhost:5173`**.
- Keep both running until you press `Ctrl+C`.

---

## Option 2: Manual Setup & Execution

If you prefer to start the components individually, follow these steps.

### Step 1: Start the Python Backend API
1. Navigate to the `hcai_project` directory:
   ```bash
   cd hcai_project
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python3 api_server.py
   ```
   The backend will launch at **`http://localhost:8000`**.

### Step 2: Start the React Frontend Dashboard
1. Open a new terminal window and navigate to the frontend directory:
   ```bash
   cd hcai_project/ui
   ```
2. Install npm dependencies (if this is your first time):
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm run dev
   ```
   The dashboard will automatically open in your browser at **`http://localhost:5173`**.
