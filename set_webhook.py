"""
Simple Telegram Webhook Setup Script
Run this after ngrok is running to set the webhook
"""

import requests
import json
import sys
import os

# Telegram Bot Token
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def get_ngrok_url():
    """Get the current ngrok URL"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()
            for tunnel in tunnels.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
        return None
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {e}")
        return None

def set_webhook(webhook_url):
    """Set the Telegram webhook"""
    try:
        data = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        }
        
        response = requests.post(TELEGRAM_API + "setWebhook", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                print(f"   URL: {webhook_url}")
                return True
            else:
                print(f"❌ Telegram API Error: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def get_webhook_info():
    """Get current webhook info"""
    try:
        response = requests.get(TELEGRAM_API + "getWebhookInfo")
        if response.status_code == 200:
            info = response.json()
            if info.get('ok'):
                webhook_info = info.get('result', {})
                print("\n📋 Current Webhook Info:")
                print(f"   URL: {webhook_info.get('url', 'Not set')}")
                print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                if webhook_info.get('last_error_message'):
                    print(f"   Last error: {webhook_info.get('last_error_message')}")
                return True
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
    return False

def delete_webhook():
    """Delete the current webhook"""
    try:
        response = requests.post(TELEGRAM_API + "deleteWebhook")
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook deleted successfully!")
                return True
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
    return False

def main():
    print("🔧 Telegram Webhook Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "delete":
            delete_webhook()
            return
        elif sys.argv[1] == "info":
            get_webhook_info()
            return
        elif sys.argv[1].startswith("https://"):
            ngrok_url = sys.argv[1]
            print(f"📡 Using provided URL: {ngrok_url}")
        else:
            print("Usage:")
            print("  python set_webhook.py                    - Auto-detect ngrok URL")
            print("  python set_webhook.py https://xxx.ngrok.io  - Use specific URL") 
            print("  python set_webhook.py delete             - Delete webhook")
            print("  python set_webhook.py info               - Show webhook info")
            return
    else:
        # Auto-detect ngrok URL
        print("🔍 Looking for ngrok tunnel...")
        ngrok_url = get_ngrok_url()
        
        if not ngrok_url:
            print("❌ Could not find ngrok URL")
            print("Make sure:")
            print("1. ngrok is running (ngrok http 5005)")
            print("2. ngrok API is available on http://localhost:4040")
            print("\nOr run with a specific URL:")
            print("python set_webhook.py https://your-ngrok-url.ngrok.io")
            return
        
        print(f"✅ Found ngrok URL: {ngrok_url}")
    
    # Create webhook URL
    webhook_url = f"{ngrok_url}/webhooks/telegram/webhook"
    print(f"🔗 Setting webhook to: {webhook_url}")
    
    # Set the webhook
    if set_webhook(webhook_url):
        get_webhook_info()
        print(f"""
🎉 Setup Complete!

Your bot is now ready at: https://t.me/healthcare20bot

Test messages:
• Hello
• मलेरिया के बारे में बताएं
• What are the symptoms of dengue?
• डेंगू के लक्षण क्या हैं?
""")
    else:
        print("❌ Failed to set webhook")

if __name__ == "__main__":
    main()
