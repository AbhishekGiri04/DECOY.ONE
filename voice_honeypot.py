from flask import Flask, request, jsonify, send_file
import re
import requests
from datetime import datetime
import logging
import os
import tempfile
from gtts import gTTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ScamDetector:
    def __init__(self):
        self.patterns = [
            r'(?:account|bank).*(?:block|suspend|freeze)',
            r'(?:verify|confirm).*(?:urgent|immediate)',
            r'(?:upi|account).*(?:id|number)',
            r'(?:otp|pin|cvv)',
            r'(?:won|prize|congratulations)',
        ]
    
    def detect(self, text):
        if not text:
            return False
        return any(re.search(p, text.lower()) for p in self.patterns)

class Agent:
    def respond(self, message, stage):
        msg = message.lower()
        
        if stage <= 2:
            if 'block' in msg or 'suspend' in msg:
                return "Oh no! Why is my account being blocked? I haven't done anything wrong."
            elif 'verify' in msg or 'kyc' in msg:
                return "What do I need to verify? Is this really from my bank?"
            elif 'won' in msg or 'prize' in msg:
                return "Really? I won something? What did I win?"
            return "I don't understand. Can you explain?"
        
        elif stage <= 6:
            if 'upi' in msg or 'account' in msg:
                return "You need my account details? I'm nervous about sharing that."
            elif 'otp' in msg or 'pin' in msg:
                return "My bank said never to share OTP. Why do you need it?"
            return "I'm still not clear about this."
        
        elif stage <= 10:
            return "This sounds urgent. I'm getting scared."
        
        return "I'm really scared now. Can you guide me?"

detector = ScamDetector()
agent = Agent()
sessions = {}

@app.route('/api/voice/speak', methods=['POST'])
def speak():
    """Convert text to speech and return audio"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        logger.info(f"Generated speech: {text[:50]}...")
        
        return send_file(
            temp_file.name,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='response.mp3'
        )
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/chat', methods=['POST'])
def voice_chat():
    """Text message in, returns both text and audio URL"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message_text = data['message']
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {'messages': [], 'scam': False}
        
        session = sessions[session_id]
        
        # Detect scam
        is_scam = detector.detect(message_text)
        
        if not is_scam and not session['messages']:
            reply = "I'm sorry, I don't understand."
        else:
            if is_scam:
                session['scam'] = True
            
            # Generate response
            stage = len(session['messages'])
            reply = agent.respond(message_text, stage)
            
            # Update session
            session['messages'].append({
                "sender": "scammer",
                "text": message_text,
                "timestamp": datetime.now().isoformat()
            })
            session['messages'].append({
                "sender": "agent",
                "text": reply,
                "timestamp": datetime.now().isoformat()
            })
        
        # Generate audio
        tts = gTTS(text=reply, lang='en', slow=False)
        audio_file = f"/tmp/voice_{session_id}_{len(session['messages'])}.mp3"
        tts.save(audio_file)
        
        logger.info(f"Session {session_id}: {reply[:50]}...")
        
        return jsonify({
            "status": "success",
            "text_reply": reply,
            "audio_file": audio_file,
            "message_count": len(session['messages'])
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/message', methods=['POST'])
def text_message():
    """Original text endpoint"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        if session_id not in sessions:
            sessions[session_id] = {'messages': [], 'scam': False}
        
        session = sessions[session_id]
        is_scam = detector.detect(message['text'])
        
        if not is_scam and not history:
            return jsonify({"status": "success", "reply": "I'm sorry, I don't understand."})
        
        if is_scam:
            session['scam'] = True
        
        full_history = history + [message]
        session['messages'] = full_history
        
        reply = agent.respond(message['text'], len(full_history))
        
        return jsonify({"status": "success", "reply": reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Voice Honeypot",
        "version": "2.0",
        "features": ["text", "voice"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    total = len(sessions)
    scam = sum(1 for s in sessions.values() if s.get('scam'))
    return jsonify({"total_sessions": total, "scam_sessions": scam})

if __name__ == '__main__':
    logger.info("🍯🎤 Starting Voice Honeypot")
    app.run(host='0.0.0.0', port=8080, debug=False)
