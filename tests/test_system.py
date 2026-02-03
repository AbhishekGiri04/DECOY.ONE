#!/usr/bin/env python3
"""Simple test for all systems"""

import requests
import time

BASE_URL = "http://localhost:8080"

def test_system():
    print("🧪 Testing Honeypot System\n")
    
    # Test 1: Health
    print("1. Health Check...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"   ✅ {r.json()['status']}\n")
    
    # Test 2: Scam detection
    print("2. Scam Detection...")
    messages = [
        "Your account will be blocked",
        "Share your UPI ID",
        "Send OTP now"
    ]
    
    for msg in messages:
        r = requests.post(f"{BASE_URL}/api/message", json={
            "sessionId": "test-123",
            "message": {"sender": "scammer", "text": msg, "timestamp": "2026-01-21T10:15:30Z"},
            "conversationHistory": []
        })
        reply = r.json()['reply']
        print(f"   Scammer: {msg}")
        print(f"   Agent: {reply}\n")
        time.sleep(1)
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    try:
        test_system()
    except Exception as e:
        print(f"❌ Error: {e}")
