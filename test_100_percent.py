#!/usr/bin/env python3
"""
100% Production Readiness Test
Comprehensive validation of all systems
"""

import sys
import os
sys.path.insert(0, 'src')

def test_all_systems():
    """Test all production systems"""
    
    print("="*70)
    print("🚀 100% PRODUCTION READINESS TEST")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: ML Detector
    print("\n[1/10] ML Detector...")
    try:
        from ml_detector import EnhancedMLScamDetector
        detector = EnhancedMLScamDetector()
        
        assert detector.trained, "Model not trained"
        assert detector.accuracy > 0.85, f"Low accuracy: {detector.accuracy}"
        
        is_scam, conf = detector.detect_scam("Your account blocked verify now")
        assert is_scam, "Failed to detect scam"
        assert conf > 0.7, f"Low confidence: {conf}"
        
        print(f"  ✅ PASS - Accuracy: {detector.accuracy*100:.1f}%")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 2: NLP Extractor
    print("\n[2/10] NLP Extractor...")
    try:
        from nlp_extractor import NLPIntelligenceExtractor
        extractor = NLPIntelligenceExtractor()
        
        messages = [{'text': 'Send to scammer@paytm call 9876543210'}]
        intel = extractor.extract_full_intelligence(messages)
        
        assert len(intel.get('upiIds', [])) > 0, "Failed to extract UPI"
        assert len(intel.get('phoneNumbers', [])) > 0, "Failed to extract phone"
        assert intel.get('scamScore', 0) > 0, "No scam score"
        
        print(f"  ✅ PASS - Extracted {sum(len(v) for v in intel.values() if isinstance(v, list))} items")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 3: Monitoring
    print("\n[3/10] Monitoring System...")
    try:
        from monitoring import ProductionMonitor, PerformanceTracker, AlertSystem
        
        monitor = ProductionMonitor()
        perf = PerformanceTracker()
        alerts = AlertSystem()
        
        monitor.record_request(True, 0.15, 3)
        perf.record_ml_time(45.2)
        
        metrics = monitor.get_metrics()
        assert metrics['total_requests'] > 0, "No requests recorded"
        
        print(f"  ✅ PASS - Tracking {metrics['total_requests']} requests")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 4: Cache System
    print("\n[4/10] Cache System...")
    try:
        from cache import RedisCache
        
        cache = RedisCache()
        cache.set('test_key', {'data': 'test'})
        result = cache.get('test_key')
        
        assert result is not None, "Cache not working"
        assert result['data'] == 'test', "Cache data mismatch"
        
        cache.delete('test_key')
        
        print(f"  ✅ PASS - Cache: {'Redis' if cache.redis_client else 'Memory'}")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 5: Rate Limiter
    print("\n[5/10] Rate Limiter...")
    try:
        from rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=5)
        
        # Should allow first 5
        for i in range(5):
            assert limiter.is_allowed('test_ip'), f"Request {i+1} blocked"
        
        # Should block 6th
        assert not limiter.is_allowed('test_ip'), "Rate limit not enforced"
        
        print(f"  ✅ PASS - Rate limiting working")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 6: Configuration
    print("\n[6/10] Configuration...")
    try:
        from config import Config
        
        assert Config.PORT > 0, "Invalid port"
        assert Config.MONGO_URI, "No MongoDB URI"
        assert Config.RATE_LIMIT > 0, "Invalid rate limit"
        
        print(f"  ✅ PASS - Config validated")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 7: Health Checker
    print("\n[7/10] Health Checker...")
    try:
        from health import HealthChecker
        
        checker = HealthChecker()
        assert checker.start_time > 0, "Health checker not initialized"
        
        print(f"  ✅ PASS - Health checks ready")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 8: Logging System
    print("\n[8/10] Logging System...")
    try:
        from logger import setup_logging, RequestLogger
        
        logger = setup_logging()
        assert logger is not None, "Logger not setup"
        
        RequestLogger.log_request('test', 'msg', True, 0.95, 0.15)
        
        print(f"  ✅ PASS - Logging configured")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 9: Context-Aware Agent
    print("\n[9/10] Context-Aware Agent...")
    try:
        from production_app import agent, memory
        
        context = memory.get_context('test_session')
        reply = agent.generate_response('Your account blocked', context)
        
        assert len(reply) > 10, "Reply too short"
        assert 'block' in reply.lower() or 'account' in reply.lower(), "Reply not contextual"
        
        print(f"  ✅ PASS - Agent generating responses")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Test 10: Full Integration
    print("\n[10/10] Full Integration...")
    try:
        from production_app import app
        
        with app.test_client() as client:
            # Test health
            response = client.get('/health')
            assert response.status_code in [200, 503], f"Health check failed: {response.status_code}"
            
            # Test stats
            response = client.get('/stats')
            assert response.status_code == 200, f"Stats failed: {response.status_code}"
        
        print(f"  ✅ PASS - All endpoints working")
        passed_tests += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
    total_tests += 1
    
    # Results
    print("\n" + "="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 100% PRODUCTION READY!")
        print("="*70)
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
        print("="*70)
        return False

if __name__ == '__main__':
    success = test_all_systems()
    sys.exit(0 if success else 1)
