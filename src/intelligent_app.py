from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# OpenAI API key (set in environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

class ScamDetector:
    def __init__(self):
        self.scam_patterns = [
            r'(?:account|bank).*(?:block|suspend|freeze)',
            r'(?:share|send).*(?:upi|otp|pin|cvv)',
            r'(?:transfer|pay).*(?:money|verify)',
            r'(?:urgent|immediate)',
        ]
    
    def detect_scam(self, text):
        if not text:
            return False
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in self.scam_patterns)

class IntelligentAgent:
    """Real AI agent using GPT for human-like responses"""
    
    def __init__(self):
        self.system_prompt = """You are a worried, confused elderly person who doesn't understand technology well.
You are receiving a call from someone claiming to be from your bank.
You are nervous, ask questions, and show concern.
Keep responses short (1-2 sentences).
Never reveal you know it's a scam.
Act naturally worried and confused.

Examples:
- "Oh no! Why is my account blocked? What did I do wrong?"
- "I'm not sure about sharing that. How do I know you're really from the bank?"
- "This sounds urgent. I'm getting scared. What should I do?"
"""
    
    def generate_response(self, message, conversation_history):
        """Generate intelligent response using GPT"""
        
        # Build conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "assistant" if msg.get('sender') == 'user' else "user"
            messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            # Call OpenAI API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": 100,
                    "temperature": 0.8
                },
                timeout=10
            )
            
            if response.status_code == 200:
                reply = response.json()['choices'][0]['message']['content']
                return reply.strip()
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return self.fallback_response(message)
        
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return self.fallback_response(message)
    
    def fallback_response(self, message):
        """Fallback if API fails"""
        msg_lower = message.lower()
        
        if 'block' in msg_lower or 'suspend' in msg_lower:
            return "Oh no! Why is my account being blocked? I'm so worried!"
        elif 'upi' in msg_lower or 'account' in msg_lower:
            return "You need my account details? I'm nervous about sharing that."
        elif 'otp' in msg_lower or 'pin' in msg_lower:
            return "My bank said never to share OTP. Why do you need it?"
        else:
            return "I don't understand. Can you explain what this is about?"

# Initialize
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
        
        # Get session
        if session_id not in sessions:
            sessions[session_id] = {'scam_detected': False, 'messages': []}
        
        session = sessions[session_id]
        
        # Detect scam
        is_scam = detector.detect_scam(message['text'])
        
        if not is_scam and not history:
            return jsonify({
                "status": "success",
                "reply": "I'm sorry, I don't understand what you're referring to."
            })
        
        if is_scam:
            session['scam_detected'] = True
        
        # Generate intelligent response using GPT
        full_history = history + [message]
        reply = agent.generate_response(message['text'], full_history)
        
        session['messages'] = full_history
        
        return jsonify({
            "status": "success",
            "reply": reply
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Intelligent Honeypot"})

if __name__ == '__main__':
    logger.info("🍯🧠 Starting Intelligent AI Honeypot")
    app.run(host='0.0.0.0', port=8080, debug=False)
