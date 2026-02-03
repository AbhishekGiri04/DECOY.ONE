#!/usr/bin/env python3
"""Voice Chat Demo - Agent bolke baat karega"""

import requests
import os

BASE_URL = "http://localhost:8080"

def voice_conversation():
    """Full voice conversation demo"""
    
    print("🍯🎤 VOICE HONEYPOT - LIVE DEMO")
    print("="*60)
    print("Agent ab BOLKE baat karega!\n")
    
    session_id = "voice-demo-123"
    
    # Scam messages
    messages = [
        "Your bank account will be blocked today",
        "Share your UPI ID to avoid suspension",
        "Transfer money to 9876543210@paytm",
        "Send your OTP immediately",
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{'='*60}")
        print(f"💬 Turn {i}")
        print(f"🔴 Scammer: {msg}")
        
        # Send message to voice chat
        response = requests.post(f"{BASE_URL}/api/voice/chat", json={
            "sessionId": session_id,
            "message": msg
        })
        
        if response.status_code == 200:
            result = response.json()
            text_reply = result['text_reply']
            audio_file = result['audio_file']
            
            print(f"🤖 Agent (Text): {text_reply}")
            print(f"🔊 Agent (Audio): {audio_file}")
            print(f"📊 Messages: {result['message_count']}")
            
            # Play audio (macOS)
            print(f"▶️  Playing audio...")
            os.system(f"afplay {audio_file} 2>/dev/null")
            
        else:
            print(f"❌ Error: {response.status_code}")
            break
    
    print(f"\n{'='*60}")
    print("✅ Voice conversation completed!")
    print("🎤 Agent ne bolke baat ki!")

def test_text_to_speech():
    """Test direct text-to-speech"""
    
    print("\n🔊 DIRECT TEXT-TO-SPEECH TEST")
    print("="*60)
    
    text = "Oh no! Why is my account being blocked? I haven't done anything wrong."
    
    print(f"📝 Text: {text}")
    
    response = requests.post(f"{BASE_URL}/api/voice/speak", json={
        "text": text
    })
    
    if response.status_code == 200:
        # Save audio
        audio_file = "/tmp/test_speech.mp3"
        with open(audio_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Audio generated: {audio_file}")
        print(f"▶️  Playing...")
        os.system(f"afplay {audio_file} 2>/dev/null")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    try:
        # Test 1: Direct TTS
        test_text_to_speech()
        
        # Test 2: Full voice conversation
        voice_conversation()
        
        print("\n🎉 All voice tests completed!")
        print("🎤 Agent successfully bolke baat kar raha hai!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
