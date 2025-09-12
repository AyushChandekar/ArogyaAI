#!/usr/bin/env python3
"""
Production Webhook Setup for Healthcare Chatbot
Sets up Telegram webhook using environment variables and production URL
"""

import os
import sys
import requests
import argparse

def get_env_var(var_name, default=None, required=True):
    """Get environment variable with validation"""
    value = os.getenv(var_name, default)
    if required and not value:
        print(f"❌ Error: {var_name} environment variable is required")
        return None
    return value

def set_telegram_webhook(bot_token, webhook_url):
    """Set Telegram webhook"""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        'url': webhook_url,
        'allowed_updates': ['message', 'callback_query'],
        'drop_pending_updates': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print(f"✅ Webhook set successfully!")
            print(f"   URL: {webhook_url}")
            print(f"   Description: {result.get('description', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_webhook_info(bot_token):
    """Get current webhook information"""
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            webhook_info = result.get('result', {})
            print("📋 Current Webhook Info:")
            print(f"   URL: {webhook_info.get('url', 'Not set')}")
            print(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error date: {webhook_info.get('last_error_date', 'None')}")
            print(f"   Last error message: {webhook_info.get('last_error_message', 'None')}")
            return True
        else:
            print(f"❌ Failed to get webhook info: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return False

def delete_webhook(bot_token):
    """Delete current webhook"""
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        response = requests.post(url, json={'drop_pending_updates': True}, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Production Telegram Webhook Setup')
    parser.add_argument('command', choices=['set', 'info', 'delete'], 
                       help='Command to execute')
    parser.add_argument('--url', type=str, 
                       help='Custom webhook URL (overrides environment variable)')
    parser.add_argument('--token', type=str,
                       help='Custom bot token (overrides environment variable)')
    
    args = parser.parse_args()
    
    print("🤖 Healthcare Chatbot - Production Webhook Setup")
    print("=" * 50)
    
    # Get configuration
    bot_token = args.token or get_env_var('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ Bot token not provided. Set TELEGRAM_BOT_TOKEN environment variable or use --token")
        sys.exit(1)
    
    # Execute command
    if args.command == 'info':
        success = get_webhook_info(bot_token)
    elif args.command == 'delete':
        success = delete_webhook(bot_token)
    elif args.command == 'set':
        # Get webhook URL
        webhook_url = args.url or get_env_var('RENDER_BACKEND_URL')
        if not webhook_url:
            print("❌ Webhook URL not provided. Set RENDER_BACKEND_URL environment variable or use --url")
            sys.exit(1)
        
        # Construct full webhook URL
        if not webhook_url.endswith('/'):
            webhook_url += '/'
        webhook_url += 'webhooks/telegram/webhook'
        
        print(f"🔗 Setting webhook to: {webhook_url}")
        success = set_telegram_webhook(bot_token, webhook_url)
    
    if success:
        print("\n✅ Operation completed successfully!")
        
        if args.command == 'set':
            print("\n🎉 Your Telegram bot is now connected to your Render backend!")
            print("📱 Test it by messaging your bot on Telegram")
            print("🏥 Bot username: @healthcare20bot")
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
