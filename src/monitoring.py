"""
Production Monitoring & Analytics Dashboard
Real-time metrics, performance tracking, and visualization
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json

logger = logging.getLogger(__name__)

class ProductionMonitor:
    """Monitor system performance and metrics"""
    
    def __init__(self, db=None):
        self.db = db
        self.metrics = {
            'total_requests': 0,
            'scam_detected': 0,
            'normal_messages': 0,
            'avg_response_time': 0.0,
            'intelligence_extracted': 0,
            'errors': 0,
            'uptime_start': datetime.now()
        }
        
        self.response_times = []
        self.hourly_stats = {}
    
    def record_request(self, is_scam: bool, response_time: float, intelligence_count: int = 0):
        """Record request metrics"""
        self.metrics['total_requests'] += 1
        
        if is_scam:
            self.metrics['scam_detected'] += 1
        else:
            self.metrics['normal_messages'] += 1
        
        self.response_times.append(response_time)
        
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        self.metrics['avg_response_time'] = sum(self.response_times) / len(self.response_times)
        
        if intelligence_count > 0:
            self.metrics['intelligence_extracted'] += intelligence_count
        
        # Hourly stats
        hour_key = datetime.now().strftime('%Y-%m-%d %H:00')
        if hour_key not in self.hourly_stats:
            self.hourly_stats[hour_key] = {'requests': 0, 'scams': 0}
        
        self.hourly_stats[hour_key]['requests'] += 1
        if is_scam:
            self.hourly_stats[hour_key]['scams'] += 1
    
    def record_error(self, error_type: str):
        """Record error"""
        self.metrics['errors'] += 1
        logger.error(f"Error recorded: {error_type}")
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        uptime = datetime.now() - self.metrics['uptime_start']
        
        return {
            **self.metrics,
            'uptime_seconds': uptime.total_seconds(),
            'uptime_hours': uptime.total_seconds() / 3600,
            'scam_detection_rate': (
                self.metrics['scam_detected'] / self.metrics['total_requests'] * 100
                if self.metrics['total_requests'] > 0 else 0
            ),
            'error_rate': (
                self.metrics['errors'] / self.metrics['total_requests'] * 100
                if self.metrics['total_requests'] > 0 else 0
            )
        }
    
    def get_hourly_stats(self, hours: int = 24) -> List[Dict]:
        """Get hourly statistics"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        stats = []
        for hour_key, data in sorted(self.hourly_stats.items()):
            hour_time = datetime.strptime(hour_key, '%Y-%m-%d %H:00')
            if hour_time >= cutoff:
                stats.append({
                    'hour': hour_key,
                    'requests': data['requests'],
                    'scams': data['scams'],
                    'scam_rate': data['scams'] / data['requests'] * 100 if data['requests'] > 0 else 0
                })
        
        return stats
    
    def get_mongodb_stats(self) -> Dict:
        """Get MongoDB statistics"""
        if self.db is None:
            return {'error': 'MongoDB not connected'}
        
        try:
            sessions = self.db['sessions']
            intelligence = self.db['intelligence']
            scam_logs = self.db['scam_logs']
            
            total_sessions = sessions.count_documents({})
            scam_sessions = sessions.count_documents({'scam_detected': True})
            total_intelligence = intelligence.count_documents({})
            total_logs = scam_logs.count_documents({})
            
            # Get recent activity
            recent_sessions = list(sessions.find().sort('updated_at', -1).limit(10))
            
            # Top scam tactics
            pipeline = [
                {'$unwind': '$context.scammer_tactics'},
                {'$group': {
                    '_id': '$context.scammer_tactics',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            
            top_tactics = list(sessions.aggregate(pipeline))
            
            return {
                'total_sessions': total_sessions,
                'scam_sessions': scam_sessions,
                'scam_rate': scam_sessions / total_sessions * 100 if total_sessions > 0 else 0,
                'intelligence_records': total_intelligence,
                'scam_logs': total_logs,
                'recent_activity': len(recent_sessions),
                'top_tactics': [{'tactic': t['_id'], 'count': t['count']} for t in top_tactics]
            }
        
        except Exception as e:
            logger.error(f"MongoDB stats error: {e}")
            return {'error': str(e)}
    
    def generate_report(self) -> str:
        """Generate text report"""
        metrics = self.get_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           🍯 PRODUCTION HONEYPOT SYSTEM REPORT              ║
╚══════════════════════════════════════════════════════════════╝

📊 SYSTEM METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Requests:        {metrics['total_requests']:,}
  Scams Detected:        {metrics['scam_detected']:,}
  Normal Messages:       {metrics['normal_messages']:,}
  Detection Rate:        {metrics['scam_detection_rate']:.1f}%
  
⚡ PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Avg Response Time:     {metrics['avg_response_time']:.3f}s
  Error Rate:            {metrics['error_rate']:.2f}%
  Uptime:                {metrics['uptime_hours']:.1f} hours
  
🔍 INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Intelligence Extracted: {metrics['intelligence_extracted']:,} items
  
✅ STATUS: {'HEALTHY' if metrics['error_rate'] < 5 else 'DEGRADED'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return report

class PerformanceTracker:
    """Track performance metrics"""
    
    def __init__(self):
        self.ml_detection_times = []
        self.nlp_extraction_times = []
        self.db_operation_times = []
        self.total_processing_times = []
    
    def record_ml_time(self, time_ms: float):
        """Record ML detection time"""
        self.ml_detection_times.append(time_ms)
        if len(self.ml_detection_times) > 100:
            self.ml_detection_times = self.ml_detection_times[-100:]
    
    def record_nlp_time(self, time_ms: float):
        """Record NLP extraction time"""
        self.nlp_extraction_times.append(time_ms)
        if len(self.nlp_extraction_times) > 100:
            self.nlp_extraction_times = self.nlp_extraction_times[-100:]
    
    def record_db_time(self, time_ms: float):
        """Record database operation time"""
        self.db_operation_times.append(time_ms)
        if len(self.db_operation_times) > 100:
            self.db_operation_times = self.db_operation_times[-100:]
    
    def record_total_time(self, time_ms: float):
        """Record total processing time"""
        self.total_processing_times.append(time_ms)
        if len(self.total_processing_times) > 100:
            self.total_processing_times = self.total_processing_times[-100:]
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        def calc_stats(times):
            if not times:
                return {'avg': 0, 'min': 0, 'max': 0, 'p95': 0}
            
            sorted_times = sorted(times)
            return {
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'p95': sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0
            }
        
        return {
            'ml_detection': calc_stats(self.ml_detection_times),
            'nlp_extraction': calc_stats(self.nlp_extraction_times),
            'db_operations': calc_stats(self.db_operation_times),
            'total_processing': calc_stats(self.total_processing_times)
        }

class AlertSystem:
    """Alert system for critical events"""
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            'error_rate': 5.0,  # 5%
            'response_time': 3.0,  # 3 seconds
            'scam_rate': 80.0  # 80%
        }
    
    def check_metrics(self, metrics: Dict):
        """Check metrics against thresholds"""
        alerts = []
        
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'level': 'WARNING',
                'message': f"High error rate: {metrics['error_rate']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if metrics.get('avg_response_time', 0) > self.thresholds['response_time']:
            alerts.append({
                'level': 'WARNING',
                'message': f"Slow response time: {metrics['avg_response_time']:.2f}s",
                'timestamp': datetime.now().isoformat()
            })
        
        if metrics.get('scam_detection_rate', 0) > self.thresholds['scam_rate']:
            alerts.append({
                'level': 'INFO',
                'message': f"High scam activity: {metrics['scam_detection_rate']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        self.alerts.extend(alerts)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        return alerts
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alerts[-count:]

# Global instances
monitor = ProductionMonitor()
performance_tracker = PerformanceTracker()
alert_system = AlertSystem()
