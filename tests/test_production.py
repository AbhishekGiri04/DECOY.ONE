"""
Production Test Suite
Tests ML detection, NLP extraction, API endpoints, and full system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8080"
API_KEY = "your-secret-api-key"

class TestMLDetection(unittest.TestCase):
    """Test ML-based scam detection"""
    
    def setUp(self):
        from ml_detector import EnhancedMLScamDetector
        self.detector = EnhancedMLScamDetector()
    
    def test_scam_detection_accuracy(self):
        """Test scam detection with real examples"""
        scam_messages = [
            "Your account will be blocked verify immediately",
            "Share your UPI ID to avoid suspension",
            "Send OTP now urgent action required",
            "Transfer money to verify account",
            "You won prize claim now",
            "Click link to verify account urgently"
        ]
        
        for msg in scam_messages:
            is_scam, confidence = self.detector.detect_scam(msg)
            self.assertTrue(is_scam, f"Failed to detect scam: {msg}")
            self.assertGreater(confidence, 0.7, f"Low confidence for: {msg}")
    
    def test_normal_message_detection(self):
        """Test that normal messages are not flagged"""
        normal_messages = [
            "Hello how are you today",
            "Thanks for your help",
            "Let's meet tomorrow",
            "Have a great day",
            "See you soon"
        ]
        
        for msg in normal_messages:
            is_scam, confidence = self.detector.detect_scam(msg)
            self.assertFalse(is_scam, f"False positive for: {msg}")
    
    def test_model_accuracy(self):
        """Test overall model accuracy"""
        self.assertTrue(self.detector.trained, "Model not trained")
        self.assertGreater(self.detector.accuracy, 0.85, "Accuracy below 85%")

class TestNLPExtraction(unittest.TestCase):
    """Test NLP-based intelligence extraction"""
    
    def setUp(self):
        from nlp_extractor import NLPIntelligenceExtractor
        self.extractor = NLPIntelligenceExtractor()
    
    def test_upi_extraction(self):
        """Test UPI ID extraction"""
        messages = [
            {"text": "Send money to scammer@paytm"},
            {"text": "My UPI is 9876543210@ybl"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('upiIds', intel)
        self.assertGreater(len(intel['upiIds']), 0, "Failed to extract UPI IDs")
    
    def test_phone_extraction(self):
        """Test phone number extraction"""
        messages = [
            {"text": "Call me at 9876543210"},
            {"text": "Contact +91-9876543210"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('phoneNumbers', intel)
        self.assertGreater(len(intel['phoneNumbers']), 0, "Failed to extract phone numbers")
    
    def test_link_extraction(self):
        """Test phishing link extraction"""
        messages = [
            {"text": "Click http://fake-bank.com/verify"},
            {"text": "Visit www.scam-site.com"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('phishingLinks', intel)
        self.assertGreater(len(intel['phishingLinks']), 0, "Failed to extract links")
    
    def test_scam_score_calculation(self):
        """Test scam score calculation"""
        high_risk = [{"text": "Urgent! Send OTP and transfer money now!"}]
        low_risk = [{"text": "Hello, how are you?"}]
        
        high_intel = self.extractor.extract_full_intelligence(high_risk)
        low_intel = self.extractor.extract_full_intelligence(low_risk)
        
        self.assertGreater(high_intel['scamScore'], 50, "High risk not detected")
        self.assertLess(low_intel['scamScore'], 30, "Low risk incorrectly scored")

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('features', data)
    
    def test_message_endpoint_scam(self):
        """Test message endpoint with scam"""
        payload = {
            "sessionId": "test-scam-001",
            "message": {
                "sender": "scammer",
                "text": "Your account will be blocked verify immediately",
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/message",
            json=payload,
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('reply', data)
        self.assertGreater(len(data['reply']), 10)
    
    def test_message_endpoint_normal(self):
        """Test message endpoint with normal message"""
        payload = {
            "sessionId": "test-normal-001",
            "message": {
                "sender": "user",
                "text": "Hello how are you",
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/message",
            json=payload,
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = requests.get(f"{BASE_URL}/stats")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_sessions', data)

class TestFullConversation(unittest.TestCase):
    """Test full conversation flow"""
    
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
        self.session_id = f"test-full-{datetime.now().timestamp()}"
    
    def test_multi_turn_conversation(self):
        """Test multi-turn scam conversation"""
        conversation = [
            "Your account will be blocked today",
            "Share your UPI ID immediately",
            "Send the OTP you received",
            "Transfer Rs 1 to verify"
        ]
        
        history = []
        
        for i, msg in enumerate(conversation):
            payload = {
                "sessionId": self.session_id,
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": history
            }
            
            response = requests.post(
                f"{BASE_URL}/api/message",
                json=payload,
                headers=self.headers
            )
            
            self.assertEqual(response.status_code, 200, f"Turn {i+1} failed")
            
            data = response.json()
            self.assertIn('reply', data)
            
            # Add to history
            history.append({"sender": "scammer", "text": msg})
            history.append({"sender": "agent", "text": data['reply']})
        
        print(f"\n✅ Completed {len(conversation)}-turn conversation")

class TestRealScamScenarios(unittest.TestCase):
    """Test with real scam scenarios"""
    
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
    
    def test_account_blocking_scam(self):
        """Test account blocking scam scenario"""
        session_id = "test-blocking-scam"
        
        messages = [
            "Your bank account will be blocked in 2 hours",
            "You need to verify your account immediately",
            "Share your UPI ID to avoid suspension"
        ]
        
        self._run_scenario(session_id, messages)
    
    def test_otp_scam(self):
        """Test OTP scam scenario"""
        session_id = "test-otp-scam"
        
        messages = [
            "We detected suspicious activity on your account",
            "Please share the OTP sent to your mobile",
            "This is urgent for your account security"
        ]
        
        self._run_scenario(session_id, messages)
    
    def test_prize_scam(self):
        """Test prize scam scenario"""
        session_id = "test-prize-scam"
        
        messages = [
            "Congratulations! You won 5 lakh rupees",
            "To claim your prize, pay processing fee",
            "Transfer Rs 500 to claim@paytm"
        ]
        
        self._run_scenario(session_id, messages)
    
    def _run_scenario(self, session_id, messages):
        """Helper to run scam scenario"""
        history = []
        
        for msg in messages:
            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": datetime.now().isoformat()
                },
                "conversationHistory": history
            }
            
            response = requests.post(
                f"{BASE_URL}/api/message",
                json=payload,
                headers=self.headers
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            history.append({"sender": "scammer", "text": msg})
            history.append({"sender": "agent", "text": data['reply']})
        
        print(f"\n✅ Scenario '{session_id}' completed with {len(messages)} turns")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("🧪 PRODUCTION TEST SUITE")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMLDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestFullConversation))
    suite.addTests(loader.loadTestsFromTestCase(TestRealScamScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
