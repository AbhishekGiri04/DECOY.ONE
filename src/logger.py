"""
Production Logging System
Structured logging with rotation and levels
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    """Setup production logging"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)s:%(name)s:%(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/honeypot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

class RequestLogger:
    """Log API requests"""
    
    @staticmethod
    def log_request(session_id: str, message: str, is_scam: bool, confidence: float, response_time: float):
        """Log request details"""
        logger = logging.getLogger('requests')
        logger.info(
            f"Session: {session_id} | Scam: {is_scam} | "
            f"Confidence: {confidence:.2%} | Time: {response_time*1000:.0f}ms | "
            f"Message: {message[:50]}"
        )
    
    @staticmethod
    def log_intelligence(session_id: str, intelligence: dict):
        """Log extracted intelligence"""
        logger = logging.getLogger('intelligence')
        intel_count = sum(len(v) for v in intelligence.values() if isinstance(v, list))
        logger.info(
            f"Session: {session_id} | Extracted: {intel_count} items | "
            f"Score: {intelligence.get('scamScore', 0)}/100"
        )
