from flask import Flask, request, jsonify, send_file
import re
import requests
from datetime import datetime
import logging
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Reuse existing components
class ScamDetector:
    def __init__(self):
        self.scam_patterns = [
            r'(?:account|bank).*(?:block|suspend|freeze|close)',
            r'(?:verify|confirm|update).*(?:urgent|immediate)',
            r'(?:upi|account|card).*(?:id|number|details)',
            r'(?:otp|pin|password|cvv)',
            r'(?:congratulations|winner|won|prize)',
            r'(?:transfer|pay|send).*(?:money|rupees)',
        ]
    
    def detect_scam(self, text):
        if not text:
            return False
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in self.scam_patterns)

class AgentPersonality:
    def generate_response(self, message, conversation_history):
        msg_lower = message.lower()
        stage = len(conversation_history)
        
        if stage <= 2:
            if any(w in msg_lower for w in ['block', 'suspend', 'freeze']):
                return "Oh no! Why is my account being blocked? I haven't done anything wrong."
            elif any(w in msg_lower for w in ['verify', 'confirm', 'kyc']):
                return "What do I need to verify? Is this really from my bank?"
            elif any(w in msg_lower for w in ['won', 'congratulations', 'prize']):
                return "Really? I won something? What did I win?"
            else:
                return "I don't understand. Can you explain?"
        
        elif stage <= 6:
            if any(w in msg_lower for w in ['upi', 'account', 'details']):
                return "You need my account details? I'm nervous about sharing that."
            elif any(w in msg_lower for w in ['otp', 'pin', 'cvv']):
                return "My bank said never to share OTP. Why do you need it?"
            elif any(w in msg_lower for w in ['link', 'click', 'download']):
                return "I'm not comfortable clicking unknown links."
            else:
                return "I'm still not clear about this."
        
        elif stage <= 10:
            return "This sounds urgent. I'm getting scared. What happens if I don't do this?"
        
        else:
            return "I'm really scared now. Can you guide me step by step?"

class VoiceProcessor:
    """Handle voice input/output"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def speech_to_text(self, audio_file):
        """Convert speech to text"""
        try:
            # Load audio file
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Convert to text using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-IN')
            logger.info(f"Transcribed: {text}")
            return text
        
        except sr.UnknownValueError:
            logger.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in speech_to_text: {e}")
            return None
    
    def text_to_speech(self, text, lang='en'):
        """Convert text to speech"""
        try:
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            
            logger.info(f"Generated speech: {text[:50]}...")
            return temp_file.name
        
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            return None

# Initialize components
detector = ScamDetector()
agent = AgentPersonality()
voice_processor = VoiceProcessor()
sessions = {}

@app.route('/api/voice/call', methods=['POST'])
def handle_voice_call():
    """Handle voice call - receives audio, returns audio response"""
    try:
        session_id = request.form.get('sessionId')
        audio_file = request.files.get('audio')
        
        if not session_id or not audio_file:
            return jsonify({"status": "error", "message": "Missing sessionId or audio"}), 400
        
        logger.info(f"Processing voice call for session {session_id}")
        
        # Save uploaded audio temporarily
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_audio.name)
        
        # Convert speech to text
        scammer_text = voice_processor.speech_to_text(temp_audio.name)
        
        if not scammer_text:
            return jsonify({"status": "error", "message": "Could not understand audio"}), 400
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {
                'scam_detected': False,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
        
        session = sessions[session_id]
        
        # Detect scam
        is_scam = detector.detect_scam(scammer_text)
        
        if not is_scam and not session['messages']:
            agent_text = "I'm sorry, I don't understand what you're referring to."
        else:
            if is_scam:
                session['scam_detected'] = True
            
            # Generate agent response
            agent_text = agent.generate_response(scammer_text, session['messages'])
            
            # Update session
            session['messages'].append({
                "sender": "scammer",
                "text": scammer_text,
                "timestamp": datetime.now().isoformat()
            })
            session['messages'].append({
                "sender": "user",
                "text": agent_text,
                "timestamp": datetime.now().isoformat()
            })
        
        # Convert agent response to speech
        audio_response_path = voice_processor.text_to_speech(agent_text)
        
        if not audio_response_path:
            return jsonify({"status": "error", "message": "Could not generate speech"}), 500
        
        # Clean up temp files
        os.unlink(temp_audio.name)
        
        # Return audio response
        return send_file(
            audio_response_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='response.mp3'
        )
    
    except Exception as e:
        logger.error(f"Error in voice call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/voice/message', methods=['POST'])
def handle_voice_message():
    """Handle voice message - text in, audio out"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message_text = data['message']['text']
        
        logger.info(f"Processing voice message for session {session_id}")
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {
                'scam_detected': False,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
        
        session = sessions[session_id]
        
        # Detect scam
        is_scam = detector.detect_scam(message_text)
        
        if not is_scam and not session['messages']:
            agent_text = "I'm sorry, I don't understand."
        else:
            if is_scam:
                session['scam_detected'] = True
            
            # Generate response
            agent_text = agent.generate_response(message_text, session['messages'])
            
            # Update session
            session['messages'].append({
                "sender": "scammer",
                "text": message_text,
                "timestamp": datetime.now().isoformat()
            })
            session['messages'].append({
                "sender": "user",
                "text": agent_text,
                "timestamp": datetime.now().isoformat()
            })
        
        # Generate audio
        audio_path = voice_processor.text_to_speech(agent_text)
        
        return jsonify({
            "status": "success",
            "reply": agent_text,
            "audio_url": f"/api/voice/audio/{os.path.basename(audio_path)}"
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/message', methods=['POST'])
def handle_text_message():
    """Original text-based endpoint"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        if session_id not in sessions:
            sessions[session_id] = {
                'scam_detected': False,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
        
        session = sessions[session_id]
        is_scam = detector.detect_scam(message['text'])
        
        if not is_scam and not history:
            return jsonify({
                "status": "success",
                "reply": "I'm sorry, I don't understand what you're referring to."
            })
        
        if is_scam:
            session['scam_detected'] = True
        
        full_history = history + [message]
        session['messages'] = full_history
        
        reply = agent.generate_response(message['text'], full_history)
        
        return jsonify({
            "status": "success",
            "reply": reply
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Voice-Enabled Agentic Honeypot",
        "version": "2.0.0",
        "features": ["text", "voice"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    total = len(sessions)
    scam_count = sum(1 for s in sessions.values() if s.get('scam_detected'))
    
    return jsonify({
        "total_sessions": total,
        "scam_sessions_detected": scam_count,
        "active_sessions": total
    })

if __name__ == '__main__':
    logger.info("🍯🎤 Starting Voice-Enabled Agentic Honeypot")
    app.run(host='0.0.0.0', port=8080, debug=False)
