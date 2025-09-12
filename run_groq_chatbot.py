#!/usr/bin/env python3
"""
Healthcare Chatbot with Groq AI Translation
Startup script for the restructured RASA-based healthcare chatbot
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def print_header():
    """Print startup header"""
    print("=" * 70)
    print("🏥 HEALTHCARE CHATBOT WITH GROQ AI TRANSLATION")
    print("=" * 70)
    print("🌍 Multilingual Support: English, Hindi, Bengali, Tamil, Telugu, etc.")
    print("💊 Healthcare Knowledge: Diseases, Symptoms, Prevention, Vaccination")
    print("🔄 Real-time Translation: Powered by Groq AI")
    print("=" * 70)

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'healthcare_data.yml',
        'groq_translation_service.py',
        'actions/actions.py',
        'data/nlu.yml',
        'data/stories.yml',
        'data/rules.yml',
        'domain.yml',
        'config.yml',
        'endpoints.yml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files found")
    return True

def train_model():
    """Train the RASA model"""
    print("\n🤖 Training RASA model...")
    try:
        result = subprocess.run(['rasa', 'train'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Model trained successfully")
            return True
        else:
            print("❌ Model training failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return False

def start_action_server():
    """Start the action server in background"""
    print("🚀 Starting action server...")
    try:
        process = subprocess.Popen(
            ['rasa', 'run', 'actions'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Give server time to start
        
        if process.poll() is None:
            print("✅ Action server started successfully")
            return process
        else:
            print("❌ Action server failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting action server: {e}")
        return None

def start_rasa_shell():
    """Start RASA shell for testing"""
    print("\n💬 Starting RASA shell...")
    print("You can now chat with your healthcare assistant!")
    print("Try these examples:")
    print("  - 'Tell me about malaria'")
    print("  - 'मुझे डेंगू के बारे में बताएं'")
    print("  - 'Vaccination schedule for babies'")
    print("  - 'Emergency help'")
    print("\nType '/stop' to exit\n")
    
    try:
        subprocess.run(['rasa', 'shell'])
    except KeyboardInterrupt:
        print("\n\n👋 Chatbot session ended")
    except Exception as e:
        print(f"❌ Error running shell: {e}")

def main():
    """Main startup function"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please ensure all required files are present")
        sys.exit(1)
    
    # Train model
    if not train_model():
        print("\n❌ Model training failed. Please check your configuration")
        sys.exit(1)
    
    # Start action server
    action_process = start_action_server()
    if not action_process:
        print("\n❌ Action server failed to start")
        sys.exit(1)
    
    try:
        # Start RASA shell
        start_rasa_shell()
    finally:
        # Clean up
        if action_process:
            print("\n🛑 Stopping action server...")
            action_process.terminate()
            action_process.wait()
            print("✅ Action server stopped")

if __name__ == "__main__":
    main()
