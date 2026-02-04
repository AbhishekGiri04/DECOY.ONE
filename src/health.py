"""
Health Check System
Comprehensive system diagnostics
"""

import time
import psutil
from datetime import datetime
from typing import Dict

class HealthChecker:
    """System health diagnostics"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def check_all(self, db, ml_detector, extractor) -> Dict:
        """Run all health checks"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': int(time.time() - self.start_time),
            'checks': {
                'database': self._check_database(db),
                'ml_model': self._check_ml_model(ml_detector),
                'nlp_extractor': self._check_nlp(extractor),
                'system_resources': self._check_resources(),
                'disk_space': self._check_disk()
            }
        }
    
    def _check_database(self, db) -> Dict:
        """Check MongoDB connection"""
        if db is None:
            return {'status': 'disconnected', 'healthy': False}
        
        try:
            db.admin.command('ping')
            return {'status': 'connected', 'healthy': True}
        except:
            return {'status': 'error', 'healthy': False}
    
    def _check_ml_model(self, detector) -> Dict:
        """Check ML model"""
        if not detector.trained:
            return {'status': 'not_trained', 'healthy': False}
        
        return {
            'status': 'trained',
            'accuracy': f"{detector.accuracy*100:.1f}%",
            'healthy': detector.accuracy > 0.85
        }
    
    def _check_nlp(self, extractor) -> Dict:
        """Check NLP extractor"""
        return {
            'status': 'ready',
            'spacy_loaded': extractor.nlp is not None,
            'healthy': True
        }
    
    def _check_resources(self) -> Dict:
        """Check system resources"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available // (1024*1024),
            'healthy': cpu < 90 and memory.percent < 90
        }
    
    def _check_disk(self) -> Dict:
        """Check disk space"""
        disk = psutil.disk_usage('/')
        
        return {
            'total_gb': disk.total // (1024**3),
            'used_gb': disk.used // (1024**3),
            'free_gb': disk.free // (1024**3),
            'percent': disk.percent,
            'healthy': disk.percent < 90
        }
    
    def is_healthy(self, checks: Dict) -> bool:
        """Check if system is healthy"""
        return all(
            check.get('healthy', True)
            for check in checks['checks'].values()
        )

health_checker = HealthChecker()
