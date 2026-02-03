#!/usr/bin/env python3
"""Live Voice Demo - Agent bolke baat karega"""

import requests
from gtts import gTTS
import os
import tempfile

BASE_URL = "http://localhost:8080"

def speak_and_play(text):
    """Generate speech and play it"""
    print(f"🤖 Agent: {text}")
    
    # Generate audio
    tts = gTTS(text=text, lang='en', slow=False)
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(audio_file.name)
    
    # Play audio
    print(f"🔊 Playing audio...")
    os.system(f"afplay {audio_file.name}")
    
    # Cleanup
    os.unlink(audio_file.name)
    print()

def live_voice_demo():
    """Live voice conversation demo"""
    
    print("="*70)
    print("🍯📞 LIVE VOICE HONEYPOT DEMO")
    print("="*70)
    print("Agent ab BOLKE baat karega - Audio sunai dega!\n")
    
    session_id = "live-demo"
    
    # Conversation
    conversations = [
        {
            "scammer": "Your bank account will be blocked today",
            "agent_expected": "Oh no! Why is my account being blocked?"
        },
        {
            "scammer": "Share your UPI ID to avoid suspension",
            "agent_expected": "You need my account details? I'm nervous..."
        },
        {
            "scammer": "Transfer money to 9876543210@paytm immediately",
            "agent_expected": "I'm still not clear about this..."
        },
        {
            "scammer": "Send your OTP now or account will be closed",
            "agent_expected": "My bank said never to share OTP..."
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print(f"{'='*70}")
        print(f"💬 TURN {i}")
        print(f"{'='*70}")
        
        # Scammer speaks
        print(f"🔴 Scammer: {conv['scammer']}")
        print()
        
        # Get agent response from API
        response = requests.post(f"{BASE_URL}/api/message", json={
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": conv['scammer'],
                "timestamp": "2026-01-21T10:15:30Z"
            },
            "conversationHistory": []
        })
        
        if response.status_code == 200:
            agent_text = response.json()['reply']
            
            # Agent speaks (with audio)
            speak_and_play(agent_text)
        else:
            print(f"❌ Error: {response.status_code}\n")
            break
        
        input("Press Enter for next turn...")
        print()
    
    print("="*70)
    print("✅ DEMO COMPLETE!")
    print("🎤 Agent ne successfully bolke baat ki!")
    print("="*70)

if __name__ == "__main__":
    try:
        print("\n🎧 Make sure your speakers are ON!\n")
        input("Press Enter to start voice demo...")
        print()
        
        live_voice_demo()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
