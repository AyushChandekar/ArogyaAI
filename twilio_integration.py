"""
Twilio Integration for ArogyaAI
Handles WhatsApp and SMS messages using Twilio API
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TwilioHandler:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.rasa_url = os.getenv('RASA_SERVER_URL', 'http://localhost:5005/webhooks/rest/webhook')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing Twilio credentials in environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
        logger.info("Twilio client initialized successfully")
    
    def handle_incoming_message(self, request_data: Dict[str, Any]) -> str:
        """
        Handle incoming WhatsApp or SMS message
        Returns TwiML response as string
        """
        try:
            # Extract message details
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            message_body = request_data.get('Body', '').strip()
            message_type = self._determine_message_type(from_number, to_number)
            
            logger.info(f"Received {message_type} from {from_number}: {message_body}")
            
            if not message_body:
                response_text = "Hello! I'm ArogyaAI, your health assistant. How can I help you today?"
            else:
                # Get response from chatbot
                response_text = self.get_chatbot_response(message_body, from_number)
            
            # Create TwiML response
            twiml_response = MessagingResponse()
            twiml_response.message(response_text)
            
            logger.info(f"Sent {message_type} response to {from_number}: {response_text[:100]}...")
            
            return str(twiml_response)
            
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
            # Return error response
            twiml_response = MessagingResponse()
            twiml_response.message(
                "Sorry, I'm experiencing technical difficulties. Please try again later."
            )
            return str(twiml_response)
    
    def get_chatbot_response(self, message: str, user_id: str) -> str:
        """Get response from the chatbot system"""
        try:
            # Clean user_id for use as sender
            sender_id = user_id.replace('+', '').replace(':', '_').replace('whatsapp_', 'wa_')
            
            # Try to get response from FastAPI backend first
            backend_url = "http://localhost:8000/api/query"
            payload = {
                "query": message,
                "user_id": f"twilio_{sender_id}"
            }
            
            try:
                response = requests.post(backend_url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    chatbot_response = data.get('response', 'No response received.')
                    
                    # Truncate response if too long (Twilio has message limits)
                    if len(chatbot_response) > 1500:
                        chatbot_response = chatbot_response[:1500] + "... [truncated]"
                    
                    return chatbot_response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Backend API error: {e}, trying Rasa directly")
            
            # Fallback to direct Rasa integration
            rasa_payload = {
                "sender": f"twilio_{sender_id}",
                "message": message
            }
            
            rasa_response = requests.post(self.rasa_url, json=rasa_payload, timeout=10)
            
            if rasa_response.status_code == 200:
                rasa_data = rasa_response.json()
                if rasa_data and len(rasa_data) > 0:
                    bot_messages = []
                    for msg in rasa_data:
                        if msg.get('text'):
                            bot_messages.append(msg.get('text'))
                    
                    if bot_messages:
                        response_text = '\n\n'.join(bot_messages)
                        # Truncate if too long
                        if len(response_text) > 1500:
                            response_text = response_text[:1500] + "... [truncated]"
                        return response_text
            
            # Final fallback with welcome message
            return self._get_welcome_message()
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return (
                "I'm having trouble processing your request right now. "
                "Please try again in a few moments."
            )
    
    def _determine_message_type(self, from_number: str, to_number: str) -> str:
        """Determine if message is WhatsApp or SMS"""
        if from_number.startswith('whatsapp:') or to_number.startswith('whatsapp:'):
            return 'WhatsApp'
        else:
            return 'SMS'
    
    def _get_welcome_message(self) -> str:
        """Get welcome message for new users"""
        return (
            "🏥 Welcome to ArogyaAI!\n\n"
            "I'm your intelligent health assistant. I can help you with:\n"
            "• Disease information\n"
            "• Symptoms and treatments\n"
            "• Health guidance\n\n"
            "Just ask me about any health concern!"
        )
    
    def send_message(self, to_number: str, message: str, message_type: str = 'sms') -> bool:
        """
        Send a message via Twilio (SMS or WhatsApp)
        
        Args:
            to_number: Recipient phone number
            message: Message content
            message_type: 'sms' or 'whatsapp'
        
        Returns:
            bool: True if message sent successfully
        """
        try:
            # Format phone numbers for WhatsApp
            if message_type.lower() == 'whatsapp':
                if not to_number.startswith('whatsapp:'):
                    to_number = f'whatsapp:{to_number}'
                from_number = f'whatsapp:{self.phone_number}'
            else:
                from_number = self.phone_number
            
            # Send message
            message_instance = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"Message sent successfully via {message_type}: {message_instance.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending {message_type} message: {e}")
            return False
    
    def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            dict: Message status information or None if error
        """
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'sid': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return None
    
    def setup_webhooks(self, webhook_base_url: str) -> Dict[str, bool]:
        """
        Setup webhooks for incoming messages
        Note: This is typically done through Twilio Console, but can be automated
        
        Args:
            webhook_base_url: Base URL for webhooks (e.g., https://your-domain.ngrok.io)
            
        Returns:
            dict: Status of webhook setup
        """
        results = {
            'sms_webhook': False,
            'whatsapp_webhook': False
        }
        
        try:
            # This would typically require additional Twilio API calls
            # For now, just log the URLs that should be configured
            sms_webhook_url = f"{webhook_base_url}/sms"
            whatsapp_webhook_url = f"{webhook_base_url}/whatsapp"
            
            logger.info(f"Configure SMS webhook URL: {sms_webhook_url}")
            logger.info(f"Configure WhatsApp webhook URL: {whatsapp_webhook_url}")
            
            # In a production environment, you would use Twilio's API to set these
            # For now, we'll return True assuming manual configuration
            results['sms_webhook'] = True
            results['whatsapp_webhook'] = True
            
        except Exception as e:
            logger.error(f"Error setting up webhooks: {e}")
        
        return results

def create_twilio_handler():
    """Create and return a TwilioHandler instance"""
    return TwilioHandler()

if __name__ == "__main__":
    # For testing purposes
    handler = create_twilio_handler()
    print(f"Twilio handler initialized")
    print(f"Account SID: {handler.account_sid}")
    print(f"Phone number: {handler.phone_number}")
    
    # Test sending a message (uncomment to test)
    # test_number = "+1234567890"  # Replace with your test number
    # success = handler.send_message(test_number, "Test message from ArogyaAI!", "sms")
    # print(f"Test message sent: {success}")