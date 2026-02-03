# Production Deployment Guide

## MongoDB Setup (Free)

### Option 1: MongoDB Atlas (Recommended)
```bash
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster (M0 Free tier)
4. Get connection string:
   mongodb+srv://username:password@cluster.mongodb.net/honeypot_db
```

### Option 2: Local MongoDB
```bash
# Install
brew install mongodb-community

# Start
brew services start mongodb-community

# Connection string
mongodb://localhost:27017/
```

---

## Ollama Setup

### Local Development
```bash
# Install
brew install ollama

# Start service
ollama serve

# Download model
ollama pull llama3.2:1b

# Verify
curl http://localhost:11434/api/tags
```

### Production (Render)
```bash
# Ollama needs to run separately
# Use Ollama cloud API or self-hosted instance
```

---

## Render Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Production ready with MongoDB and ML"
git push origin main
```

### Step 2: Deploy on Render
```bash
1. Go to https://render.com
2. Sign up / Login
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Configure:
   - Name: honeypot-api
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn src.production_app:app
```

### Step 3: Set Environment Variables
```
API_KEY=your-secret-key-here
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/honeypot_db
OLLAMA_URL=http://your-ollama-instance:11434
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
PORT=10000
```

### Step 4: Deploy
```bash
Click "Create Web Service"
Wait for deployment (5-10 minutes)
```

---

## Testing Deployed API

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### Test Message
```bash
curl -X POST https://your-app.onrender.com/api/message \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked",
      "timestamp": "2026-01-21T10:15:30Z"
    },
    "conversationHistory": []
  }'
```

### Check Stats
```bash
curl https://your-app.onrender.com/stats
```

---

## Local Testing

### Start MongoDB
```bash
brew services start mongodb-community
```

### Start Ollama
```bash
ollama serve
```

### Start App
```bash
export MONGO_URI="mongodb://localhost:27017/"
export API_KEY="test-key"
python src/production_app.py
```

### Test
```bash
python tests/test_api.py
```

---

## Features

✅ ML-based scam detection (scikit-learn)
✅ Ollama AI for intelligent responses
✅ MongoDB for data persistence
✅ Intelligence extraction with advanced patterns
✅ GUVI integration
✅ API key authentication
✅ Production-ready error handling
✅ Logging and monitoring

---

## Architecture

```
Client Request
    ↓
API Key Auth
    ↓
ML Scam Detection (scikit-learn)
    ↓
Ollama AI Response Generation
    ↓
MongoDB Storage
    ↓
Intelligence Extraction
    ↓
GUVI Callback
```

---

## Monitoring

### Check Logs (Render)
```bash
Render Dashboard → Your Service → Logs
```

### MongoDB Data
```bash
# Connect to MongoDB
mongosh "mongodb+srv://cluster.mongodb.net/honeypot_db"

# View sessions
db.sessions.find()

# View intelligence
db.intelligence.find()
```

---

## Cost

- Render: Free tier (750 hours/month)
- MongoDB Atlas: Free tier (512MB)
- Ollama: Free (self-hosted)

Total: ₹0/month

---

## Troubleshooting

### Ollama Connection Failed
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### MongoDB Connection Failed
```bash
# Check connection string
# Whitelist IP in MongoDB Atlas
# Check username/password
```

### Deployment Failed
```bash
# Check Render logs
# Verify requirements.txt
# Check Python version
```
