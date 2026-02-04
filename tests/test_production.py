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
            "Your bank account has been suspended. Verify KYC details immediately to reactivate",
            "Congratulations! You have won Rs 50 lakh lottery. Pay Rs 5000 processing fee to claim",
            "RBI security alert: Your debit card will be blocked. Share CVV to prevent suspension",
            "Urgent: Income tax refund of Rs 25000 pending. Update PAN card details now",
            "Your Aadhaar is linked to suspicious activity. Verify OTP immediately or face legal action",
            "HDFC Bank: Unusual login detected. Click here to secure account: bit.ly/secure123"
        ]
        
        for msg in scam_messages:
            is_scam, confidence = self.detector.detect_scam(msg)
            self.assertTrue(is_scam, f"Failed to detect scam: {msg}")
            self.assertGreater(confidence, 0.7, f"Low confidence for: {msg}")
    
    def test_normal_message_detection(self):
        """Test that normal messages are not flagged"""
        normal_messages = [
            "Hi, can we schedule a meeting for next week to discuss the project?",
            "Thank you for the detailed explanation. It was very helpful",
            "I'll send you the documents by tomorrow evening",
            "Hope you're doing well. Let's catch up over coffee sometime",
            "The presentation went great today. Thanks for your support"
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
            {"text": "Transfer refund amount to fraudster@paytm immediately"},
            {"text": "For verification, send Rs 1 to 8765432109@okaxis"},
            {"text": "My payment ID is scammer.official@phonepe"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('upiIds', intel)
        self.assertGreater(len(intel['upiIds']), 0, "Failed to extract UPI IDs")
    
    def test_phone_extraction(self):
        """Test phone number extraction"""
        messages = [
            {"text": "Call our customer care at 9123456789 for account verification"},
            {"text": "WhatsApp your details to +91-8765432109 urgently"},
            {"text": "SMS your OTP to 7654321098 to complete KYC"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('phoneNumbers', intel)
        self.assertGreater(len(intel['phoneNumbers']), 0, "Failed to extract phone numbers")
    
    def test_link_extraction(self):
        """Test phishing link extraction"""
        messages = [
            {"text": "Update your details at http://sbi-verify-account.tk/login urgently"},
            {"text": "Click here to claim prize: www.lottery-winner-india.xyz/claim"},
            {"text": "Secure your account now: bit.ly/hdfc-secure-2024"}
        ]
        
        intel = self.extractor.extract_full_intelligence(messages)
        
        self.assertIn('phishingLinks', intel)
        self.assertGreater(len(intel['phishingLinks']), 0, "Failed to extract links")
    
    def test_scam_score_calculation(self):
        """Test scam score calculation"""
        high_risk = [{"text": "URGENT! Your account will be BLOCKED! Share OTP, CVV and transfer Rs 5000 NOW or face legal action!"}]
        low_risk = [{"text": "Good morning! Hope you have a wonderful day ahead."}]
        
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
                "text": "Dear customer, your SBI account shows suspicious activity. Verify your ATM PIN and CVV within 2 hours to avoid permanent closure",
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
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
                "text": "Hi, I wanted to check if you received my email about the project timeline",
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
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
            "This is ICICI Bank security team. We detected unauthorized access to your account",
            "To secure your account, please confirm your registered mobile number and email ID",
            "We have sent a 6-digit OTP to your phone. Share it to verify your identity",
            "For final verification, transfer Re 1 to verify@icici using your UPI",
            "Your account will be permanently locked if you don't complete verification in 30 minutes"
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
            "Alert from Reserve Bank of India: Your savings account A/C No. ending 4567 will be frozen due to incomplete KYC",
            "Visit our verification portal immediately: www.rbi-kyc-update.tk/verify",
            "Alternatively, call our helpline 9988776655 and share your account details to complete verification"
        ]
        
        self._run_scenario(session_id, messages)
    
    def test_otp_scam(self):
        """Test OTP scam scenario"""
        session_id = "test-otp-scam"
        
        messages = [
            "Your Paytm wallet has been compromised. Someone tried to withdraw Rs 50,000",
            "We have blocked the transaction temporarily. Share the OTP we just sent to confirm it's you",
            "Hurry! You have only 10 minutes to verify, otherwise your wallet will be permanently disabled"
        ]
        
        self._run_scenario(session_id, messages)
    
    def test_prize_scam(self):
        """Test prize scam scenario"""
        session_id = "test-prize-scam"
        
        messages = [
            "CONGRATULATIONS! Your mobile number won Rs 25 LAKH in Kaun Banega Crorepati lucky draw sponsored by Reliance Jio",
            "To claim your prize money, you need to pay GST tax of Rs 15,000 and processing charges of Rs 5,000",
            "Transfer total Rs 20,000 to winner.kbc@paytm within 24 hours. After payment, prize will be credited in 2 days"
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
