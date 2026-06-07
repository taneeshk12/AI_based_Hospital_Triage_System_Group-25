#!/bin/bash

# 🫁 Respiratory Agent - Complete Startup Script
# This script starts both the backend API and frontend UI

echo ""
echo "=========================================="
echo "🫁 Respiratory Agent System"
echo "=========================================="
echo ""

# Check if backend is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is already running on http://localhost:8000"
    BACKEND_RUNNING=true
else
    echo "❌ Backend API is not running"
    BACKEND_RUNNING=false
fi

echo ""
echo "To start the complete system:"
echo ""
echo "1️⃣  If not running, start the backend in a NEW terminal:"
echo "   cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training"
echo "   source .venv/bin/activate"
echo "   python api_server.py"
echo ""
echo "2️⃣  Start the React frontend in THIS or ANOTHER terminal:"
echo "   cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui"
echo "   npm start"
echo ""
echo "Then open your browser to: http://localhost:3000"
echo ""
echo "=========================================="
echo "API Endpoints:"
echo "=========================================="
echo "GET  http://localhost:8000/health              - Health check"
echo "POST http://localhost:8000/predict             - Single prediction"
echo "POST http://localhost:8000/batch               - Batch predictions"
echo "GET  http://localhost:8000/model-info          - Model metadata"
echo "GET  http://localhost:8000/example-patients    - Example patients"
echo ""
echo "=========================================="
echo ""

if [ "$BACKEND_RUNNING" = true ]; then
    echo "Backend Status: ✅ RUNNING"
    echo ""
    echo "You can now start the frontend:"
    echo "cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui && npm start"
else
    echo "Backend Status: ⏸️  NOT RUNNING"
fi

echo ""
