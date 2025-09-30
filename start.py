"""
Combined startup script for ArogyaAI - runs both backend and webhooks in one service
Perfect for single-service free tiers like Koyeb
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import asyncio
import logging
from typing import Dict, Any

# Import your existing modules
from backend import app as backend_app
from telegram_bot import create_telegram_handler
from twilio_integration import create_twilio_handler
from telegram import Update

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(
    title="ArogyaAI Combined Service",
    description="Backend API + Telegram/WhatsApp Webhooks",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event to initialize Telegram handler
@app.on_event("startup")
async def startup_event():
    """Initialize async components on startup"""
    await initialize_telegram_handler()

# Shutdown event to cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if telegram_handler and telegram_handler.application:
        await telegram_handler.application.shutdown()

# Initialize handlers
telegram_handler = None
twilio_handler = None

async def initialize_telegram_handler():
    """Initialize Telegram handler with proper async setup"""
    global telegram_handler
    try:
        telegram_handler = create_telegram_handler()
        await telegram_handler.application.initialize()
        logger.info("Telegram handler initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram handler: {e}")
        telegram_handler = None

try:
    twilio_handler = create_twilio_handler()
    logger.info("Twilio handler initialized")
except Exception as e:
    logger.error(f"Failed to initialize Twilio handler: {e}")

# Add backend routes directly instead of mounting
from backend import QueryRequest, QueryResponse, DiseasesResponse
from backend import query as backend_query, get_diseases, health_check as backend_health

# Backend API routes
@app.post("/api/query", response_model=QueryResponse)
async def api_query(request: QueryRequest):
    return await backend_query(request)

@app.get("/api/diseases")
async def api_diseases():
    return await get_diseases()

@app.get("/api/health")
async def api_backend_health():
    return await backend_health()

# Health check endpoint
@app.get("/")
@app.get("/health")
async def health_check():
    """Combined health check"""
    return {
        "status": "healthy",
        "message": "ArogyaAI Combined Service is running",
        "services": {
            "backend_api": "mounted at /api",
            "telegram_webhook": "/telegram",
            "whatsapp_webhook": "/whatsapp",
            "sms_webhook": "/sms"
        },
        "integrations": {
            "telegram": telegram_handler is not None,
            "twilio": twilio_handler is not None
        }
    }

# Telegram webhook - simplified approach
@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook - direct message processing"""
    try:
        json_data = await request.json()
        logger.info(f"Received Telegram webhook: {json_data}")
        
        # Extract message data
        if 'message' not in json_data:
            return {"status": "ok"}  # No message to process
            
        message_data = json_data['message']
        user_id = str(message_data['from']['id'])
        chat_id = message_data['chat']['id']
        text = message_data.get('text', '')
        
        if not text:
            return {"status": "ok"}  # No text to process
            
        # Get response from backend API directly
        try:
            from backend import QueryRequest
            
            # Create request object
            query_request = QueryRequest(query=text, user_id=f'telegram_{user_id}')
            
            # Call backend function directly
            response_result = await backend_query(query_request)
            bot_response = response_result.response
            
            if not bot_response:
                bot_response = "Sorry, I could not process your request."
                
        except Exception as e:
            logger.error(f"Error getting backend response: {e}")
            bot_response = "I'm experiencing technical difficulties. Please try again later."
        
        # Send response back to user via Telegram API
        if telegram_handler and telegram_handler.bot:
            try:
                await telegram_handler.bot.send_message(
                    chat_id=chat_id,
                    text=bot_response
                )
            except Exception as e:
                logger.error(f"Error sending Telegram message: {e}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"status": "error", "message": str(e)}

# WhatsApp webhook
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp webhook from Twilio"""
    if not twilio_handler:
        raise HTTPException(status_code=500, detail="Twilio handler not available")
    
    try:
        # Get form data (Twilio sends form-encoded data)
        form_data = await request.form()
        form_dict = dict(form_data)
        logger.info(f"Received WhatsApp webhook: {form_dict}")
        
        # Process the message and get TwiML response
        twiml_response = twilio_handler.handle_incoming_message(form_dict)
        
        # Return TwiML response
        return Response(content=twiml_response, media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I\'m experiencing technical difficulties.</Message></Response>'
        return Response(content=error_response, status_code=500, media_type="text/xml")

# SMS webhook
@app.post("/sms")
async def sms_webhook(request: Request):
    """Handle SMS webhook from Twilio"""
    if not twilio_handler:
        raise HTTPException(status_code=500, detail="Twilio handler not available")
    
    try:
        # Get form data (Twilio sends form-encoded data)
        form_data = await request.form()
        form_dict = dict(form_data)
        logger.info(f"Received SMS webhook: {form_dict}")
        
        # Process the message and get TwiML response
        twiml_response = twilio_handler.handle_incoming_message(form_dict)
        
        # Return TwiML response
        return Response(content=twiml_response, media_type="text/xml")
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I\'m experiencing technical difficulties.</Message></Response>'
        return Response(content=error_response, status_code=500, media_type="text/xml")

# Test endpoint
@app.get("/test")
@app.post("/test")
async def test_endpoint(request: Request):
    """Test endpoint for debugging"""
    method = request.method
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    
    body = None
    form = None
    
    if method == "POST":
        content_type = headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                body = await request.json()
            except:
                pass
        elif "application/x-www-form-urlencoded" in content_type:
            try:
                form_data = await request.form()
                form = dict(form_data)
            except:
                pass
    
    return {
        "method": method,
        "headers": headers,
        "query_params": query_params,
        "body": body,
        "form": form
    }

if __name__ == "__main__":
    # Get port from environment
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting ArogyaAI Combined Service on {host}:{port}")
    logger.info("📋 Available endpoints:")
    logger.info(f"  Health: http://{host}:{port}/health")
    logger.info(f"  Backend API: http://{host}:{port}/api/*")
    logger.info(f"  Telegram: http://{host}:{port}/telegram")
    logger.info(f"  WhatsApp: http://{host}:{port}/whatsapp")
    logger.info(f"  SMS: http://{host}:{port}/sms")
    logger.info(f"  Test: http://{host}:{port}/test")
    
    uvicorn.run(
        "start:app",
        host=host,
        port=port,
        log_level="info"
    )