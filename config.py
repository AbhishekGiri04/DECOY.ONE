import os

class Config:
    # API Configuration
    API_KEY = os.environ.get('API_KEY', 'your-secret-api-key')
    
    # GUVI Callback Configuration
    GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    CALLBACK_TIMEOUT = 5
    
    # Conversation Configuration
    MAX_CONVERSATION_LENGTH = 12
    MIN_INTELLIGENCE_THRESHOLD = 3
    
    # Flask Configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 8080))
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')