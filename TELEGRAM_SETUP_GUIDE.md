# 🤖 Healthcare Chatbot - Telegram & Web Integration Guide

## 🔥 **URGENT SECURITY NOTE**
Your Telegram bot token is now visible in this session. **Immediately rotate it** for security:
1. Open Telegram and message @BotFather
2. Send `/token` and select your bot
3. Send `/revoke` to get a new token
4. Update the token in `credentials.yml` and `set_webhook.py`

## 📋 Prerequisites

### Required Software:
- **ngrok**: Download from https://ngrok.com/
- **Python packages**: `requests` (install with `pip install requests`)

### Setup ngrok:
1. Download ngrok and extract to a folder
2. Add ngrok to your PATH environment variable
3. Get free auth token from https://dashboard.ngrok.com/
4. Run: `ngrok config add-authtoken YOUR_AUTH_TOKEN`

## 🚀 Method 1: Telegram Integration (Recommended)

### Step 1: Start Your Services
```bash
# Terminal 1: Start action server
python -m rasa run actions

# Terminal 2: Start ngrok
ngrok http 5005

# Terminal 3: Start Rasa server (without Telegram initially)
python -m rasa run --enable-api --cors "*"
```

### Step 2: Set Up Telegram Webhook
```bash
# Get ngrok URL from http://localhost:4040
# Then set webhook automatically:
python set_webhook.py

# Or manually with your ngrok URL:
python set_webhook.py https://your-ngrok-url.ngrok.io
```

### Step 3: Test Your Bot
1. Open Telegram
2. Search for `@healthcare20bot`
3. Send `/start`
4. Try these messages:
   - `Hello`
   - `मलेरिया के बारे में बताएं`
   - `What are the symptoms of dengue?`
   - `डेंगू के लक्षण क्या हैं?`

## 🌐 Method 2: Web Testing (Alternative)

### Step 1: Start Rasa Server
```bash
# Terminal 1: Start action server
python -m rasa run actions

# Terminal 2: Start Rasa with REST API
python -m rasa run --enable-api --cors "*"
```

### Step 2: Open Web Interface
1. Open `web_test.html` in your browser
2. The interface will automatically connect to `http://localhost:5005`
3. Test with the provided quick suggestions or type your own messages

### Step 3: Test Features
- **English**: "What are the symptoms of malaria?"
- **Hindi**: "मलेरिया के बारे में बताएं"
- **Mixed**: Try various health-related questions

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `credentials.yml` | Updated with Telegram configuration |
| `set_webhook.py` | Simple webhook setup script |
| `web_test.html` | Beautiful web testing interface |
| `start_telegram_bot.bat` | Windows batch script (alternative) |
| `telegram_bot_setup.py` | Advanced setup script with ngrok automation |

## 🔧 Troubleshooting

### Common Issues:

1. **"Invalid webhook URL" Error**
   - Make sure ngrok is running on port 5005
   - Check that the URL is HTTPS (not HTTP)
   - Verify the webhook URL format: `https://xxx.ngrok.io/webhooks/telegram/webhook`

2. **ngrok Not Found**
   ```bash
   # Download ngrok and add to PATH
   # Or use full path:
   C:\path\to\ngrok.exe http 5005
   ```

3. **Bot Not Responding**
   - Check that action server is running on port 5055
   - Verify Rasa server is running on port 5005
   - Check webhook status: `python set_webhook.py info`

4. **Web Interface Connection Error**
   - Ensure Rasa server is running with `--enable-api --cors "*"`
   - Check http://localhost:5005 in browser
   - Verify firewall/antivirus isn't blocking the connection

### Quick Commands:
```bash
# Check webhook status
python set_webhook.py info

# Delete webhook
python set_webhook.py delete

# Set specific webhook URL
python set_webhook.py https://your-ngrok-url.ngrok.io

# Test REST API directly
curl -X POST http://localhost:5005/webhooks/rest/webhook -H "Content-Type: application/json" -d "{\"sender\":\"test\",\"message\":\"Hello\"}"
```

## 🌟 Features Demonstrated

### ✅ Working Features:
- **Multilingual Support**: English, Hindi, and more
- **Medical Knowledge**: Disease information, symptoms, prevention
- **Template-based Hindi**: High-quality Hindi medical responses
- **Language Detection**: Automatic detection of input language
- **Web Interface**: Modern, responsive chat interface
- **Telegram Integration**: Full bot functionality via Telegram

### 🧪 Test Cases:
1. **English Medical Query**: "What are the symptoms of malaria?"
2. **Hindi Medical Query**: "मलेरिया के बारे में बताएं"
3. **Disease Information**: "डेंगू के लक्षण क्या हैं?"
4. **Health Advice**: "स्वास्थ्य के लिए सुझाव दें"
5. **Greetings**: "Hello" / "नमस्ते"

## 📱 Production Deployment Tips

1. **Use a VPS/Cloud Server** instead of ngrok for production
2. **Set up SSL certificate** for HTTPS webhook
3. **Configure proper logging** and monitoring
4. **Implement rate limiting** to prevent abuse
5. **Add user authentication** if needed
6. **Monitor webhook delivery** and errors

## 🔐 Security Best Practices

1. **Rotate your bot token immediately** after this session
2. **Use environment variables** for sensitive data
3. **Validate incoming webhook requests**
4. **Implement proper error handling**
5. **Monitor for unusual activity**

---

## 🎯 Quick Start Summary

**For Telegram Bot:**
```bash
# 1. Start services
python -m rasa run actions &
ngrok http 5005 &
python -m rasa run --enable-api --cors "*"

# 2. Set webhook
python set_webhook.py

# 3. Test on Telegram @healthcare20bot
```

**For Web Testing:**
```bash
# 1. Start services
python -m rasa run actions &
python -m rasa run --enable-api --cors "*"

# 2. Open web_test.html in browser
# 3. Start chatting!
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all services are running
3. Check the console logs for error messages
4. Ensure ngrok tunnel is active (for Telegram)

Your healthcare chatbot is now ready for both Telegram and web testing! 🎉
