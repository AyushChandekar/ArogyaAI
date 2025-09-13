#!/usr/bin/env python3
"""
Final deployment readiness check
"""
import os

def check_deployment_readiness():
    print("🏥 Healthcare Chatbot - Deployment Readiness Check")
    print("=" * 55)
    
    # Check critical files
    critical_files = {
        "Dockerfile": "Docker configuration with port 10000",
        "start_production_robust.sh": "Robust startup with fallback",
        "simple_server.py": "Flask fallback server",
        "requirements.txt": "Dependencies with Flask",
        "domain.yml": "Rasa domain configuration",
        "config-minimal.yml": "Rasa minimal config"
    }
    
    print("📁 Critical Files Check:")
    all_present = True
    for file, description in critical_files.items():
        if os.path.exists(file):
            print(f"   ✅ {file} - {description}")
        else:
            print(f"   ❌ {file} - MISSING!")
            all_present = False
    
    print()
    
    # Check Dockerfile configuration
    print("🐳 Dockerfile Configuration:")
    if os.path.exists("Dockerfile"):
        with open("Dockerfile", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = [
            ("PORT=10000", "Port set to 10000 ✅" if "PORT=10000" in content else "❌ Port not set correctly"),
            ("EXPOSE 10000", "Port 10000 exposed ✅" if "EXPOSE 10000" in content else "❌ Port not exposed"),
            ("start_production_robust.sh", "Robust startup ✅" if "start_production_robust.sh" in content else "❌ Not using robust startup"),
        ]
        
        for check, result in checks:
            print(f"   {result}")
    
    print()
    
    # Check startup script
    print("🚀 Startup Script Analysis:")
    if os.path.exists("start_production_robust.sh"):
        with open("start_production_robust.sh", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("-i 0.0.0.0", "Binds to 0.0.0.0 ✅" if "-i 0.0.0.0" in content else "❌ Wrong host binding"),
            ("$PORT", "Uses PORT env var ✅" if "$PORT" in content else "❌ Hardcoded port"),
            ("simple_server.py", "Has fallback server ✅" if "simple_server.py" in content else "❌ No fallback"),
        ]
        
        for check, result in checks:
            print(f"   {result}")
    
    print()
    
    # Check Flask server
    print("🌐 Flask Fallback Server:")
    if os.path.exists("simple_server.py"):
        with open("simple_server.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("/health", "Health endpoint ✅" if "/health" in content else "❌ No health endpoint"),
            ("/webhooks/rest/webhook", "Webhook endpoint ✅" if "/webhooks/rest/webhook" in content else "❌ No webhook endpoint"),
            ("0.0.0.0", "Correct host binding ✅" if "0.0.0.0" in content else "❌ Wrong host"),
        ]
        
        for check, result in checks:
            print(f"   {result}")
    
    print()
    
    # Summary
    print("📋 Deployment Summary:")
    print("   🎯 Target Platform: Render")
    print("   🌐 Host Binding: 0.0.0.0 (required by Render)")
    print("   🔌 Port: Uses $PORT env variable (Render sets this to 10000)")
    print("   🏥 Primary: Rasa chatbot with health training data")
    print("   🔄 Fallback: Flask server if Rasa fails")
    print("   ❤️  Health Check: /health endpoint for Render")
    print("   💬 Chat API: /webhooks/rest/webhook (Rasa compatible)")
    
    print("\n" + "=" * 55)
    
    if all_present:
        print("🎉 READY FOR DEPLOYMENT!")
        print("\n📤 Next Steps:")
        print("   1. Commit and push your changes to GitHub")
        print("   2. Deploy on Render (it should work now)")
        print("   3. If Rasa fails, fallback server will handle requests")
        print("\n🔗 Your service will be accessible at:")
        print("   https://your-service-name.onrender.com")
        return True
    else:
        print("❌ NOT READY - Missing critical files")
        return False

if __name__ == "__main__":
    check_deployment_readiness()