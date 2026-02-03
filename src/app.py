from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ScamDetector:
    """Detect scam messages using pattern matching"""
    
    def __init__(self):
        self.scam_patterns = [
            r'(?:account|bank).*(?:block|suspend|freeze|close|deactivate|locked)',
            r'(?:block|suspend|freeze|close).*(?:account|bank)',
            r'(?:verify|confirm|update).*(?:urgent|immediate|now|today)',
            r'(?:upi|account|card|bank).*(?:id|number|details)',
            r'(?:share|send|give|provide).*(?:upi|account|otp|pin|cvv|details)',
            r'(?:otp|pin|password|cvv)',
            r'(?:click|visit|download).*(?:link|app)',
            r'(?:congratulations|winner|won|selected|prize|lottery)',
            r'(?:kyc|know.*your.*customer)',
            r'(?:rbi|reserve.*bank|government|police)',
            r'(?:transfer|pay|send).*(?:money|rupees|amount|verify)',
            r'(?:refund|cashback).*(?:pending|claim)',
            r'(?:urgent|immediate|asap|hurry|quickly)',
            r'(?:expire|deadline|last.*chance|final.*warning)',
            r'http[s]?://(?!(?:www\.)?(?:google|facebook|amazon|flipkart|paytm)\.)',
        ]
        
        self.high_risk_keywords = [
            'blocked', 'suspended', 'urgent', 'verify', 'otp', 'pin', 'cvv',
            'upi', 'account', 'bank', 'expire', 'winner', 'congratulations'
        ]
    
    def detect_scam(self, text):
        """Returns True if scam detected"""
        if not text or not text.strip():
            return False
        
        text_lower = text.lower()
        pattern_matches = sum(1 for p in self.scam_patterns if re.search(p, text_lower))
        keyword_matches = sum(1 for k in self.high_risk_keywords if k in text_lower)
        
        return pattern_matches >= 1 or keyword_matches >= 2

class IntelligenceExtractor:
    """Extract intelligence from conversations"""
    
    def __init__(self):
        self.patterns = {
            'bankAccounts': [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                r'\b\d{9,18}\b'
            ],
            'upiIds': [
                r'\b[\w\.-]+@[\w\.-]+\b',
                r'\b\d{10}@(?:paytm|phonepe|googlepay|amazonpay|ybl)\b'
            ],
            'phishingLinks': [
                r'https?://[^\s]+',
                r'www\.[^\s]+',
                r'[a-zA-Z0-9-]+\.(?:com|in|org|net)/[^\s]*'
            ],
            'phoneNumbers': [
                r'\+91[-\s]?\d{10}',
                r'\b[6-9]\d{9}\b'
            ]
        }
        
        self.keywords = [
            'urgent', 'verify now', 'account blocked', 'suspended', 'expire',
            'otp', 'pin', 'cvv', 'last chance', 'final warning', 'immediate',
            'click here', 'download now', 'winner', 'congratulations',
            'refund pending', 'cashback', 'rbi notice', 'legal action'
        ]
    
    def extract(self, conversation_history):
        """Extract all intelligence from conversation"""
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

class AgentPersonality:
    """Generate human-like responses based on conversation stage"""
    
    def generate_response(self, message, conversation_history):
        """Generate contextual response based on conversation stage"""
        msg_lower = message.lower()
        stage = len(conversation_history)
        
        # Stage 1: Initial concern (messages 0-2)
        if stage <= 2:
            if any(w in msg_lower for w in ['block', 'suspend', 'freeze', 'close']):
                return "Oh no! Why is my account being blocked? I haven't done anything wrong. What should I do?"
            elif any(w in msg_lower for w in ['verify', 'confirm', 'update', 'kyc']):
                return "What exactly do I need to verify? Is this really from my bank? I'm a bit worried."
            elif any(w in msg_lower for w in ['won', 'congratulations', 'winner', 'prize']):
                return "Really? I won something? That's amazing! What did I win exactly? How do I claim it?"
            elif any(w in msg_lower for w in ['refund', 'cashback']):
                return "A refund? I wasn't expecting any. How much is it and from where? This sounds good!"
            else:
                return "I'm not sure I understand this message. Can you explain what this is about?"
        
        # Stage 2: Seeking clarification (messages 3-6)
        elif stage <= 6:
            if any(w in msg_lower for w in ['upi', 'account', 'card', 'number', 'details']):
                return "You need my account details? I'm nervous about sharing that. How do I know you're legitimate?"
            elif any(w in msg_lower for w in ['otp', 'pin', 'password', 'cvv']):
                return "My bank always tells me never to share OTP with anyone. Why do you need it? Is this safe?"
            elif any(w in msg_lower for w in ['link', 'click', 'visit', 'download']):
                return "I'm not comfortable clicking unknown links. Can you tell me exactly what it's for?"
            elif any(w in msg_lower for w in ['transfer', 'send', 'pay']):
                return "You want me to transfer money? That doesn't sound right. Why would I need to pay?"
            else:
                return "I'm still not clear about this. Can you give me more specific details?"
        
        # Stage 3: Expressing fear (messages 7-10)
        elif stage <= 10:
            if any(w in msg_lower for w in ['urgent', 'immediate', 'quickly', 'hurry']):
                return "This sounds very urgent. I'm getting scared. What happens if I don't do this in time?"
            elif any(w in msg_lower for w in ['expire', 'deadline', 'last chance']):
                return "How much time do I have? This is making me very anxious. Is there another way to do this?"
            elif any(w in msg_lower for w in ['legal', 'police', 'action']):
                return "Legal action? That sounds serious! I don't want any trouble. What should I do?"
            else:
                return "I'm getting more confused and worried. Maybe I should visit my bank branch instead?"
        
        # Stage 4: Reluctant compliance (messages 11+)
        else:
            return "I'm really scared now but I don't want my account blocked. Can you please guide me step by step?"

class SessionManager:
    """Manage conversation sessions"""
    
    def __init__(self):
        self.sessions = {}
        self.max_length = 12
    
    def get_or_create(self, session_id):
        """Get or create session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'scam_detected': False,
                'messages': [],
                'intelligence': {},
                'created_at': datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def should_end(self, session_id):
        """Check if conversation should end"""
        session = self.sessions.get(session_id, {})
        msg_count = len(session.get('messages', []))
        
        if msg_count >= self.max_length:
            return True
        
        intel = session.get('intelligence', {})
        intel_count = sum(len(v) for v in intel.values() if isinstance(v, list))
        return intel_count >= 3

# Initialize components
detector = ScamDetector()
extractor = IntelligenceExtractor()
agent = AgentPersonality()
sessions = SessionManager()

@app.route('/api/message', methods=['POST'])
def handle_message():
    """Main API endpoint"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        logger.info(f"Processing session {session_id}")
        
        # Get session
        session = sessions.get_or_create(session_id)
        
        # Detect scam
        is_scam = detector.detect_scam(message['text'])
        
        # If not scam and no history, ignore
        if not is_scam and not history:
            return jsonify({
                "status": "success",
                "reply": "I'm sorry, I don't understand what you're referring to."
            })
        
        # Mark as scam
        if is_scam:
            session['scam_detected'] = True
        
        # Update history
        full_history = history + [message]
        session['messages'] = full_history
        
        # Generate response
        reply = agent.generate_response(message['text'], full_history)
        
        # Check if should end
        if sessions.should_end(session_id):
            logger.info(f"Ending conversation {session_id}")
            
            # Extract intelligence
            intelligence = extractor.extract(full_history)
            session['intelligence'] = intelligence
            
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
            "message": "Internal server error"
        }), 500

def send_final_result(session_id, total_messages, intelligence):
    """Send final result to GUVI"""
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": f"Scammer used various tactics. Extracted {sum(len(v) for v in intelligence.values() if isinstance(v, list))} pieces of intelligence."
    }
    
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
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
        "service": "Agentic Honeypot",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    """System statistics"""
    total = len(sessions.sessions)
    scam_count = sum(1 for s in sessions.sessions.values() if s.get('scam_detected'))
    
    return jsonify({
        "total_sessions": total,
        "scam_sessions_detected": scam_count,
        "active_sessions": total
    })

if __name__ == '__main__':
    from config import Config
    logger.info("🍯 Starting Agentic Honeypot System")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
