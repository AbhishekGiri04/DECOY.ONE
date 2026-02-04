#!/bin/bash

# Start Script - Launch all services
# Usage: ./start.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=======================================================================${NC}"
echo -e "${BLUE}AGENTIC HONEYPOT - STARTUP SCRIPT${NC}"
echo -e "${BLUE}=======================================================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: ./setup.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}[1/4] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Check if Ollama is running
echo -e "${YELLOW}[2/4] Checking Ollama service...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}[WARN] Ollama not running. Starting Ollama...${NC}"
    
    # Start Ollama in background
    nohup ollama serve > logs/ollama.log 2>&1 &
    OLLAMA_PID=$!
    echo $OLLAMA_PID > logs/ollama.pid
    
    # Wait for Ollama to start
    echo -e "${YELLOW}Waiting for Ollama to start...${NC}"
    sleep 3
    
    # Check if model exists
    if ! ollama list | grep -q "llama3.2:1b"; then
        echo -e "${YELLOW}Downloading llama3.2:1b model (this may take a few minutes)...${NC}"
        ollama pull llama3.2:1b
    fi
    
    echo -e "${GREEN}[OK] Ollama started (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}[OK] Ollama already running${NC}"
fi
echo ""

# Check MongoDB connection
echo -e "${YELLOW}[3/4] Checking MongoDB connection...${NC}"
python3 -c "
from pymongo import MongoClient
import os
try:
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb+srv://SUser:XVI7Q07RWDPdDEgl@scamuser.mr9rdlw.mongodb.net/?appName=ScamUser'), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('[OK] MongoDB connected')
except Exception as e:
    print(f'[WARN] MongoDB connection failed: {e}')
    print('[WARN] System will run without MongoDB persistence')
"
echo ""

# Start Flask application
echo -e "${YELLOW}[4/4] Starting Flask application...${NC}"
echo ""
echo -e "${BLUE}=======================================================================${NC}"
echo -e "${GREEN}STARTING HONEYPOT SERVER${NC}"
echo -e "${BLUE}=======================================================================${NC}"
echo ""

# Start Flask app
python src/production_app.py

# Cleanup on exit
trap cleanup EXIT

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    
    # Kill Ollama if we started it
    if [ -f logs/ollama.pid ]; then
        OLLAMA_PID=$(cat logs/ollama.pid)
        if ps -p $OLLAMA_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping Ollama (PID: $OLLAMA_PID)...${NC}"
            kill $OLLAMA_PID 2>/dev/null || true
            rm logs/ollama.pid
        fi
    fi
    
    echo -e "${GREEN}[OK] Cleanup complete${NC}"
}
