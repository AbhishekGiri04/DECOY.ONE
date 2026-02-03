#!/usr/bin/env python3
"""
Real Voice Conversation - Microphone se sunega, bolke reply dega
"""

import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import requests
import time

BASE_URL = "http://localhost:8080"

class VoiceHoneypot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.session_id = "voice-session"
        
        # Adjust for ambient noise
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!\n")
    
    def listen(self):
        """Microphone se sun"""
        print("🎤 Listening... (Speak now)")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            print("🔄 Processing speech...")
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio, language='en-IN')
            return text
        
        except sr.WaitTimeoutError:
            print("⏱️  Timeout - No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def speak(self, text):
        """Bolke reply de"""
        print(f"\n🤖 Agent: {text}")
        
        try:
            # Generate audio
            tts = gTTS(text=text, lang='en', slow=False)
            audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(audio_file.name)
            
            # Play audio
            print("🔊 [Speaking...]")
            os.system(f"afplay {audio_file.name} 2>/dev/null")
            
            # Cleanup
            os.unlink(audio_file.name)
        
        except Exception as e:
            print(f"❌ Speech error: {e}")
    
    def get_agent_response(self, user_text):
        """API se agent response le"""
        try:
            response = requests.post(f"{BASE_URL}/api/message", json={
                "sessionId": self.session_id,
                "message": {
                    "sender": "scammer",
                    "text": user_text,
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": []
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json()['reply']
            else:
                return "I'm sorry, I didn't understand that."
        
        except Exception as e:
            print(f"❌ API error: {e}")
            return "Sorry, there was an error."
    
    def start_conversation(self):
        """Real voice conversation start"""
        
        print("\n" + "="*70)
        print("🍯🎤 REAL VOICE HONEYPOT - MICROPHONE MODE")
        print("="*70)
        print("\n📌 Instructions:")
        print("   1. Speak into your microphone")
        print("   2. Agent will listen and understand")
        print("   3. Agent will speak back (reply)")
        print("   4. Say 'goodbye' or 'quit' to exit\n")
        print("="*70)
        
        turn = 0
        
        while True:
            turn += 1
            print(f"\n{'='*70}")
            print(f"💬 TURN {turn}")
            print(f"{'='*70}\n")
            
            # Listen to user
            user_text = self.listen()
            
            if not user_text:
                print("⚠️  No speech detected. Try again.\n")
                continue
            
            print(f"🔴 You said: {user_text}")
            
            # Check for exit
            if any(word in user_text.lower() for word in ['goodbye', 'quit', 'exit', 'bye']):
                self.speak("Goodbye! Take care.")
                break
            
            # Get agent response
            agent_text = self.get_agent_response(user_text)
            
            # Agent speaks
            time.sleep(0.5)
            self.speak(agent_text)
            
            print()
            
            # Limit conversation
            if turn >= 10:
                print("\n⚠️  Conversation limit reached")
                self.speak("I need to go now. Goodbye.")
                break
        
        print("\n" + "="*70)
        print("✅ Conversation ended!")
        print(f"📊 Total turns: {turn}")
        print("="*70 + "\n")

def main():
    try:
        print("\n🎧 Make sure:")
        print("   ✅ Microphone is connected")
        print("   ✅ Speakers are ON")
        print("   ✅ Server is running (python app.py)")
        
        input("\nPress Enter to start voice conversation...")
        
        honeypot = VoiceHoneypot()
        honeypot.start_conversation()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Conversation stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
