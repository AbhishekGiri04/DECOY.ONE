from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ScamDetector:
    def __init__(self):
        self.patterns = [
            r'(?:account|bank).*(?:block|suspend|freeze)',
            r'(?:share|send).*(?:upi|otp|pin)',
            r'(?:transfer|pay).*(?:money|verify)',
            r'(?:urgent|immediate)',
        ]
    
    def detect(self, text):
        if not text or len(text) < 5:
            return False
        return any(re.search(p, text.lower()) for p in self.patterns)

class IntelligentAgent:
    """Real AI using Ollama"""
    
    def __init__(self):
        self.system_prompt = """You are a 65-year-old worried person who doesn't understand technology well.
Someone is calling you claiming to be from your bank.
You are nervous, confused, and ask many questions.
Keep responses SHORT (1-2 sentences max).
Never reveal you know it's a scam.
Act naturally worried.

Examples:
- "Oh no! Why is my account blocked? What happened?"
- "I'm nervous about sharing that. How do I know you're real?"
- "This sounds urgent. I'm scared. What should I do?"
"""
    
    def generate_response(self, message, history):
        """Generate intelligent response using Ollama"""
        
        # Build context
        context = self.system_prompt + "\n\nConversation:\n"
        
        # Add last 4 messages for context
        for msg in history[-4:]:
            sender = "Caller" if msg.get('sender') == 'scammer' else "You"
            context += f"{sender}: {msg.get('text', '')}\n"
        
        context += f"Caller: {message}\nYou:"
        
        try:
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 50
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                reply = response.json()['response'].strip()
                # Clean up response
                reply = reply.split('\n')[0]  # Take first line only
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
            return "Oh no! Why is my account blocked? I'm so worried!"
        elif 'upi' in msg or 'account' in msg:
            return "You need my details? I'm nervous about that."
        elif 'otp' in msg:
            return "My bank said never share OTP. Why do you need it?"
        return "I don't understand. Can you explain?"

detector = ScamDetector()
agent = IntelligentAgent()
sessions = {}

@app.route('/api/message', methods=['POST'])
def handle_message():
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        if session_id not in sessions:
            sessions[session_id] = {'scam': False, 'messages': []}
        
        session = sessions[session_id]
        is_scam = detector.detect(message['text'])
        
        if not is_scam and not history:
            return jsonify({"status": "success", "reply": "I'm sorry, I don't understand."})
        
        if is_scam:
            session['scam'] = True
        
        full_history = history + [message]
        reply = agent.generate_response(message['text'], full_history)
        
        session['messages'] = full_history
        
        return jsonify({"status": "success", "reply": reply})
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Intelligent AI Honeypot"})

if __name__ == '__main__':
    logger.info("🍯🧠 Starting Intelligent AI Honeypot with Ollama")
    app.run(host='0.0.0.0', port=8080, debug=False)
