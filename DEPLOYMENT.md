# 🚀 Deployment Guide

## Quick Deploy Commands

### Local Development
```bash
# Start server
python src/app.py

# Test API
python tests/test_api.py
```

### Production (Heroku)
```bash
# Login
heroku login

# Create app
heroku create decoy-honeypot

# Set config
heroku config:set API_KEY=your-secret-key

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

### Production (Railway)
```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Set env
railway variables set API_KEY=your-secret-key
```

### Docker
```bash
# Build
docker build -t honeypot .

# Run
docker run -p 8080:8080 -e API_KEY=your-secret-key honeypot
```

## Environment Variables

```bash
export API_KEY="your-secret-api-key"
export GUVI_CALLBACK_URL="https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
export PORT=8080
```

## Testing Deployed API

```bash
# Health check
curl https://your-app.herokuapp.com/health

# Test with API key
curl -X POST https://your-app.herokuapp.com/api/message \
  -H "x-api-key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"Your account blocked","timestamp":"2026-01-21T10:15:30Z"},"conversationHistory":[]}'
```
