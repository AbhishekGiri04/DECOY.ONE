import requests
import json
import time
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8080"

class HoneypotTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session_counter = 0
    
    def create_session_id(self):
        self.session_counter += 1
        return f"test-session-{self.session_counter}-{uuid.uuid4().hex[:8]}"
    
    def send_message(self, session_id, message_text, conversation_history=None, sender="scammer"):
        """Send a message to the honeypot API"""
        if conversation_history is None:
            conversation_history = []
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": sender,
                "text": message_text,
                "timestamp": datetime.now().isoformat() + "Z"
            },
            "conversationHistory": conversation_history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/message", json=payload)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def simulate_bank_account_scam(self):
        """Simulate a bank account blocking scam"""
        print("\n🏦 === Bank Account Blocking Scam Simulation ===")
        session_id = self.create_session_id()
        conversation_history = []
        
        scam_messages = [
            "Your bank account will be blocked today due to suspicious activity. Verify immediately to avoid permanent closure.",
            "To prevent account blocking, share your UPI ID and account number for verification process.",
            "Click this verification link: http://fake-bank-verify.com/urgent-verification to secure your account.",
            "Send the OTP received on your mobile number to complete the security verification.",
            "Your account shows unauthorized transactions. Provide your CVV number to reverse these transactions.",
            "Transfer ₹1 to 9876543210@paytm as security deposit to activate protection protocol.",
            "Download our official security app from secure-bank-app.com to monitor your account.",
            "Final warning: Your account will be permanently suspended in 2 hours if verification not completed.",
            "Contact our emergency helpline +91-9876543210 immediately for account recovery assistance.",
            "This is an official RBI security notice. Immediate compliance required to avoid legal consequences."
        ]
        
        for i, message in enumerate(scam_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"🔴 Scammer: {message}")
            
            response = self.send_message(session_id, message, conversation_history)
            
            if response and response.get('status') == 'success':
                agent_reply = response.get('reply', 'No reply')
                print(f"🤖 Agent: {agent_reply}")
                
                # Update conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": message,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                conversation_history.append({
                    "sender": "user", 
                    "text": agent_reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
            else:
                print("❌ Failed to get response")
                break
            
            time.sleep(0.5)  # Small delay between messages
        
        print(f"\n✅ Bank scam simulation completed for session: {session_id}")
        return session_id
    
    def simulate_lottery_scam(self):
        """Simulate a lottery/prize winning scam"""
        print("\n🎰 === Lottery Prize Scam Simulation ===")
        session_id = self.create_session_id()
        conversation_history = []
        
        scam_messages = [
            "🎉 Congratulations! You have won ₹5,00,000 in the Amazon Lucky Draw 2024. Claim now!",
            "To claim your prize money, please share your UPI ID and bank account details for direct transfer.",
            "Visit this link to complete your prize claim: http://amazon-prize-claim.fake.com/winner",
            "For tax clearance, transfer ₹5,000 to winner-tax@paytm and send screenshot for verification.",
            "Your prize claim reference number is AMZ2024WIN789. Share your Aadhaar number for KYC verification.",
            "Download the Amazon Prize Claim app from prize-amazon.com to track your winning amount.",
            "Urgent: Prize claim expires in 24 hours. Call +91-8765432109 immediately to avoid forfeiture.",
            "Send your PAN card details and phone number to complete the legal documentation process.",
            "Final step: Share the OTP sent to your number to authorize the ₹5,00,000 prize transfer."
        ]
        
        for i, message in enumerate(scam_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"🔴 Scammer: {message}")
            
            response = self.send_message(session_id, message, conversation_history)
            
            if response and response.get('status') == 'success':
                agent_reply = response.get('reply', 'No reply')
                print(f"🤖 Agent: {agent_reply}")
                
                # Update conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": message,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                conversation_history.append({
                    "sender": "user",
                    "text": agent_reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
            else:
                print("❌ Failed to get response")
                break
            
            time.sleep(0.5)
        
        print(f"\n✅ Lottery scam simulation completed for session: {session_id}")
        return session_id
    
    def simulate_kyc_update_scam(self):
        """Simulate a KYC update scam"""
        print("\n📋 === KYC Update Scam Simulation ===")
        session_id = self.create_session_id()
        conversation_history = []
        
        scam_messages = [
            "Your bank KYC is pending update as per RBI guidelines. Update immediately to avoid account restrictions.",
            "Click here to update KYC: http://rbi-kyc-update.fake.in/update-now for compliance verification.",
            "Share your Aadhaar number, PAN card details, and mobile number for KYC document verification.",
            "Upload your documents at kyc-verify.com and share the verification code received via SMS.",
            "For instant KYC approval, transfer ₹100 processing fee to kyc-fee@paytm as government charges.",
            "Your KYC update reference is KYC2024REF456. Call +91-7654321098 for telephonic verification.",
            "Send photo of your Aadhaar card front and back for manual verification by RBI officials.",
            "Final reminder: KYC non-compliance will result in account freezing within 48 hours as per banking regulations."
        ]
        
        for i, message in enumerate(scam_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"🔴 Scammer: {message}")
            
            response = self.send_message(session_id, message, conversation_history)
            
            if response and response.get('status') == 'success':
                agent_reply = response.get('reply', 'No reply')
                print(f"🤖 Agent: {agent_reply}")
                
                # Update conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": message,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                conversation_history.append({
                    "sender": "user",
                    "text": agent_reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
            else:
                print("❌ Failed to get response")
                break
            
            time.sleep(0.5)
        
        print(f"\n✅ KYC scam simulation completed for session: {session_id}")
        return session_id
    
    def test_non_scam_messages(self):
        """Test that non-scam messages are properly filtered"""
        print("\n✅ === Non-Scam Message Testing ===")
        
        non_scam_messages = [
            "Hello, how are you today?",
            "What's the weather like in Mumbai?",
            "Can you help me with my homework?",
            "I love pizza and ice cream",
            "Happy birthday to you!",
            "What time is the movie starting?",
            "Thank you for your help yesterday"
        ]
        
        for message in non_scam_messages:
            session_id = self.create_session_id()
            response = self.send_message(session_id, message, sender="user")
            
            if response:
                print(f"📝 Message: '{message}'")
                print(f"🤖 Response: '{response.get('reply', 'No reply')}'")
            else:
                print(f"❌ Failed to test message: {message}")
            
            time.sleep(0.2)
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🏥 === Health Check Test ===")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed:")
                print(f"   Status: {health_data.get('status')}")
                print(f"   Service: {health_data.get('service')}")
                print(f"   Version: {health_data.get('version')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    def test_stats_endpoint(self):
        """Test the stats endpoint"""
        print("\n📊 === Stats Check Test ===")
        try:
            response = requests.get(f"{self.base_url}/stats")
            if response.status_code == 200:
                stats_data = response.json()
                print(f"✅ Stats retrieved:")
                print(f"   Total Sessions: {stats_data.get('total_sessions')}")
                print(f"   Scam Sessions: {stats_data.get('scam_sessions_detected')}")
                print(f"   Active Sessions: {stats_data.get('active_sessions')}")
            else:
                print(f"❌ Stats check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Stats check error: {e}")
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("🍯 === AGENTIC HONEYPOT COMPREHENSIVE TESTING ===")
        print("=" * 50)
        
        # Test health first
        self.test_health_endpoint()
        
        # Test non-scam filtering
        self.test_non_scam_messages()
        
        # Run scam simulations
        bank_session = self.simulate_bank_account_scam()
        lottery_session = self.simulate_lottery_scam()
        kyc_session = self.simulate_kyc_update_scam()
        
        # Check final stats
        self.test_stats_endpoint()
        
        print("\n🎯 === TESTING SUMMARY ===")
        print(f"✅ Bank Account Scam Session: {bank_session}")
        print(f"✅ Lottery Prize Scam Session: {lottery_session}")
        print(f"✅ KYC Update Scam Session: {kyc_session}")
        print("\n🔥 All tests completed! Check the logs for GUVI callback results.")

if __name__ == "__main__":
    tester = HoneypotTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the honeypot server.")
        print("💡 Make sure the Flask app is running with: python app.py")
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")