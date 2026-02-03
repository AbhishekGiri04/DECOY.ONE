from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
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
            r'(?:verify|confirm).*(?:urgent|immediate)',
            r'(?:upi|account).*(?:id|number)',
            r'(?:otp|pin|cvv)',
            r'(?:won|prize|congratulations)',
            r'(?:transfer|pay|send).*(?:money|rupees)',
        ]
    
    def detect(self, text):
        if not text:
            return False
        return any(re.search(p, text.lower()) for p in self.patterns)

class VoiceAgent:
    def respond(self, message, stage):
        msg = message.lower()
        
        if stage <= 2:
            if 'block' in msg or 'suspend' in msg:
                return "Oh no! Why is my account being blocked? I haven't done anything wrong. What should I do?"
            elif 'verify' in msg or 'kyc' in msg:
                return "What do I need to verify? Is this really from my bank? I'm worried."
            elif 'won' in msg or 'prize' in msg:
                return "Really? I won something? What did I win? How do I claim it?"
            return "I don't understand. Can you explain what this is about?"
        
        elif stage <= 6:
            if 'upi' in msg or 'account' in msg:
                return "You need my account details? I'm nervous about sharing that. How do I know you're legitimate?"
            elif 'otp' in msg or 'pin' in msg:
                return "My bank said never to share OTP with anyone. Why do you need it?"
            elif 'link' in msg or 'click' in msg:
                return "I'm not comfortable clicking unknown links. What is it for?"
            return "I'm still not clear. Can you give me more details?"
        
        elif stage <= 10:
            return "This sounds very urgent. I'm getting scared. What happens if I don't do this?"
        
        return "I'm really scared now but I don't want problems. Can you guide me step by step?"

detector = ScamDetector()
agent = VoiceAgent()
sessions = {}

@app.route('/voice/incoming', methods=['POST'])
def incoming_call():
    """Handle incoming phone call - Twilio webhook"""
    try:
        # Get caller info
        from_number = request.form.get('From', 'unknown')
        call_sid = request.form.get('CallSid', 'unknown')
        
        logger.info(f"Incoming call from {from_number}, SID: {call_sid}")
        
        # Create session
        sessions[call_sid] = {
            'from': from_number,
            'messages': [],
            'scam_detected': False,
            'started_at': datetime.now().isoformat()
        }
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Gather speech input - WAIT for caller to speak first
        gather = Gather(
            input='speech',
            action='/voice/process',
            method='POST',
            language='en-IN',
            timeout=10,
            speech_timeout='auto'
        )
        
        # Just wait silently for caller to speak
        gather.pause(length=1)
        
        response.append(gather)
        
        # If no input, prompt
        response.say("Hello? Are you there?", voice='Polly.Aditi', language='en-IN')
        response.redirect('/voice/incoming')
        
        return str(response), 200, {'Content-Type': 'text/xml'}
    
    except Exception as e:
        logger.error(f"Error in incoming_call: {e}")
        response = VoiceResponse()
        response.say("Sorry, there was an error. Please try again later.")
        response.hangup()
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/voice/process', methods=['POST'])
def process_speech():
    """Process speech input and respond"""
    try:
        call_sid = request.form.get('CallSid', 'unknown')
        speech_result = request.form.get('SpeechResult', '')
        
        logger.info(f"Call {call_sid}: Heard '{speech_result}'")
        
        # Get session
        session = sessions.get(call_sid, {'messages': [], 'scam_detected': False})
        
        # Detect scam
        is_scam = detector.detect(speech_result)
        
        if is_scam:
            session['scam_detected'] = True
            logger.warning(f"SCAM DETECTED in call {call_sid}: {speech_result}")
        
        # Generate agent response
        stage = len(session['messages'])
        agent_reply = agent.respond(speech_result, stage)
        
        # Update session
        session['messages'].append({
            'sender': 'caller',
            'text': speech_result,
            'timestamp': datetime.now().isoformat()
        })
        session['messages'].append({
            'sender': 'agent',
            'text': agent_reply,
            'timestamp': datetime.now().isoformat()
        })
        
        sessions[call_sid] = session
        
        # Create response
        response = VoiceResponse()
        
        # Check if should end call
        if len(session['messages']) >= 20:
            response.say(agent_reply, voice='Polly.Aditi', language='en-IN')
            response.say("I need to go now. Goodbye.", voice='Polly.Aditi', language='en-IN')
            response.hangup()
            
            # Send final report
            if session['scam_detected']:
                send_scam_report(call_sid, session)
        else:
            # Continue conversation
            gather = Gather(
                input='speech',
                action='/voice/process',
                method='POST',
                language='en-IN',
                timeout=5,
                speech_timeout='auto'
            )
            
            gather.say(agent_reply, voice='Polly.Aditi', language='en-IN')
            response.append(gather)
            
            # Fallback
            response.say("Are you still there?", voice='Polly.Aditi', language='en-IN')
            response.redirect('/voice/process')
        
        return str(response), 200, {'Content-Type': 'text/xml'}
    
    except Exception as e:
        logger.error(f"Error in process_speech: {e}")
        response = VoiceResponse()
        response.say("Sorry, I didn't understand. Can you repeat?")
        response.redirect('/voice/process')
        return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/voice/status', methods=['POST'])
def call_status():
    """Handle call status updates"""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    logger.info(f"Call {call_sid} status: {call_status}")
    
    if call_status == 'completed' and call_sid in sessions:
        session = sessions[call_sid]
        if session.get('scam_detected'):
            send_scam_report(call_sid, session)
    
    return '', 200

def send_scam_report(call_sid, session):
    """Send scam report to GUVI"""
    try:
        # Extract intelligence
        all_text = ' '.join([m['text'] for m in session['messages']])
        
        intelligence = {
            'phoneNumbers': [session.get('from', 'unknown')],
            'upiIds': re.findall(r'\b[\w\.-]+@[\w\.-]+\b', all_text),
            'suspiciousKeywords': ['urgent', 'verify', 'otp', 'account', 'blocked']
        }
        
        payload = {
            'sessionId': call_sid,
            'scamDetected': True,
            'totalMessagesExchanged': len(session['messages']),
            'extractedIntelligence': intelligence,
            'agentNotes': f"Voice call scam from {session.get('from')}. Conversation lasted {len(session['messages'])} exchanges."
        }
        
        response = requests.post(
            'https://hackathon.guvi.in/api/updateHoneyPotFinalResult',
            json=payload,
            timeout=10
        )
        
        logger.info(f"Scam report sent for {call_sid}: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Failed to send scam report: {e}")

@app.route('/api/message', methods=['POST'])
def text_message():
    """Text-based endpoint (original)"""
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        
        if session_id not in sessions:
            sessions[session_id] = {'messages': [], 'scam_detected': False}
        
        session = sessions[session_id]
        is_scam = detector.detect(message['text'])
        
        if not is_scam and not history:
            return jsonify({"status": "success", "reply": "I'm sorry, I don't understand."})
        
        if is_scam:
            session['scam_detected'] = True
        
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
        "service": "Production Voice Honeypot",
        "version": "3.0",
        "features": ["text", "voice_calls", "twilio"],
        "active_calls": len([s for s in sessions.values() if 'from' in s]),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def stats():
    total = len(sessions)
    scam = sum(1 for s in sessions.values() if s.get('scam_detected'))
    voice_calls = len([s for s in sessions.values() if 'from' in s])
    
    return jsonify({
        "total_sessions": total,
        "scam_sessions": scam,
        "voice_calls": voice_calls
    })

if __name__ == '__main__':
    logger.info("🍯📞 Starting Production Voice Honeypot with Twilio")
    app.run(host='0.0.0.0', port=8080, debug=False)
