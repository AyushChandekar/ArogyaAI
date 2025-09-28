"""
Unified Webhook Server for ArogyaAI
Handles webhooks from Telegram, WhatsApp, and SMS
"""

import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from dotenv import load_dotenv
import json

# Import our integration modules
from telegram_bot import create_telegram_handler
from twilio_integration import create_twilio_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WebhookServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', 5001))
        
        # Initialize handlers
        try:
            self.telegram_handler = create_telegram_handler()
            logger.info("Telegram handler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram handler: {e}")
            self.telegram_handler = None
        
        try:
            self.twilio_handler = create_twilio_handler()
            logger.info("Twilio handler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio handler: {e}")
            self.twilio_handler = None
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for webhooks"""
        
        @self.app.route('/', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'message': 'ArogyaAI Webhook Server is running',
                'endpoints': {
                    'telegram': '/telegram',
                    'whatsapp': '/whatsapp',
                    'sms': '/sms',
                    'health': '/'
                },
                'integrations': {
                    'telegram': self.telegram_handler is not None,
                    'twilio': self.twilio_handler is not None
                }
            })
        
        @self.app.route('/telegram', methods=['POST'])
        def telegram_webhook():
            """Handle Telegram webhook"""
            if not self.telegram_handler:
                logger.error("Telegram handler not available")
                return jsonify({'error': 'Telegram handler not available'}), 500
            
            try:
                # Get JSON data from request
                json_data = request.get_json()
                if not json_data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                logger.info(f"Received Telegram webhook: {json_data}")
                
                # Create Update object and process it
                update = Update.de_json(json_data, self.telegram_handler.bot)
                
                # Process the update asynchronously
                asyncio.create_task(
                    self.telegram_handler.application.process_update(update)
                )
                
                return jsonify({'status': 'ok'})
                
            except Exception as e:
                logger.error(f"Error processing Telegram webhook: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/whatsapp', methods=['POST'])
        def whatsapp_webhook():
            """Handle WhatsApp webhook from Twilio"""
            if not self.twilio_handler:
                logger.error("Twilio handler not available")
                return jsonify({'error': 'Twilio handler not available'}), 500
            
            try:
                # Get form data (Twilio sends form-encoded data)
                form_data = request.form.to_dict()
                logger.info(f"Received WhatsApp webhook: {form_data}")
                
                # Process the message and get TwiML response
                twiml_response = self.twilio_handler.handle_incoming_message(form_data)
                
                # Return TwiML response
                return twiml_response, 200, {'Content-Type': 'text/xml'}
                
            except Exception as e:
                logger.error(f"Error processing WhatsApp webhook: {e}")
                error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I\'m experiencing technical difficulties.</Message></Response>'
                return error_response, 500, {'Content-Type': 'text/xml'}
        
        @self.app.route('/sms', methods=['POST'])
        def sms_webhook():
            """Handle SMS webhook from Twilio"""
            if not self.twilio_handler:
                logger.error("Twilio handler not available")
                return jsonify({'error': 'Twilio handler not available'}), 500
            
            try:
                # Get form data (Twilio sends form-encoded data)
                form_data = request.form.to_dict()
                logger.info(f"Received SMS webhook: {form_data}")
                
                # Process the message and get TwiML response
                twiml_response = self.twilio_handler.handle_incoming_message(form_data)
                
                # Return TwiML response
                return twiml_response, 200, {'Content-Type': 'text/xml'}
                
            except Exception as e:
                logger.error(f"Error processing SMS webhook: {e}")
                error_response = '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, I\'m experiencing technical difficulties.</Message></Response>'
                return error_response, 500, {'Content-Type': 'text/xml'}
        
        @self.app.route('/test', methods=['GET', 'POST'])
        def test_endpoint():
            """Test endpoint for debugging"""
            return jsonify({
                'method': request.method,
                'headers': dict(request.headers),
                'args': dict(request.args),
                'form': dict(request.form) if request.form else None,
                'json': request.get_json() if request.is_json else None
            })
    
    def run(self, host='0.0.0.0', port=None, debug=False):
        """Run the webhook server"""
        if port is None:
            port = self.webhook_port
        
        logger.info(f"Starting ArogyaAI Webhook Server on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  Health: http://{host}:{port}/")
        logger.info(f"  Telegram: http://{host}:{port}/telegram")
        logger.info(f"  WhatsApp: http://{host}:{port}/whatsapp")
        logger.info(f"  SMS: http://{host}:{port}/sms")
        logger.info(f"  Test: http://{host}:{port}/test")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

class AsyncWebhookServer:
    """Alternative async version using FastAPI"""
    def __init__(self):
        try:
            from fastapi import FastAPI, HTTPException, Form
            from fastapi.responses import Response
            import uvicorn
            
            self.app = FastAPI(title="ArogyaAI Webhook Server", version="1.0.0")
            self.webhook_port = int(os.getenv('WEBHOOK_PORT', 5001))
            
            # Initialize handlers
            self.telegram_handler = None
            self.twilio_handler = None
            
            try:
                self.telegram_handler = create_telegram_handler()
                logger.info("Telegram handler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram handler: {e}")
            
            try:
                self.twilio_handler = create_twilio_handler()
                logger.info("Twilio handler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio handler: {e}")
            
            self.setup_routes()
            
        except ImportError:
            logger.error("FastAPI not available, use FlaskWebhookServer instead")
            raise
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def health_check():
            return {
                'status': 'healthy',
                'message': 'ArogyaAI Async Webhook Server is running',
                'integrations': {
                    'telegram': self.telegram_handler is not None,
                    'twilio': self.twilio_handler is not None
                }
            }
        
        @self.app.post("/telegram")
        async def telegram_webhook(update_data: dict):
            if not self.telegram_handler:
                raise HTTPException(status_code=500, detail="Telegram handler not available")
            
            try:
                update = Update.de_json(update_data, self.telegram_handler.bot)
                await self.telegram_handler.application.process_update(update)
                return {'status': 'ok'}
            except Exception as e:
                logger.error(f"Error processing Telegram webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def run_async(self):
        """Run the async webhook server"""
        import uvicorn
        config = uvicorn.Config(
            self.app, 
            host="0.0.0.0", 
            port=self.webhook_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

def create_webhook_server(async_mode=False):
    """Create webhook server instance"""
    if async_mode:
        try:
            return AsyncWebhookServer()
        except ImportError:
            logger.warning("FastAPI not available, falling back to Flask")
            return WebhookServer()
    else:
        return WebhookServer()

if __name__ == "__main__":
    # Check for command line arguments
    import sys
    
    debug_mode = '--debug' in sys.argv
    async_mode = '--async' in sys.argv
    
    try:
        server = create_webhook_server(async_mode=async_mode)
        
        if async_mode and hasattr(server, 'run_async'):
            # Run async server
            asyncio.run(server.run_async())
        else:
            # Run Flask server
            server.run(debug=debug_mode)
            
    except KeyboardInterrupt:
        logger.info("Webhook server stopped by user")
    except Exception as e:
        logger.error(f"Error starting webhook server: {e}")
        sys.exit(1)