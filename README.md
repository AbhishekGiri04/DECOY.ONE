# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

🍯 **An AI-powered honeypot system that detects scam intent and autonomously engages scammers to extract useful intelligence without revealing detection.**

## 🔥 Core Concept

This system acts as a **fake user (honeypot)** that:
- 🎯 **Detects scam messages** using advanced pattern matching
- 🤖 **Engages scammers** with human-like responses
- 🕵️ **Extracts intelligence** (UPI IDs, phone numbers, links, etc.)
- 📊 **Reports findings** to GUVI evaluation endpoint
- 🛡️ **Protects real users** by wasting scammers' time

## 🧠 Real-Life Example

```
🔴 Scammer: "Your bank account will be blocked. Verify now."
🤖 Agent: "Blocked? But I haven't done anything wrong..."

🔴 Scammer: "Share your UPI ID to avoid suspension."
🤖 Agent: "I'm nervous about sharing that. How do I know you're legitimate?"

🔴 Scammer: "Transfer ₹1 to 9876543210@paytm for verification."
🤖 Agent: "Okay, but I'm scared. What happens if something goes wrong?"

📊 System extracts: UPI ID, phone number, scam keywords
📤 Sends final intelligence report to GUVI
```

## 🚀 Quick Start

### Method 1: Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Method 2: Using Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Method 3: Deployment Script
```bash
# Make executable and run
chmod +x deploy.sh
./deploy.sh
```

## 🧪 Testing

```bash
# Basic functionality test
python test_honeypot.py

# Comprehensive scam simulation
python comprehensive_test.py
```

## 📡 API Endpoints

### POST /api/message
**Main endpoint for processing incoming messages**

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh no! Why is my account being blocked? I haven't done anything wrong. What should I do?"
}
```

### GET /health
**Health check endpoint**

### GET /stats
**System statistics**

## 🧩 System Flow

```
1️⃣ Message arrives → 2️⃣ Scam detection → 3️⃣ Agent activation
                                                      ↓
7️⃣ GUVI callback ← 6️⃣ End conversation ← 5️⃣ Intelligence extraction ← 4️⃣ Multi-turn chat
```

## 🎯 Scam Detection Patterns

- **Account Threats**: block, suspend, freeze, close
- **Urgency Tactics**: urgent, immediate, deadline, expire
- **Verification Scams**: verify, confirm, KYC update
- **Financial Requests**: UPI ID, account number, OTP, CVV
- **Authority Impersonation**: RBI, government, police
- **Prize Scams**: congratulations, winner, lottery
- **Phishing**: click link, download app
- **Payment Scams**: transfer money, refund pending

## 🕵️ Intelligence Extracted

| Type | Examples |
|------|----------|
| **UPI IDs** | `scammer@paytm`, `9876543210@phonepe` |
| **Phone Numbers** | `+91-9876543210`, `8765432109` |
| **Bank Accounts** | `1234-5678-9012-3456` |
| **Phishing Links** | `http://fake-bank.com/verify` |
| **Keywords** | `urgent`, `verify now`, `account blocked` |

## 🤖 Agent Personality Stages

1. **Initial Concern** (Messages 1-2): Worried but curious
2. **Seeking Clarification** (Messages 3-6): Asking questions, showing hesitation
3. **Expressing Fear** (Messages 7-10): Getting scared but still engaged
4. **Reluctant Compliance** (Messages 11+): Fearful but considering compliance

## 📊 GUVI Integration

**Mandatory Final Callback:**
```json
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+91XXXXXXXXXX"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scam Message  │───▶│  Scam Detector   │───▶│  AI Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│ Final Callback  │◀───│ Intelligence     │◀────────────┘
│   (GUVI API)    │    │   Extractor      │
└─────────────────┘    └──────────────────┘
```

## 🔧 Configuration

Environment variables in `config.py`:
- `FLASK_PORT`: Server port (default: 8080)
- `FLASK_DEBUG`: Debug mode (default: False)
- `API_KEY`: Authentication key
- `MAX_CONVERSATION_LENGTH`: Max messages per session

## 🚀 Production Deployment

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app

# Using Docker
docker-compose up -d
```

## 🛡️ Security & Ethics

✅ **What we do:**
- Waste scammers' time
- Extract intelligence for analysis
- Protect real users
- Follow ethical guidelines

❌ **What we DON'T do:**
- Impersonate real individuals
- Share real personal information
- Engage in illegal activities
- Harass or threaten

## 📈 Evaluation Criteria

- **Scam Detection Accuracy**: How well it identifies scams
- **Agent Quality**: Human-like conversation ability
- **Intelligence Extraction**: Valuable data collection
- **API Stability**: Reliable performance
- **Ethical Behavior**: Responsible engagement

## 🎯 One-Line Summary

**Build an AI-powered agentic honeypot API that detects scam messages, engages scammers in multi-turn conversations, extracts intelligence, and reports final results to GUVI evaluation endpoint.**

---

🔥 **Ready to catch some scammers? Let's go!** 🍯