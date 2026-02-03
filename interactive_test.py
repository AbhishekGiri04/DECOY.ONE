#!/usr/bin/env python3
"""
Interactive Honeypot Tester
Manually test kar sakte ho apne honeypot ko
"""

import requests
import json
from datetime import datetime
import uuid

BASE_URL = "http://localhost:8080"

def print_banner():
    print("=" * 60)
    print("🍯 AGENTIC HONEYPOT - INTERACTIVE TESTER")
    print("=" * 60)
    print()

def test_health():
    """Check if server is running"""
    print("🏥 Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("💡 Start server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_scam_message(session_id, message_text, conversation_history):
    """Send a scam message and get agent response"""
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "conversationHistory": conversation_history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/message", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def interactive_mode():
    """Manual testing mode - tu khud scam messages bhej"""
    print("\n🎮 INTERACTIVE MODE")
    print("=" * 60)
    print("Tu scammer ban ja aur messages bhej!")
    print("Type 'quit' to exit\n")
    
    session_id = f"interactive-{uuid.uuid4().hex[:8]}"
    conversation_history = []
    message_count = 0
    
    print(f"📝 Session ID: {session_id}\n")
    
    while True:
        # User input
        scam_message = input("🔴 Scammer (You): ")
        
        if scam_message.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Exiting interactive mode...")
            break
        
        if not scam_message.strip():
            continue
        
        message_count += 1
        
        # Send to honeypot
        response = send_scam_message(session_id, scam_message, conversation_history)
        
        if response and response.get('status') == 'success':
            agent_reply = response.get('reply', 'No reply')
            print(f"🤖 Agent: {agent_reply}\n")
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scam_message,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            conversation_history.append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            
            # Show message count
            print(f"📊 Messages exchanged: {message_count * 2}")
            
            if message_count >= 12:
                print("\n⚠️  Conversation limit reached (12 messages)")
                print("🔔 GUVI callback should have been triggered!")
                break
        else:
            print("❌ Failed to get response\n")

def quick_test():
    """Quick automated test"""
    print("\n⚡ QUICK TEST MODE")
    print("=" * 60)
    
    session_id = f"quick-test-{uuid.uuid4().hex[:8]}"
    conversation_history = []
    
    test_messages = [
        "Your bank account will be blocked today. Verify immediately.",
        "Share your UPI ID to avoid account suspension.",
        "Transfer ₹1 to 9876543210@paytm for verification.",
        "Click this link: http://fake-bank.com/verify",
        "Send OTP received on your mobile number.",
    ]
    
    print(f"📝 Session ID: {session_id}\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"--- Message {i} ---")
        print(f"🔴 Scammer: {message}")
        
        response = send_scam_message(session_id, message, conversation_history)
        
        if response and response.get('status') == 'success':
            agent_reply = response.get('reply', 'No reply')
            print(f"🤖 Agent: {agent_reply}\n")
            
            # Update history
            conversation_history.append({
                "sender": "scammer",
                "text": message,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            conversation_history.append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.now().isoformat() + "Z"
            })
        else:
            print("❌ Failed\n")
            break
    
    print("✅ Quick test completed!")

def show_stats():
    """Show system statistics"""
    print("\n📊 SYSTEM STATISTICS")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Sessions: {stats.get('total_sessions', 0)}")
            print(f"Scam Sessions Detected: {stats.get('scam_sessions_detected', 0)}")
            print(f"Active Sessions: {stats.get('active_sessions', 0)}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main_menu():
    """Main menu"""
    print_banner()
    
    # Check server health first
    if not test_health():
        return
    
    print("\n📋 SELECT TEST MODE:")
    print("1. Interactive Mode (Manual testing)")
    print("2. Quick Test (Automated)")
    print("3. Show Statistics")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        interactive_mode()
    elif choice == '2':
        quick_test()
    elif choice == '3':
        show_stats()
    elif choice == '4':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice!")
    
    # Show stats at the end
    print()
    show_stats()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
