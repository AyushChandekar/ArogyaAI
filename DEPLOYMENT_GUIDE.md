# 🚀 Healthcare Chatbot - Complete Deployment Guide

Deploy your multilingual healthcare chatbot with **free hosting** on Render (backend) and Netlify (frontend), plus connect your Telegram bot!

## 📋 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Netlify       │    │     Render      │    │    Telegram     │
│   Frontend      │───▶│   Rasa Backend  │◀───│      Bot        │
│   (Free Static) │    │   + Actions     │    │  @healthcare20bot│
│                 │    │   (Free Tier)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🐳 Step 1: Deploy Backend to Render

### 1.1 Prepare Your Repository
First, make sure all files are committed to Git:

```bash
git add .
git commit -m "Add production deployment files"
git push origin main
```

### 1.2 Deploy on Render

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Connect your GitHub repository**
3. **Create a new Web Service**:
   - **Repository**: Select your healthChatbot repository
   - **Name**: `healthcare-chatbot` 
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Plan**: `Free` 🆓

4. **Set Environment Variables** in Render dashboard:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   RASA_TELEMETRY_ENABLED=false
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   PORT=5005
   ```

5. **Deploy**! Render will:
   - Build your Docker image
   - Train your Rasa model
   - Start both action server and Rasa core
   - Provide you with a URL like: `https://healthcare-chatbot-latest.onrender.com`

### 1.3 Verify Backend Deployment

Once deployed, test your backend:

```bash
# Test status endpoint
curl https://healthcare-chatbot-latest.onrender.com/status

# Test REST webhook
curl -X POST https://healthcare-chatbot-latest.onrender.com/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"Hello"}'
```

---

## 🌐 Step 2: Deploy Frontend to Netlify

### 2.1 Deploy on Netlify

1. **Go to [Netlify.com](https://netlify.com)** and sign up/login
2. **Create new site from Git**:
   - **Connect to Git provider**: GitHub
   - **Pick a repository**: Your healthChatbot repo
   - **Branch**: `main`
   - **Build command**: Leave empty (static deployment)
   - **Publish directory**: `.` (root directory)

3. **Deploy site**! Netlify will:
   - Deploy your `index.html` 
   - Configure redirects and headers
   - Provide you with a URL like: `https://healthcare-assistant-ai.netlify.app`

### 2.2 Update Backend URL (Optional)

If your Render URL is different from the default, update the frontend:

1. Edit `index.html` line 339:
   ```javascript
   RASA_URL: window.location.hostname === 'localhost' 
       ? 'http://localhost:5005'
       : 'https://YOUR-ACTUAL-RENDER-URL.onrender.com',
   ```

2. Commit and push - Netlify will auto-deploy!

---

## 📱 Step 3: Connect Telegram Bot

### 3.1 Set Webhook

Use the production webhook script:

```bash
# Set environment variables (or use command line args)
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
export RENDER_BACKEND_URL="https://healthcare-chatbot-latest.onrender.com"

# Set webhook
python set_webhook_production.py set

# Check webhook status
python set_webhook_production.py info
```

### 3.2 Test Your Telegram Bot

1. **Open Telegram** and search for `@healthcare20bot`
2. **Send `/start`** to begin
3. **Test multilingual features**:
   - `Hello` (English)
   - `मलेरिया के बारे में बताएं` (Hindi)  
   - `What are dengue symptoms?` (English)
   - `डेंगू के लक्षण क्या हैं?` (Hindi)

---

## ✅ Step 4: Verify Complete Deployment

### 4.1 Test All Components

**🌐 Frontend (Netlify)**:
- Visit your Netlify URL
- Test the web chat interface
- Verify connection status shows "Online"

**🤖 Backend (Render)**:
- Check Render dashboard for deployment status
- Monitor logs for any errors
- Test API endpoints

**📱 Telegram**:
- Send various health-related questions
- Test multilingual responses
- Verify bot responds correctly

### 4.2 Performance Check

**Expected Response Times**:
- Web interface: 1-3 seconds
- Telegram bot: 2-5 seconds  
- Translation queries: 3-7 seconds

**Memory Usage**:
- Render free tier: 512MB (should be sufficient)
- Your app typically uses: 300-400MB

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 🚨 Backend Issues

**1. "Application failed to respond"**
```bash
# Check Render logs in dashboard
# Usually means model training failed or action server crashed
# Solution: Check environment variables are set correctly
```

**2. "Action server connection failed"**
```bash
# The startup script starts both services
# If it fails, check start_production.sh logs in Render
# Solution: Increase startup timeout in Render settings
```

#### 🌐 Frontend Issues

**1. "Cannot connect to backend"**
```bash
# Frontend shows "Offline" status
# Check if backend URL in index.html is correct
# Test backend directly: curl YOUR_RENDER_URL/status
```

**2. "CORS errors"**
```bash
# Backend should start with --cors "*"
# Check Render logs to ensure this flag is used
```

#### 📱 Telegram Issues

**1. "Bot doesn't respond"**
```bash
# Check webhook status
python set_webhook_production.py info

# Common fix: Delete and reset webhook
python set_webhook_production.py delete
python set_webhook_production.py set
```

**2. "Webhook URL invalid"**
```bash
# Ensure your Render URL is HTTPS (not HTTP)
# URL should end with /webhooks/telegram/webhook
# Example: https://your-app.onrender.com/webhooks/telegram/webhook
```

### 🔍 Debug Commands

```bash
# Check backend health
curl https://your-render-url.onrender.com/status

# Test REST API
curl -X POST https://your-render-url.onrender.com/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"test","message":"Hello"}'

# Check Telegram webhook
python set_webhook_production.py info

# Test Telegram directly
curl https://api.telegram.org/bot<TOKEN>/getMe
```

---

## 💰 Cost Breakdown

### ✅ **FREE TIER LIMITS**

**Render (Free Tier)**:
- ✅ 750 hours/month (sufficient for 24/7)
- ✅ 512MB RAM
- ✅ Automatic deploys
- ❌ Sleeps after 15min inactivity (spins up in ~30 seconds)

**Netlify (Free Tier)**:
- ✅ 100GB bandwidth/month
- ✅ Unlimited personal projects
- ✅ HTTPS included
- ✅ CDN worldwide

**Total Cost**: **$0/month** 🎉

---

## 🚀 Going Live Checklist

- [ ] ✅ Backend deployed on Render
- [ ] ✅ Frontend deployed on Netlify  
- [ ] ✅ Telegram webhook configured
- [ ] ✅ All environment variables set
- [ ] ✅ Health checks passing
- [ ] ✅ Multilingual functionality tested
- [ ] ✅ Error handling verified
- [ ] ✅ Performance acceptable

---

## 🔐 Production Security Notes

### Environment Variables
Your sensitive data is now properly secured:
- ✅ **GROQ_API_KEY**: Hidden in Render environment
- ✅ **TELEGRAM_BOT_TOKEN**: Not exposed in code
- ✅ **No secrets in Git repository**

### Additional Security
- ✅ **HTTPS everywhere** (enforced by Render/Netlify)
- ✅ **CORS properly configured**
- ✅ **CSP headers** set via Netlify
- ✅ **No inline scripts** in production

---

## 📈 Monitoring & Maintenance

### Daily Checks
- Monitor Render app status
- Check Telegram bot responsiveness
- Review error logs if issues arise

### Weekly Tasks
- Review Render resource usage
- Test new medical queries
- Verify translation quality

### Monthly Tasks
- Update dependencies if needed
- Review and update medical database
- Check for Rasa/Groq API updates

---

## 🎯 Success! Your URLs

After successful deployment, you'll have:

- 🌐 **Frontend**: https://your-app-name.netlify.app
- 🤖 **Backend**: https://healthcare-chatbot-latest.onrender.com
- 📱 **Telegram**: @healthcare20bot

**Your healthcare chatbot is now LIVE and accessible worldwide!** 🌍🏥

---

## 📞 Support

If you need help:
1. Check the troubleshooting section above
2. Review Render/Netlify logs
3. Test individual components separately
4. Verify all environment variables are set

**Happy deployment!** 🚀
