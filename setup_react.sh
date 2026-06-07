#!/bin/bash

# React + Flask Setup Script for Respiratory Agent

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  RESPIRATORY AGENT - REACT + FLASK SETUP                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install Flask dependencies
echo -e "${BLUE}Step 1: Installing Flask dependencies...${NC}"
pip install flask flask-cors
echo -e "${GREEN}✓ Flask dependencies installed${NC}\n"

# Step 2: Create React project
echo -e "${BLUE}Step 2: Creating React project...${NC}"
cd /Users/taneeshkpatel/Desktop/OVGU_Projects

if [ -d "respiratory-ui" ]; then
    echo -e "${YELLOW}⚠ React project already exists. Skipping creation.${NC}"
else
    npx create-react-app respiratory-ui
fi

cd respiratory-ui

echo -e "${GREEN}✓ React project ready${NC}\n"

# Step 3: Install React dependencies
echo -e "${BLUE}Step 3: Installing React dependencies...${NC}"
npm install axios recharts
echo -e "${GREEN}✓ React dependencies installed${NC}\n"

# Step 4: Create .env file
echo -e "${BLUE}Step 4: Creating environment configuration...${NC}"
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:5000
EOF
echo -e "${GREEN}✓ Environment file created${NC}\n"

# Step 5: Create components directory
mkdir -p src/components

# Step 6: Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✓ SETUP COMPLETE - READY TO RUN                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}NEXT STEPS:${NC}"
echo ""
echo "1. In Terminal 1 (Backend):"
echo "   cd /Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training"
echo "   python api_server.py"
echo ""
echo "2. In Terminal 2 (Frontend):"
echo "   cd /Users/taneeshkpatel/Desktop/OVGU_Projects/respiratory-ui"
echo "   npm start"
echo ""
echo "3. Open Browser:"
echo "   http://localhost:3000"
echo ""
echo -e "${GREEN}Files created:${NC}"
echo "  - api_server.py (Flask backend)"
echo "  - respiratory-ui/ (React frontend)"
echo "  - REACT_SETUP_GUIDE.md (Complete documentation)"
echo ""
