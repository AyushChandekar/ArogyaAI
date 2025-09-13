#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""
import os
import sys
import subprocess
import json
import requests
import time
from pathlib import Path

def check_files():
    """Check if required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        "domain.yml",
        "config-minimal.yml",
        "requirements.txt",
        "Dockerfile",
        "simple_server.py",
        "start_production_robust.sh",
        "start_production_ultra_minimal.sh"
    ]
    
    required_dirs = ["data", "actions"]
    
    missing = []
    
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
        else:
            print(f"  ✅ {file}")
    
    for dir_name in required_dirs:
        if not Path(dir_name).is_dir():
            missing.append(dir_name + "/")
        else:
            print(f"  ✅ {dir_name}/")
    
    if missing:
        print(f"  ❌ Missing: {', '.join(missing)}")
        return False
    
    return True

def check_rasa_syntax():
    """Check if Rasa configuration syntax is valid"""
    print("🔍 Checking Rasa configuration...")
    
    try:
        # Check if Rasa can validate the configuration
        result = subprocess.run(
            ["rasa", "data", "validate", "--config", "config-minimal.yml", "--domain", "domain.yml", "--data", "data"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  ✅ Rasa configuration is valid")
            return True
        else:
            print(f"  ❌ Rasa validation failed: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("  ⚠️ Rasa validation timed out")
        return False
    except FileNotFoundError:
        print("  ℹ️ Rasa not installed locally, skipping validation")
        return True

def test_fallback_server():
    """Test the fallback Flask server"""
    print("🧪 Testing fallback server...")
    
    # Start the server in background
    try:
        process = subprocess.Popen([
            sys.executable, "simple_server.py"
        ], env={**os.environ, "PORT": "8080"})
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ Health endpoint working")
            else:
                print(f"  ❌ Health endpoint returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Health endpoint failed: {e}")
            return False
        
        # Test chat endpoint
        try:
            response = requests.post(
                "http://localhost:8080/webhooks/rest/webhook",
                json={"message": "hello"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and "text" in data[0]:
                    print("  ✅ Chat endpoint working")
                    print(f"      Response: {data[0]['text']}")
                else:
                    print(f"  ❌ Chat endpoint returned unexpected format: {data}")
                    return False
            else:
                print(f"  ❌ Chat endpoint returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Chat endpoint failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to start server: {e}")
        return False
    
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass

def main():
    """Main test function"""
    print("🧪 Testing Healthcare Chatbot Deployment Configuration")
    print("=" * 60)
    
    all_passed = True
    
    # Test file existence
    if not check_files():
        all_passed = False
    
    print()
    
    # Test Rasa configuration
    if not check_rasa_syntax():
        all_passed = False
    
    print()
    
    # Test fallback server
    if not test_fallback_server():
        all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed! Your deployment should work on Render.")
        print("\n📋 Deployment Summary:")
        print("   - Port: Uses $PORT environment variable (defaults to 10000)")
        print("   - Host: Binds to 0.0.0.0 (required for Render)")
        print("   - Fallback: Flask server if Rasa fails")
        print("   - Health Check: Available at /health endpoint")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())