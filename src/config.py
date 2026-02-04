"""
Configuration Management
Centralized config with validation
"""

import os
from typing import Optional

class Config:
    """Production configuration"""
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # MongoDB
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://SUser:XVI7Q07RWDPdDEgl@scamuser.mr9rdlw.mongodb.net/?appName=ScamUser'
    )
    MONGO_TIMEOUT = int(os.getenv('MONGO_TIMEOUT', 5000))
    
    # Security
    API_KEY = os.getenv('API_KEY', 'your-secret-api-key')
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 100))
    
    # GUVI
    GUVI_CALLBACK_URL = os.getenv(
        'GUVI_CALLBACK_URL',
        'https://hackathon.guvi.in/api/updateHoneyPotFinalResult'
    )
    
    # ML Model
    ML_MODEL_PATH = os.getenv('ML_MODEL_PATH', 'models/scam_detector.pkl')
    ML_VECTORIZER_PATH = os.getenv('ML_VECTORIZER_PATH', 'models/vectorizer.pkl')
    ML_CONFIDENCE_THRESHOLD = float(os.getenv('ML_CONFIDENCE_THRESHOLD', 0.5))
    
    # Session
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    MAX_CONVERSATION_TURNS = int(os.getenv('MAX_CONVERSATION_TURNS', 15))
    
    # Performance
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # Cache
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/honeypot.log')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("Invalid PORT")
        
        if not cls.MONGO_URI:
            errors.append("MONGO_URI not set")
        
        if cls.API_KEY == 'your-secret-api-key':
            errors.append("⚠️  Using default API_KEY (change in production)")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def display(cls):
        """Display configuration"""
        print("="*70)
        print("⚙️  CONFIGURATION")
        print("="*70)
        print(f"Server: {cls.HOST}:{cls.PORT}")
        print(f"MongoDB: {'Connected' if cls.MONGO_URI else 'Not configured'}")
        print(f"Rate Limit: {cls.RATE_LIMIT} req/min")
        print(f"Max Workers: {cls.MAX_WORKERS}")
        print(f"Session Timeout: {cls.SESSION_TIMEOUT}s")
        print(f"Max Turns: {cls.MAX_CONVERSATION_TURNS}")
        print("="*70)

config = Config()
