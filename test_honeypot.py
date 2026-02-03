import requests
import json
import time

# Test the honeypot API
BASE_URL = "http://localhost:8080"

def test_scam_conversation():
    session_id = "test-session-123"
    
    # Test 1: Initial scam message
    print("=== Test 1: Initial Scam Message ===")
    payload1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response1 = requests.post(f"{BASE_URL}/api/message", json=payload1)
    print(f"Response: {response1.json()}")
    
    # Test 2: Follow-up message
    print("\n=== Test 2: Follow-up Message ===")
    payload2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension.",
            "timestamp": "2026-01-21T10:17:10Z"
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            {
                "sender": "user",
                "text": "Why is my account being suspended?",
                "timestamp": "2026-01-21T10:16:10Z"
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response2 = requests.post(f"{BASE_URL}/api/message", json=payload2)
    print(f"Response: {response2.json()}")

def test_non_scam_message():
    print("\n=== Test 3: Non-Scam Message ===")
    payload = {
        "sessionId": "non-scam-session",
        "message": {
            "sender": "user",
            "text": "Hello, how are you today?",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/message", json=payload)
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        # Test health endpoint
        health = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {health.json()}")
        
        # Run tests
        test_scam_conversation()
        test_non_scam_message()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")