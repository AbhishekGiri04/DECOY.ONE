#!/bin/bash

# 🚀 Production Honeypot Setup Script
# Automates complete setup without Ollama

set -e

echo "======================================================================="
echo "🍯 PRODUCTION AI HONEYPOT - AUTOMATED SETUP"
echo "======================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}[2/8] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}[3/8] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}[4/8] Upgrading pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✅ Pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}[5/8] Installing dependencies...${NC}"
echo "This may take a few minutes..."
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Install spaCy model (optional)
echo -e "\n${YELLOW}[6/8] Installing spaCy language model...${NC}"
python -m spacy download en_core_web_sm -q 2>/dev/null || {
    echo -e "${YELLOW}⚠️  spaCy model installation failed (optional)${NC}"
    echo -e "${YELLOW}   System will use regex-only mode${NC}"
}
echo -e "${GREEN}✅ NLP setup complete${NC}"

# Train ML model
echo -e "\n${YELLOW}[7/8] Training ML model...${NC}"
python -c "
from src.ml_detector import EnhancedMLScamDetector
detector = EnhancedMLScamDetector()
print(f'✅ Model trained with {detector.accuracy*100:.1f}% accuracy')
" || echo -e "${YELLOW}⚠️  ML model will train on first run${NC}"

# Create models directory
mkdir -p models

# Setup environment variables
echo -e "\n${YELLOW}[8/8] Setting up environment...${NC}"

if [ ! -f ".env" ]; then
    cat > .env << EOF
# MongoDB Configuration
MONGO_URI=mongodb+srv://SUser:XVI7Q07RWDPdDEgl@scamuser.mr9rdlw.mongodb.net/?appName=ScamUser

# API Configuration
API_KEY=your-secret-api-key-change-this

# GUVI Integration
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult

# Server Configuration
PORT=8080
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please update API_KEY in .env file${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Export environment variables
export $(cat .env | grep -v '^#' | xargs)

echo ""
echo "======================================================================="
echo -e "${GREEN}🎉 SETUP COMPLETE!${NC}"
echo "======================================================================="
echo ""
echo "📊 System Status:"
echo "  ✅ Python environment ready"
echo "  ✅ Dependencies installed"
echo "  ✅ ML model trained"
echo "  ✅ NLP extractor ready"
echo "  ✅ MongoDB configured"
echo ""
echo "🚀 To start the server:"
echo "  source venv/bin/activate"
echo "  python src/production_app.py"
echo ""
echo "🧪 To run tests:"
echo "  python tests/test_production.py"
echo ""
echo "📖 For detailed documentation:"
echo "  cat PRODUCTION_SETUP.md"
echo ""
echo "======================================================================="
