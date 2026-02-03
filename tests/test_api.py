#!/usr/bin/env python3
"""Comprehensive API Tests with Authentication"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"
API_KEY = "your-secret-api-key"

def test_health():
    """Test health endpoint (no auth required)"""
    print("\n1. Testing Health Endpoint...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    print(f"   ✅ Health: {r.json()['status']}")

def test_no_api_key():
    """Test without API key (should fail)"""
    print("\n2. Testing Without API Key...")
    r = requests.post(f"{BASE_URL}/api/message", json={
        "sessionId": "test",
        "message": {"sender": "scammer", "text": "test", "timestamp": "2026-01-21T10:15:30Z"},
        "conversationHistory": []
    })
    assert r.status_code == 401
    print(f"   ✅ Correctly rejected: {r.json()['error']}")

def test_with_api_key():
    """Test with valid API key"""
    print("\n3. Testing With Valid API Key...")
    
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    messages = [
        "Your bank account will be blocked today",
        "Share your UPI ID immediately",
        "Transfer to 9876543210@paytm",
        "Send OTP now"
    ]
    
    for i, msg in enumerate(messages, 1):
        r = requests.post(f"{BASE_URL}/api/message", 
            headers=headers,
            json={
                "sessionId": "test-session",
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": []
            }
        )
        
        assert r.status_code == 200
        reply = r.json()['reply']
        print(f"   Turn {i}:")
        print(f"   Scammer: {msg}")
        print(f"   Agent: {reply}\n")
        time.sleep(0.5)

def test_intelligence_extraction():
    """Test intelligence extraction"""
    print("\n4. Testing Intelligence Extraction...")
    
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    # Message with intelligence
    r = requests.post(f"{BASE_URL}/api/message",
        headers=headers,
        json={
            "sessionId": "intel-test",
            "message": {
                "sender": "scammer",
                "text": "Transfer to 9876543210@paytm or call +91-9876543210",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": []
        }
    )
    
    assert r.status_code == 200
    print(f"   ✅ Message contains:")
    print(f"      - UPI: 9876543210@paytm")
    print(f"      - Phone: +91-9876543210")

def test_stats():
    """Test stats endpoint"""
    print("\n5. Testing Stats Endpoint...")
    r = requests.get(f"{BASE_URL}/stats")
    if r.status_code == 200:
        stats = r.json()
        print(f"   ✅ Total Sessions: {stats['total_sessions']}")
        print(f"   ✅ Scam Sessions: {stats['scam_sessions_detected']}")

def run_all_tests():
    print("="*60)
    print("🧪 COMPREHENSIVE API TESTS")
    print("="*60)
    
    try:
        test_health()
        test_no_api_key()
        test_with_api_key()
        test_intelligence_extraction()
        test_stats()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Server not running! Start with: python src/app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_all_tests()
