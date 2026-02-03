#!/usr/bin/env python3
"""Test voice-enabled honeypot"""

import requests
from gtts import gTTS
import tempfile
import os

BASE_URL = "http://localhost:8080"

def test_voice_message():
    """Test voice message endpoint (text in, audio out)"""
    print("🎤 TEST: Voice Message (Text to Speech)")
    
    response = requests.post(f"{BASE_URL}/api/voice/message", json={
        "sessionId": "voice-test-1",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today",
            "timestamp": "2026-01-21T10:15:30Z"
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Text Reply: {result['reply']}")
        print(f"✅ Audio URL: {result.get('audio_url', 'N/A')}")
    else:
        print(f"❌ Failed: {response.status_code}")

def test_text_to_speech():
    """Test text-to-speech generation"""
    print("\n🔊 TEST: Text-to-Speech Generation")
    
    text = "Oh no! Why is my account being blocked?"
    
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        file_size = os.path.getsize(temp_file.name)
        print(f"✅ Generated audio file: {temp_file.name}")
        print(f"✅ File size: {file_size} bytes")
        
        os.unlink(temp_file.name)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test health endpoint"""
    print("\n🏥 TEST: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Service: {data['service']}")
        print(f"✅ Features: {data.get('features', [])}")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    print("🍯🎤 VOICE-ENABLED HONEYPOT TESTS\n")
    
    test_health()
    test_text_to_speech()
    test_voice_message()
    
    print("\n✅ All voice tests completed!")
