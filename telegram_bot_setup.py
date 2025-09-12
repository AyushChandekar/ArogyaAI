"""
Telegram Bot Setup and Integration Script
Sets up ngrok tunnel and configures Telegram webhook
"""

import requests
import json
import subprocess
import time
import sys
import os
from urllib.parse import urljoin

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

class TelegramBotSetup:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}/"
        self.ngrok_url = None
        self.webhook_url = None
    
    def check_bot_info(self):
        """Check if bot token is valid"""
        print("🔍 Checking bot information...")
        try:
            response = requests.get(self.api_url + "getMe")
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    print(f"✅ Bot Info:")
                    print(f"   • Name: {bot_info['result']['first_name']}")
                    print(f"   • Username: @{bot_info['result']['username']}")
                    print(f"   • ID: {bot_info['result']['id']}")
                    return True
                else:
                    print(f"❌ Bot API Error: {bot_info}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking bot: {e}")
            return False
    
    def start_ngrok(self, port=5005):
        """Start ngrok tunnel for the specified port"""
        print(f"🌐 Starting ngrok tunnel on port {port}...")
        
        try:
            # Check if ngrok is installed
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ ngrok is not installed. Please install ngrok from https://ngrok.com/")
                print("   Download ngrok and add it to your PATH")
                return False
        except FileNotFoundError:
            print("❌ ngrok is not installed or not in PATH")
            print("   1. Download ngrok from https://ngrok.com/")
            print("   2. Extract and add to PATH")
            print("   3. Run: ngrok authtoken YOUR_AUTH_TOKEN")
            return False
        
        try:
            # Kill any existing ngrok processes
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"], 
                         capture_output=True, shell=True)
            time.sleep(2)
            
            # Start ngrok
            print(f"   Starting ngrok for port {port}...")
            subprocess.Popen(["ngrok", "http", str(port)], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Wait for ngrok to start
            print("   Waiting for ngrok to initialize...")
            time.sleep(5)
            
            # Get ngrok URL
            ngrok_url = self.get_ngrok_url()
            if ngrok_url:
                self.ngrok_url = ngrok_url
                print(f"✅ ngrok tunnel active: {ngrok_url}")
                return True
            else:
                print("❌ Failed to get ngrok URL")
                return False
                
        except Exception as e:
            print(f"❌ Error starting ngrok: {e}")
            return False
    
    def get_ngrok_url(self):
        """Get the public ngrok URL"""
        try:
            # Try to get ngrok status
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels['tunnels']:
                    public_url = tunnels['tunnels'][0]['public_url']
                    return public_url.replace('http://', 'https://')
            return None
        except Exception as e:
            print(f"Warning: Could not get ngrok URL automatically: {e}")
            return None
    
    def set_webhook(self):
        """Set up Telegram webhook"""
        if not self.ngrok_url:
            print("❌ No ngrok URL available")
            return False
        
        self.webhook_url = f"{self.ngrok_url}/webhooks/telegram/webhook"
        
        print(f"🔗 Setting up Telegram webhook...")
        print(f"   Webhook URL: {self.webhook_url}")
        
        try:
            webhook_data = {
                "url": self.webhook_url,
                "allowed_updates": ["message", "callback_query"]
            }
            
            response = requests.post(
                self.api_url + "setWebhook",
                json=webhook_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    print("✅ Webhook set successfully!")
                    return True
                else:
                    print(f"❌ Webhook setup failed: {result}")
                    return False
            else:
                print(f"❌ HTTP Error setting webhook: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False
    
    def get_webhook_info(self):
        """Get current webhook information"""
        print("📋 Getting webhook information...")
        try:
            response = requests.get(self.api_url + "getWebhookInfo")
            if response.status_code == 200:
                webhook_info = response.json()
                if webhook_info['ok']:
                    info = webhook_info['result']
                    print(f"   • URL: {info.get('url', 'Not set')}")
                    print(f"   • Pending updates: {info.get('pending_update_count', 0)}")
                    print(f"   • Last error: {info.get('last_error_message', 'None')}")
                    return True
        except Exception as e:
            print(f"❌ Error getting webhook info: {e}")
        return False
    
    def delete_webhook(self):
        """Delete current webhook"""
        print("🗑️ Deleting existing webhook...")
        try:
            response = requests.post(self.api_url + "deleteWebhook")
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    print("✅ Webhook deleted successfully!")
                    return True
        except Exception as e:
            print(f"❌ Error deleting webhook: {e}")
        return False
    
    def test_bot_response(self):
        """Send a test message to verify bot is working"""
        print("🧪 Bot is ready! Test it by:")
        print("   1. Open Telegram")
        print("   2. Search for @healthcare20bot")
        print("   3. Send: /start")
        print("   4. Try: मलेरिया के बारे में बताएं")
        print("   5. Try: What are dengue symptoms?")

def main():
    """Main setup function"""
    print("🏥 Healthcare Chatbot - Telegram Integration Setup")
    print("=" * 60)
    
    # Initialize setup
    bot_setup = TelegramBotSetup(TELEGRAM_BOT_TOKEN)
    
    # Check bot token
    if not bot_setup.check_bot_info():
        print("❌ Bot token validation failed. Exiting.")
        return
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT SETUP STEPS:")
    print("1. Make sure your Rasa server is running on port 5005")
    print("2. Make sure ngrok is installed and authenticated")
    print("3. Telegram bot credentials are configured")
    print("=" * 60)
    
    input("\nPress Enter when ready to continue...")
    
    # Start ngrok tunnel
    if not bot_setup.start_ngrok(5005):
        print("❌ Failed to start ngrok. Please check installation.")
        return
    
    # Set up webhook
    if not bot_setup.set_webhook():
        print("❌ Failed to set up webhook.")
        return
    
    # Show webhook info
    bot_setup.get_webhook_info()
    
    # Test instructions
    print("\n" + "=" * 60)
    bot_setup.test_bot_response()
    print("=" * 60)
    
    print(f"""
✅ Setup Complete! Your bot is ready at: https://t.me/healthcare20bot

🔧 Technical Details:
   • Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...
   • ngrok URL: {bot_setup.ngrok_url}
   • Webhook: {bot_setup.webhook_url}
   
⚠️  Keep this terminal open to maintain the ngrok tunnel!

To stop the bot:
   1. Close this terminal
   2. Run: ngrok kill (if needed)
   3. Optionally delete webhook using the management script
""")

if __name__ == "__main__":
    main()
