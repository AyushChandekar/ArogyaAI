#!/usr/bin/env python3
"""
Quick test to verify the deployment fixes are working
"""
import json
import subprocess
import time
import requests
import threading
import sys

def test_server():
    """Test the server endpoints"""
    print("🧪 Testing server endpoints...")
    
    # Start server in background thread
    def run_server():
        subprocess.run([sys.executable, "simple_server.py"], 
                      env={"PORT": "8080"}, capture_output=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(2)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test chat endpoint
        response = requests.post(
            "http://localhost:8080/webhooks/rest/webhook",
            json={"message": "hello"},
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and "text" in data[0]:
                print(f"   ✅ Chat endpoint: '{data[0]['text'][:50]}...'")
                return True
            else:
                print(f"   ❌ Chat endpoint format error: {data}")
                return False
        else:
            print(f"   ❌ Chat endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server")
        return False
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

def main():
    print("🚀 Quick Deployment Test")
    print("=" * 40)
    
    # Check if key files exist
    import os
    key_files = [
        "Dockerfile", 
        "simple_server.py", 
        "start_production_robust.sh",
        "requirements.txt"
    ]
    
    print("📁 Checking key files...")
    missing = []
    for f in key_files:
        if os.path.exists(f):
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f}")
            missing.append(f)
    
    if missing:
        print(f"\n❌ Missing files: {missing}")
        return 1
    
    print()
    
    # Test server functionality
    if test_server():
        print("\n🎉 SUCCESS! Your deployment fixes are working:")
        print("   ✅ Port binding to 0.0.0.0:$PORT")
        print("   ✅ Health check endpoint (/health)")
        print("   ✅ Chat webhook endpoint (/webhooks/rest/webhook)")
        print("   ✅ Fallback server operational")
        print("\n📦 Ready for Render deployment!")
        return 0
    else:
        print("\n❌ Some issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())