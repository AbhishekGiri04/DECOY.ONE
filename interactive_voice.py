#!/usr/bin/env python3
"""
Real Interactive Voice Demo
User bolega → Agent sunega → Agent reply karega
"""

import requests
from gtts import gTTS
import os
import tempfile
import time

BASE_URL = "http://localhost:8080"

def agent_speak(text):
    """Agent bolke reply dega"""
    print(f"\n🤖 Agent: {text}")
    
    # Generate audio
    tts = gTTS(text=text, lang='en', slow=False)
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(audio_file.name)
    
    # Play audio
    print(f"🔊 [Playing audio...]")
    os.system(f"afplay {audio_file.name} 2>/dev/null")
    
    # Cleanup
    os.unlink(audio_file.name)

def interactive_conversation():
    """Real interactive conversation"""
    
    print("\n" + "="*70)
    print("🍯📞 INTERACTIVE VOICE HONEYPOT")
    print("="*70)
    print("\n📌 Instructions:")
    print("   1. Tu scammer ban ja")
    print("   2. Type kar ke bol (scammer ki tarah)")
    print("   3. Agent BOLKE reply dega")
    print("   4. Type 'quit' to exit\n")
    print("="*70)
    
    session_id = "interactive-voice"
    turn = 0
    
    while True:
        turn += 1
        print(f"\n{'='*70}")
        print(f"💬 TURN {turn}")
        print(f"{'='*70}")
        
        # User input (scammer)
        scammer_text = input("\n🔴 You (Scammer): ").strip()
        
        if scammer_text.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Conversation ended!")
            break
        
        if not scammer_text:
            print("⚠️  Please type something!")
            continue
        
        # Send to API
        try:
            response = requests.post(f"{BASE_URL}/api/message", json={
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": scammer_text,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": []
            }, timeout=10)
            
            if response.status_code == 200:
                agent_text = response.json()['reply']
                
                # Agent speaks (with audio)
                time.sleep(0.5)  # Small pause
                agent_speak(agent_text)
                
            else:
                print(f"\n❌ Error: {response.status_code}")
                break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break
        
        # Limit conversation
        if turn >= 10:
            print("\n⚠️  Conversation limit reached (10 turns)")
            agent_speak("I need to go now. Goodbye.")
            break
    
    print("\n" + "="*70)
    print("✅ Session completed!")
    print(f"📊 Total turns: {turn}")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        print("\n🎧 Make sure your speakers are ON!")
        input("\nPress Enter to start interactive conversation...")
        
        interactive_conversation()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Conversation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
