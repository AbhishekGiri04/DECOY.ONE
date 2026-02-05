import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import re
import requests
from datetime import datetime
import logging
import time
from pymongo import MongoClient

# Import production modules
from ml_detector import EnhancedMLScamDetector
from nlp_extractor import NLPIntelligenceExtractor
from monitoring import monitor, performance_tracker, alert_system
from cache import cache
from rate_limiter import rate_limiter
from logger import setup_logging, RequestLogger
from config import config
from health import health_checker

# Setup logging
setup_logging()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB Connection
try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=config.MONGO_TIMEOUT)
    db = client['honeypot_db']
    sessions_collection = db['sessions']
    intelligence_collection = db['intelligence']
    scam_logs_collection = db['scam_logs']
    client.admin.command('ping')
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    db = None

# Initialize production components
ml_detector = EnhancedMLScamDetector()
extractor = NLPIntelligenceExtractor()

# Conversation Memory Manager
class ConversationMemory:
    def __init__(self):
        self.sessions = {}
    
    def get_context(self, session_id):
        """Get conversation context"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'history': [],
                'extracted_info': {},
                'scammer_tactics': [],
                'trust_level': 1.0,
                'turn_count': 0
            }
        return self.sessions[session_id]
    
    def update_context(self, session_id, message, reply, intelligence):
        """Update conversation context"""
        context = self.get_context(session_id)
        
        context['history'].append({
            'scammer': message,
            'agent': reply,
            'timestamp': datetime.now().isoformat()
        })
        
        context['turn_count'] += 1
        
        # Update extracted info
        for key, value in intelligence.items():
            if isinstance(value, list) and value:
                if key not in context['extracted_info']:
                    context['extracted_info'][key] = []
                context['extracted_info'][key].extend(value)
        
        # Analyze scammer tactics
        msg_lower = message.lower()
        if 'urgent' in msg_lower or 'immediate' in msg_lower:
            context['scammer_tactics'].append('urgency')
        if 'otp' in msg_lower or 'pin' in msg_lower:
            context['scammer_tactics'].append('credential_theft')
        if 'transfer' in msg_lower or 'pay' in msg_lower:
            context['scammer_tactics'].append('payment_fraud')
        
        # Decrease trust level
        context['trust_level'] = max(0.1, context['trust_level'] - 0.1)
        
        return context

# Intelligent Agent with Context Awareness and Ollama
class ContextAwareAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = """You are a 65-year-old confused person who doesn't understand technology.
Someone is calling claiming to be from your bank.
You are nervous, worried, and ask many questions.
Keep responses SHORT (1-2 sentences).
Never reveal you know it's a scam.

Examples:
- "Oh no! Why blocked? What happened?"
- "I'm nervous sharing that. How do I know you're real?"
- "This sounds urgent. I'm scared!"
"""
        self.response_strategies = {
            'initial': [
                "Oh no! Why is my account being {action}? I haven't done anything wrong. What happened?",
                "What exactly do I need to {action}? Is this really from my bank? I'm worried.",
                "I'm confused about this. Can you explain what's happening?"
            ],
            'hesitant': [
                "You need my {detail}? I'm very nervous about sharing that. How do I know you're legitimate?",
                "My bank told me never to share {detail} with anyone. Why do you need it?",
                "I'm not comfortable with this. Can you prove you're really from the bank?"
            ],
            'fearful': [
                "This sounds very urgent. I'm getting scared. What happens if I don't do this?",
                "I'm really worried now. Should I go to my bank branch instead?",
                "This is making me very anxious. Are you sure this is the only way?"
            ],
            'reluctant': [
                "I'm still not sure about this. Can you walk me through it step by step?",
                "I'm really scared but I don't want problems. What exactly should I do?",
                "Can you give me a reference number or someone I can call to verify?"
            ]
        }
    
    def generate_response(self, message, context):
        """Generate context-aware response using Ollama"""
        # Try Ollama first
        ollama_response = self._try_ollama(message, context)
        if ollama_response:
            return ollama_response
        
        # Fallback to rule-based
        return self._fallback_response(message, context)
    
    def _try_ollama(self, message, context):
        """Try to get response from Ollama with better handling"""
        try:
            # Build context
            prompt = self.system_prompt + "\n\nConversation:\n"
            
            # Add history (last 3 turns)
            for msg in context['history'][-3:]:
                prompt += f"Caller: {msg['scammer']}\n"
                prompt += f"You: {msg['agent']}\n"
            
            prompt += f"Caller: {message}\nYou:"
            
            # Call Ollama with longer timeout
            response = requests.post(
                self.ollama_url,
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "num_predict": 80,
                        "top_p": 0.9
                    }
                },
                timeout=15  # Increased timeout
            )
            
            if response.status_code == 200:
                reply = response.json()['response'].strip()
                # Clean response
                reply = reply.split('\n')[0].strip()
                reply = reply.replace('Caller:', '').replace('You:', '').strip()
                
                if len(reply) > 15 and len(reply) < 200:
                    logger.info(f"🤖 Ollama: {reply[:60]}...")
                    return reply
                else:
                    logger.warning(f"Ollama response too short/long: {len(reply)} chars")
                    return None
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            logger.warning("Ollama timeout - using fallback")
            return None
        except Exception as e:
            logger.warning(f"Ollama error: {str(e)[:50]}")
            return None
    
    def _fallback_response(self, message, context):
        """Fallback rule-based response"""
        msg_lower = message.lower()
        turn = context['turn_count']
        trust = context['trust_level']
        
        # Generate response based on message content
        if any(w in msg_lower for w in ['block', 'suspend', 'freeze']):
            return "Oh no! Why is my account being blocked? I haven't done anything wrong. What should I do?"
        
        elif any(w in msg_lower for w in ['upi', 'account', 'details']):
            if trust > 0.7:
                return "You need my account details? I'm nervous about sharing that. How do I know you're legitimate?"
            else:
                return "I'm getting very suspicious now. Why do you keep asking for my details? This doesn't feel right."
        
        elif any(w in msg_lower for w in ['otp', 'pin', 'cvv', 'password']):
            return "My bank always tells me never to share OTP with anyone. Why do you need it? This sounds like a scam."
        
        elif any(w in msg_lower for w in ['transfer', 'pay', 'send', 'money']):
            return "You want me to transfer money? That doesn't sound right at all. Why would I need to pay to verify my own account?"
        
        elif any(w in msg_lower for w in ['link', 'click', 'download']):
            return "I'm not comfortable clicking unknown links. My grandson warned me about phishing. Can you explain what it's for?"
        
        elif any(w in msg_lower for w in ['urgent', 'immediate', 'quickly']):
            return "This sounds very urgent. I'm getting scared. What happens if I don't do this in time?"
        
        elif any(w in msg_lower for w in ['won', 'prize', 'congratulations']):
            return "Really? I won something? That's amazing! But how do I know this is real? What did I win?"
        
        else:
            if turn <= 3:
                return "I don't understand. Can you explain this more clearly? I'm getting confused."
            elif turn <= 6:
                return "I'm still not clear about this. Can you give me more specific details?"
            else:
                return "I'm getting more confused and worried. Maybe I should visit my bank branch instead?"

# Initialize agent and memory
agent = ContextAwareAgent()
memory = ConversationMemory()

# Set monitor DB
monitor.db = db

@app.before_request
def before_request():
    """Pre-request checks"""
    # Skip for health endpoint
    if request.path == '/health':
        return None
    
    # Rate limiting
    client_ip = request.remote_addr
    if not rate_limiter.is_allowed(client_ip):
        return jsonify({
            "error": "Rate limit exceeded",
            "retry_after": 300
        }), 429
    
    # API key authentication for /api/* endpoints
    if request.path.startswith('/api/'):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != config.API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
    
    return None

@app.route('/api/message', methods=['POST'])
def handle_message():
    """Main API endpoint with full intelligence"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        session_id = data['sessionId']
        message = data['message']
        history = data.get('conversationHistory', [])
        metadata = data.get('metadata', {})
        
        # Extract metadata
        channel = metadata.get('channel', 'Unknown')
        language = metadata.get('language', 'English')
        locale = metadata.get('locale', 'IN')
        
        logger.info(f"Processing session {session_id}: {message['text'][:50]}...")
        logger.info(f"Channel: {channel}, Language: {language}, Locale: {locale}")
        
        # Check cache first
        cache_key = f"session:{session_id}"
        context = cache.get(cache_key)
        
        if not context:
            context = memory.get_context(session_id)
        else:
            logger.info(f"Cache hit for {session_id}")
        
        # ML-based scam detection with timing
        ml_start = time.time()
        is_scam, confidence = ml_detector.detect_scam(message['text'])
        ml_time = (time.time() - ml_start) * 1000
        performance_tracker.record_ml_time(ml_time)
        
        # If not scam and no history, ignore
        if not is_scam and not history and context['turn_count'] == 0:
            logger.info(f"Non-scam message ignored: {session_id}")
            return jsonify({
                "status": "success",
                "reply": "I'm sorry, I don't understand what you're referring to."
            })
        
        # Mark as scam
        if is_scam:
            context['scam_detected'] = True
        
        # Generate intelligent response
        reply = agent.generate_response(message['text'], context)
        
        # Extract intelligence with timing
        nlp_start = time.time()
        full_history = history + [message]
        intelligence = extractor.extract_full_intelligence(full_history)
        nlp_time = (time.time() - nlp_start) * 1000
        performance_tracker.record_nlp_time(nlp_time)
        
        # Get scam tactics
        tactics = extractor.get_scam_tactics(intelligence)
        
        # Update conversation memory
        context = memory.update_context(session_id, message['text'], reply, intelligence)
        context['scammer_tactics'] = tactics
        context['ml_confidence'] = confidence
        
        # Update cache
        cache.set(cache_key, context, ttl=config.CACHE_TTL)
        
        # Save to MongoDB with timing
        if db is not None:
            try:
                db_start = time.time()
                session_doc = {
                    'sessionId': session_id,
                    'scam_detected': context.get('scam_detected', False),
                    'ml_confidence': confidence,
                    'messages': full_history,
                    'context': context,
                    'metadata': {
                        'channel': channel,
                        'language': language,
                        'locale': locale
                    },
                    'updated_at': datetime.now()
                }
                sessions_collection.update_one(
                    {'sessionId': session_id},
                    {'$set': session_doc},
                    upsert=True
                )
                db_time = (time.time() - db_start) * 1000
                performance_tracker.record_db_time(db_time)
            except Exception as e:
                logger.error(f"MongoDB save error: {e}")
                monitor.record_error('mongodb_save')
        
        # Check if should end conversation
        if context['turn_count'] >= 12 or len(intelligence.get('upiIds', [])) >= 2:
            logger.info(f"Ending conversation {session_id}")
            
            # Save intelligence to MongoDB
            if db is not None:
                try:
                    intel_doc = {
                        'sessionId': session_id,
                        'intelligence': intelligence,
                        'scammer_tactics': list(set(context['scammer_tactics'])),
                        'total_turns': context['turn_count'],
                        'timestamp': datetime.now()
                    }
                    intelligence_collection.insert_one(intel_doc)
                except Exception as e:
                    logger.error(f"Intelligence save error: {e}")
            
            # Send to GUVI
            send_final_result(session_id, len(full_history), intelligence, context)
        
        # Record metrics
        total_time = time.time() - start_time
        performance_tracker.record_total_time(total_time * 1000)
        
        intel_count = sum(len(v) for v in intelligence.values() if isinstance(v, list))
        monitor.record_request(is_scam, total_time, intel_count)
        
        # Check alerts
        metrics = monitor.get_metrics()
        alert_system.check_metrics(metrics)
        
        # Log request
        RequestLogger.log_request(session_id, message['text'], is_scam, confidence, total_time)
        RequestLogger.log_intelligence(session_id, intelligence)
        
        return jsonify({
            "status": "success",
            "reply": reply,
            "metadata": {
                "ml_confidence": f"{confidence:.2%}",
                "scam_score": intelligence.get('scamScore', 0),
                "processing_time_ms": f"{total_time * 1000:.2f}"
            }
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        monitor.record_error(str(e))
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

def send_final_result(session_id, total_messages, intelligence, context):
    """Send final result to GUVI with enhanced data"""
    guvi_url = os.getenv('GUVI_CALLBACK_URL', 'https://hackathon.guvi.in/api/updateHoneyPotFinalResult')
    
    # Generate detailed agent notes
    tactics = list(set(context.get('scammer_tactics', [])))
    intel_count = sum(len(v) for v in intelligence.values() if isinstance(v, list))
    confidence = context.get('ml_confidence', 0.0)
    
    agent_notes = f"ML-detected scam (confidence: {confidence:.1%}). Scammer used {len(tactics)} tactics: {', '.join(tactics)}. Extracted {intel_count} pieces of intelligence. Scam score: {intelligence.get('scamScore', 0)}/100."
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": {
            "bankAccounts": intelligence.get('bankAccounts', []),
            "upiIds": intelligence.get('upiIds', []),
            "phishingLinks": intelligence.get('phishingLinks', []),
            "phoneNumbers": intelligence.get('phoneNumbers', []),
            "suspiciousKeywords": intelligence.get('suspiciousKeywords', [])
        },
        "agentNotes": agent_notes
    }
    
    try:
        response = requests.post(guvi_url, json=payload, timeout=10, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            logger.info(f"✅ Final result sent for {session_id}")
            
            # Log to MongoDB
            if db:
                scam_logs_collection.insert_one({
                    'sessionId': session_id,
                    'payload': payload,
                    'guvi_response': response.status_code,
                    'timestamp': datetime.now()
                })
        else:
            logger.warning(f"⚠️ GUVI returned {response.status_code}")
    
    except Exception as e:
        logger.error(f"❌ Failed to send result: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    """Comprehensive health check"""
    health_data = health_checker.check_all(db, ml_detector, extractor)
    
    status_code = 200 if health_checker.is_healthy(health_data) else 503
    
    return jsonify(health_data), status_code

@app.route('/stats', methods=['GET'])
def stats():
    """Comprehensive system statistics"""
    try:
        # Get monitor metrics
        metrics = monitor.get_metrics()
        
        # Get performance stats
        perf_stats = performance_tracker.get_stats()
        
        # Get MongoDB stats
        mongo_stats = monitor.get_mongodb_stats() if db is not None else {'error': 'MongoDB not connected'}
        
        # Get recent alerts
        recent_alerts = alert_system.get_recent_alerts(5)
        
        return jsonify({
            "system_metrics": metrics,
            "performance": perf_stats,
            "database": mongo_stats,
            "recent_alerts": recent_alerts,
            "ml_model": {
                "accuracy": f"{ml_detector.accuracy*100:.1f}%",
                "trained": ml_detector.trained
            }
        })
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/intelligence', methods=['GET'])
def get_intelligence():
    """Get all extracted intelligence"""
    if db is None:
        return jsonify({"error": "MongoDB not connected"}), 500
    
    try:
        intel_records = list(intelligence_collection.find().sort('timestamp', -1).limit(10))
        
        # Convert ObjectId to string
        for record in intel_records:
            record['_id'] = str(record['_id'])
        
        return jsonify({
            "status": "success",
            "count": len(intel_records),
            "intelligence": intel_records
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/monitor', methods=['GET'])
def get_monitor_report():
    """Get monitoring report"""
    report = monitor.generate_report()
    return jsonify({
        "report": report,
        "metrics": monitor.get_metrics(),
        "hourly_stats": monitor.get_hourly_stats(24)
    })

@app.route('/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    return jsonify(performance_tracker.get_stats())

if __name__ == '__main__':
    # Validate config
    if not config.validate():
        logger.warning("Configuration validation failed")
    
    # Display config
    config.display()
    
    logger.info("="*70)
    logger.info("🍯 PRODUCTION AI HONEYPOT SYSTEM v3.0")
    logger.info("="*70)
    logger.info(f"✅ ML Model: Trained ({ml_detector.accuracy*100:.1f}% accuracy)" if ml_detector.trained else "❌ ML Model: Not Trained")
    logger.info(f"✅ MongoDB: Connected" if db is not None else "❌ MongoDB: Disconnected")
    logger.info(f"✅ NLP Extractor: {'Loaded with spaCy' if extractor.nlp else 'Regex-only mode'}")
    logger.info(f"✅ Cache: {'Redis' if cache.redis_client else 'Memory'}")
    logger.info(f"✅ Rate Limiter: {config.RATE_LIMIT} req/min")
    logger.info(f"✅ Monitoring: Active")
    logger.info(f"🚀 Server starting on {config.HOST}:{config.PORT}")
    logger.info("="*70)
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
