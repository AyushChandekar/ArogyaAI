#!/usr/bin/env python3
"""
Healthcare Chatbot Deployment Setup Script
Prepares the project for deployment on Render and Netlify
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check if we're in a git repository and if there are uncommitted changes"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a git repository. Please initialize git first:")
            print("   git init")
            print("   git add .")
            print("   git commit -m 'Initial commit'")
            return False
        
        # Check for uncommitted changes
        if "nothing to commit" not in result.stdout:
            print("⚠️ You have uncommitted changes. Please commit them before deploying.")
            print("\nUncommitted files:")
            print(result.stdout)
            return False
        
        return True
    except FileNotFoundError:
        print("❌ Git not found. Please install git and try again.")
        return False

def verify_required_files():
    """Verify all required deployment files exist"""
    required_files = [
        'Dockerfile',
        'start_production.sh', 
        'render.yaml',
        'index.html',
        'netlify.toml',
        '_redirects',
        'credentials.yml',
        'healthcare_data.yml',
        'groq_translation_service.py',
        'actions/actions.py',
        'data/nlu.yml',
        'data/stories.yml',
        'data/rules.yml',
        'domain.yml',
        'config.yml'
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

def check_environment_variables():
    """Check if environment variables are properly configured"""
    print("\n🔐 Environment Variable Check:")
    
    # Check .env.example exists
    if not Path('.env.example').exists():
        print("⚠️ .env.example file not found, but that's okay for deployment")
    
    # Check credentials.yml uses environment variables
    try:
        with open('credentials.yml', 'r') as f:
            content = f.read()
            if '${TELEGRAM_BOT_TOKEN}' in content:
                print("✅ credentials.yml uses environment variables")
            else:
                print("⚠️ credentials.yml may not be using environment variables")
    except FileNotFoundError:
        print("❌ credentials.yml not found")
        return False
    
    return True

def create_gitignore():
    """Create or update .gitignore file"""
    gitignore_content = """# Healthcare Chatbot - Git Ignore

# Environment variables
.env
.env.local
.env.production

# Rasa
models/
.rasa/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore file created/updated")

def make_scripts_executable():
    """Make shell scripts executable (Unix/Linux)"""
    if os.name != 'nt':  # Not Windows
        try:
            os.chmod('start_production.sh', 0o755)
            print("✅ Made start_production.sh executable")
        except FileNotFoundError:
            print("⚠️ start_production.sh not found")

def print_deployment_summary():
    """Print deployment instructions"""
    print(f"""
🎉 Deployment Setup Complete!

Your healthcare chatbot is ready for deployment. Follow these steps:

1. 🐳 RENDER BACKEND DEPLOYMENT:
   • Go to https://render.com
   • Connect your GitHub repository
   • Create new Web Service (Docker, Free tier)
   • Set environment variables:
   - GROQ_API_KEY=your_groq_api_key_here
     - TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
     - RASA_TELEMETRY_ENABLED=false
     - PYTHONPATH=/app
     - PYTHONUNBUFFERED=1
     - PORT=5005

2. 🌐 NETLIFY FRONTEND DEPLOYMENT:
   • Go to https://netlify.com
   • Create site from Git (your repo)
   • Deploy from root directory (no build needed)

3. 📱 TELEGRAM BOT CONNECTION:
   • After Render deployment, run:
     python set_webhook_production.py set --url YOUR_RENDER_URL

4. ✅ TEST EVERYTHING:
   • Web interface: YOUR_NETLIFY_URL
   • Telegram bot: @healthcare20bot
   • API: YOUR_RENDER_URL/status

📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md

🚀 Happy deploying!
""")

def main():
    print("🏥 Healthcare Chatbot - Deployment Setup")
    print("=" * 50)
    
    # Check git status
    print("📋 Checking git status...")
    if not check_git_status():
        return 1
    
    # Verify required files
    print("\n📁 Verifying required files...")
    if not verify_required_files():
        return 1
    
    # Check environment variables
    if not check_environment_variables():
        return 1
    
    # Create .gitignore
    print("\n📝 Creating .gitignore...")
    create_gitignore()
    
    # Make scripts executable
    print("\n🔧 Setting file permissions...")
    make_scripts_executable()
    
    # Print summary
    print_deployment_summary()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
