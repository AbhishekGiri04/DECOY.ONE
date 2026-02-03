from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime
import logging
import os
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['honeypot_db']
sessions_collection = db['sessions']
intelligence_collection = db['intelligence']

# ML Model for Scam Detection
class MLScamDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.model = MultinomialNB()
        self.trained = False
        self.train_model()
    
    def train_model(self):
        """Train ML model with scam patterns"""
        # Training data
        scam_messages = [
            "Your account will be blocked",
            "Share your UPI ID immediately",
            "Send OTP now",
            "Transfer money to verify",
            "You won a prize claim now",
            "Your KYC is pending update",
            "Click this link urgently",
            "Account suspended verify now",
            "Bank security alert",
            "Congratulations you won lottery"
        ]
        
        normal_messages = [
            "Hello how are you",
            "What time is the meeting",
            "Can you help me",
            "Thank you very much",
            "Good morning",
            "See you tomorrow",
            "Happy birthday",
            "How was your day",
            "Let's meet for coffee",
            "I love this weather"
        ]
        
        X = scam_messages + normal_messages
        y = [1] * len(scam_messages) + [0] * len(normal_messages)
        
        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)
        self.trained = True
        logger.info("ML model trained successfully")
    
    def detect_scam(self, text):
        """Detect scam using ML model"""
        if not self.trained or not text:
            return False
        
        X_vec = self.vectorizer.transform([text])
        prediction = self.model.predict(X_vec)[0]
        probability = self.model.predict_proba(X_vec)[0]
        
        logger.info(f"Scam probability: {probability[1]:.2f}")
        return prediction == 1 and probability[1] > 0.6

class IntelligenceExtractor:
    """Extract intelligence using advanced patterns"""
    
    def __init__(self):
        self.patterns = {
            'upiIds': [
                r'\b[\w\.-]+@(?:paytm|phonepe|googlepay|amazonpay|ybl|okaxis|okhdfcbank|okicici)\b',
                r'\b\d{10}@\w+\b'
            ],
            'phoneNumbers': [
                r'\+91[-\s]?\d{10}',
                r'\b[6-9]\d{9}\b',
                r'\d{10}'
            ],
            'bankAccounts': [
                r'\b\d{9,18}\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            ],
            'phishingLinks': [
                r'https?://[^\s]+',
                r'www\.[^\s]+',
                r'\w+\.(?:com|in|org|net)/[^\s]*'
            ]
        }
        
        self.keywords = [
            'urgent', 'verify', 'blocked', 'suspended', 'otp', 'pin', 'cvv',
            'account', 'bank', 'upi', 'transfer', 'winner', 'prize', 'kyc',
            'expire', 'immediate', 'click', 'link', 'download'
        ]
    
    def extract(self, conversation_history):
        """Extract all intelligence"""
        all_text = ' '.join([msg.get('text', '') for msg in conversation_history])
        
        intelligence = {}
        for intel_type, patterns in self.patterns.items():
            matches = set()
            for pattern in patterns:
                found = re.findall(pattern, all_text, re.IGNORECASE)
                matches.update(found)
            intelligence[intel_type] = list(matches)
        
        found_keywords = [kw for kw in self.keywords if kw in all_text.lower()]
        intelligence['suspiciousKeywords'] = list(set(found_keywords))
        
        return intelligence

class OllamaAgent:
    """AI Agent using Ollama"""
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model = 'llama3.2:1b'
        self.system_prompt = """You are a 65-year-old confused person who doesn't understand technology.
Someone is calling claiming to be from your bank.
You are worried, nervous, and ask many questions.
Keep responses SHORT (1-2 sentences).
Never reveal you know it's a scam.
Act naturally worried and confused.

Examples:
- "Oh no! Why is my account blocked? What happened?"
- "I'm nervous about sharing that. How do I know you're real?"
- "This sounds urgent. I'm scared. What should I do?"
"""
    
    def generate_response(self, message, conversation_history):
        """Generate intelligent response"""
        # Build context
        context = self.system_prompt + "\n\nConversation:\n"
        
        for msg in conversation_history[-4:]:
            sender = "Caller" if msg.get('sender') == 'scammer' else "You"
            context += f"{sender}: {msg.get('text', '')}\n"
        
        context += f"Caller: {message}\nYou:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 60
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                reply = response.json()['response'].strip()
                reply = reply.split('\n')[0]
                return reply if len(reply) > 10 else self.fallback(message)
            else:
                return self.fallback(message)
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self.fallback(message)
    
    def fallback(self, message):
        """Fallback responses"""
        msg = message.lower()
        
        if 'block' in msg or 'suspend' in msg:
            return "Oh no! Why is my account blocked? I'm so worried! What should I do?"
        elif 'upi' in msg or 'account' in msg:
            return "You need my account details? I'm nervous about sharing that. How do I know you're from the bank?"
        elif 'otp' in msg or 'pin' in msg:
            return "My bank said never to share OTP with anyone. Why do you need it? Is this safe?"
        elif 'transfer' in msg or 'money' in msg:
            return "Transfer money? That doesn't sound right. Why would I need to pay to verify my account?"
        elif 'link' in msg or 'click' in msg:
            return "I'm not comfortable clicking links. Can you tell me what it's for?"
        else:
            return "I don't understand. Can you explain this more clearly? I'm getting confused."

# Initialize components
ml_detector = MLScamDetector()
extractor = IntelligenceExtractor()
agent = OllamaAgent()

@app.before_request
def check_api_key():
    """API key authentication"""
    if request.path in ['/health', '/stats']:
        return None
    
    api_key = request.headers.get('x-api-key')
    expected_key = os.getenv('API_KEY', 'your-secret-api-key')
    
    if not api_key or api_key != expected_key:
        return jsonify({"error": "Unauthorized", "message": "Invalid API key"}), 401

@app.route('/api/message', methods=['POST'])
def handle_message():
    """Main API endpoint"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        logger.info(f"Processing session {session_id}")
        
        # Get or create session in MongoDB
        session = sessions_collection.find_one({'sessionId': session_id})
        if not session:
            session = {
                'sessionId': session_id,
                'scam_detected': False,
                'messages': [],
                'created_at': datetime.now()
            }
        
        # ML-based scam detection
        is_scam = ml_detector.detect_scam(message['text'])
        
        if not is_scam and not history:
            return jsonify({
                "status": "success",
                "reply": "I'm sorry, I don't understand what you're referring to."
            })
        
        if is_scam:
            session['scam_detected'] = True
        
        # Update history
        full_history = history + [message]
        session['messages'] = full_history
        
        # Generate AI response using Ollama
        reply = agent.generate_response(message['text'], full_history)
        
        # Save to MongoDB
        sessions_collection.update_one(
            {'sessionId': session_id},
            {'$set': session},
            upsert=True
        )
        
        # Check if should end conversation
        if len(full_history) >= 12:
            logger.info(f"Ending conversation {session_id}")
            
            # Extract intelligence
            intelligence = extractor.extract(full_history)
            
            # Save intelligence to MongoDB
            intelligence_doc = {
                'sessionId': session_id,
                'intelligence': intelligence,
                'timestamp': datetime.now()
            }
            intelligence_collection.insert_one(intelligence_doc)
            
            # Send to GUVI
            send_final_result(session_id, len(full_history), intelligence)
        
        return jsonify({
            "status": "success",
            "reply": reply
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def send_final_result(session_id, total_messages, intelligence):
    """Send final result to GUVI"""
    guvi_url = os.getenv('GUVI_CALLBACK_URL', 'https://hackathon.guvi.in/api/updateHoneyPotFinalResult')
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": f"ML-detected scam. Extracted {sum(len(v) for v in intelligence.values() if isinstance(v, list))} pieces of intelligence."
    }
    
    try:
        response = requests.post(guvi_url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Final result sent for {session_id}")
        else:
            logger.warning(f"⚠️ GUVI returned {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Failed to send result: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "Production AI Honeypot",
        "version": "2.0.0",
        "features": ["ML Detection", "Ollama AI", "MongoDB"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    """System statistics"""
    total = sessions_collection.count_documents({})
    scam_count = sessions_collection.count_documents({'scam_detected': True})
    intel_count = intelligence_collection.count_documents({})
    
    return jsonify({
        "total_sessions": total,
        "scam_sessions_detected": scam_count,
        "intelligence_records": intel_count
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info("🍯 Starting Production AI Honeypot")
    app.run(host='0.0.0.0', port=port, debug=False)
