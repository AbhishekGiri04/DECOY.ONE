import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8080"

def simulate_full_scam_conversation():
    """Simulate a complete scam conversation to test intelligence extraction"""
    session_id = f"test-session-{uuid.uuid4()}"
    conversation_history = []
    
    # Scam messages from scammer
    scam_messages = [
        "Your bank account will be blocked today. Verify immediately to avoid suspension.",
        "Share your UPI ID and account number to prevent account closure.",
        "Click this link to verify: http://fake-bank-verify.com/urgent",
        "Send your OTP received on mobile to complete verification process.",
        "Your account has suspicious activity. Provide CVV to secure it.",
        "Transfer ₹1 to 9876543210@paytm to activate security protocol.",
        "Download our security app from malicious-app.com for protection.",
        "Final warning: Account will be permanently closed in 2 hours.",
        "Contact our helpline +91-9876543210 for immediate assistance.",
        "This is RBI notice. Comply immediately or face legal action."
    ]
    
    print(f"=== Starting Full Scam Conversation Simulation ===")
    print(f"Session ID: {session_id}")
    
    for i, scam_text in enumerate(scam_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"Scammer: {scam_text}")
        
        # Prepare request payload
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_text,
                "timestamp": f"2026-01-21T10:{15+i:02d}:30Z"
            },
            "conversationHistory": conversation_history.copy(),
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        try:
            # Send message to honeypot
            response = requests.post(f"{BASE_URL}/api/message", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                agent_reply = result.get('reply', 'No reply')
                print(f"Agent: {agent_reply}")
                
                # Add both messages to conversation history
                conversation_history.append({\n                    "sender": "scammer",\n                    "text": scam_text,\n                    "timestamp": payload["message"]["timestamp"]\n                })\n                conversation_history.append({\n                    "sender": "user",\n                    "text": agent_reply,\n                    "timestamp": f"2026-01-21T10:{15+i:02d}:45Z"\n                })\n                \n            else:\n                print(f"Error: {response.status_code} - {response.text}")\n                break\n                \n        except requests.exceptions.RequestException as e:\n            print(f"Request failed: {e}")\n            break\n        \n        # Small delay between messages\n        time.sleep(0.5)\n    \n    print(f"\n=== Conversation Complete ===")
    print(f"Total messages exchanged: {len(conversation_history)}")

def test_non_scam_filtering():\n    """Test that non-scam messages are properly filtered out"""\n    print(f"\n=== Testing Non-Scam Message Filtering ===")
n    \n    non_scam_messages = [\n        "Hello, how are you today?",\n        "What's the weather like?",\n        "Can you help me with my homework?",\n        "I love pizza and ice cream",\n        "Happy birthday to you!"\n    ]\n    \n    for message in non_scam_messages:\n        payload = {\n            "sessionId": f"non-scam-{uuid.uuid4()}",\n            "message": {\n                "sender": "user",\n                "text": message,\n                "timestamp": "2026-01-21T10:15:30Z"\n            },\n            "conversationHistory": [],\n            "metadata": {\n                "channel": "SMS",\n                "language": "English",\n                "locale": "IN"\n            }\n        }\n        \n        response = requests.post(f"{BASE_URL}/api/message", json=payload)\n        result = response.json()\n        print(f"Message: '{message}' -> Response: '{result.get('reply', 'No reply')}'")

def test_health_endpoint():
    """Test the health check endpoint"""
    print(f"\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"Health check passed: {response.json()}")
        else:
            print(f"Health check failed: {response.status_code}")
    except Exception as e:
        print(f"Health check error: {e}")

if __name__ == "__main__":
    try:
        # Test health endpoint first
        test_health_endpoint()
        
        # Test non-scam filtering
        test_non_scam_filtering()
        
        # Run full scam conversation simulation
        simulate_full_scam_conversation()
        
        print(f"\n=== All Tests Complete ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the Flask app is running with: python app.py")
    except Exception as e:
        print(f"Unexpected error: {e}")