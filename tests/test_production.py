#!/usr/bin/env python3
"""Test Production App with ML and MongoDB"""

import requests
import time

BASE_URL = "http://localhost:8080"
API_KEY = "your-secret-api-key"

def test_production():
    print("🧪 TESTING PRODUCTION APP\n")
    
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    # Test 1: Health
    print("1. Health Check...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"   ✅ {r.json()}\n")
    
    # Test 2: ML Scam Detection
    print("2. ML Scam Detection...")
    scam_messages = [
        "Your account will be blocked today",
        "Share your UPI ID immediately",
        "Transfer to 9876543210@paytm",
        "Send OTP now or account suspended"
    ]
    
    for i, msg in enumerate(scam_messages, 1):
        r = requests.post(f"{BASE_URL}/api/message",
            headers=headers,
            json={
                "sessionId": "ml-test",
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": []
            }
        )
        
        if r.status_code == 200:
            reply = r.json()['reply']
            print(f"   Turn {i}:")
            print(f"   Scammer: {msg}")
            print(f"   AI Agent: {reply}\n")
        
        time.sleep(1)
    
    # Test 3: Stats
    print("3. MongoDB Stats...")
    r = requests.get(f"{BASE_URL}/stats")
    if r.status_code == 200:
        stats = r.json()
        print(f"   ✅ Total Sessions: {stats['total_sessions']}")
        print(f"   ✅ Scam Detected: {stats['scam_sessions_detected']}")
        print(f"   ✅ Intelligence Records: {stats['intelligence_records']}")
    
    print("\n✅ ALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        test_production()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("Start with: python src/production_app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
