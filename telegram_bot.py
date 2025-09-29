"""
Telegram Bot Integration for ArogyaAI
Handles Telegram webhook messages and integrates with the chatbot system
"""

import os
import logging
import requests
from typing import Dict, Any
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotHandler:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot_username = os.getenv('TELEGRAM_BOT_USERNAME')
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.rasa_url = os.getenv('RASA_SERVER_URL', 'http://localhost:5005/webhooks/rest/webhook')
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.bot = Bot(token=self.token)
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🏥 Welcome to ArogyaAI! 🤖\n\n"
            "I'm your intelligent health assistant. I can help you with:\n"
            "• Disease information and symptoms\n"
            "• Health-related queries\n"
            "• Medical guidance and advice\n\n"
            "Just send me a message describing your health concern or ask about any disease!\n\n"
            "Type /help for more information."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🤖 ArogyaAI Help\n\n"
            "Available commands:\n"
            "• /start - Welcome message\n"
            "• /help - Show this help message\n\n"
            "You can ask me about:\n"
            "• Symptoms of diseases\n"
            "• Treatment information\n"
            "• Health conditions\n"
            "• Medical advice\n\n"
            "Example questions:\n"
            "• \"What are the symptoms of diabetes?\"\n"
            "• \"How is hypertension treated?\"\n"
            "• \"Tell me about heart disease\"\n\n"
            "I support multiple languages! 🌍"
        )
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        try:
            user_message = update.message.text
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or f"user_{user_id}"
            
            logger.info(f"Received message from {username} ({user_id}): {user_message}")
            
            # Send typing action
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Get response from chatbot
            response = await self.get_chatbot_response(user_message, user_id)
            
            # Send response back to user
            await update.message.reply_text(response)
            
            logger.info(f"Sent response to {username}: {response[:100]}...")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_message = (
                "😔 Sorry, I encountered an error while processing your request. "
                "Please try again later or contact support if the problem persists."
            )
            await update.message.reply_text(error_message)
    
    async def get_chatbot_response(self, message: str, user_id: str) -> str:
        """Get response from the chatbot system"""
        try:
            # Try to get response from FastAPI backend first
            backend_url = os.getenv('BACKEND_API_URL', 'https://arogyaai-yr7b.onrender.com/api/query')
            payload = {
                "query": message,
                "user_id": f"telegram_{user_id}"
            }
            
            try:
                response = requests.post(backend_url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('response', 'No response received from backend.')
            except requests.exceptions.RequestException as e:
                logger.warning(f"Backend API error: {e}, trying Rasa directly")
            
            # Fallback to direct Rasa integration
            rasa_payload = {
                "sender": f"telegram_{user_id}",
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
                        return '\n\n'.join(bot_messages)
            
            # Final fallback
            return (
                "I'm currently experiencing some technical difficulties. "
                "Please try again in a few moments or contact support if the issue persists."
            )
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return (
                "I apologize, but I'm having trouble processing your request right now. "
                "Please try again later."
            )
    
    async def set_webhook(self, webhook_url: str):
        """Set webhook URL for the bot"""
        try:
            webhook_endpoint = f"{webhook_url}/telegram"
            await self.bot.set_webhook(url=webhook_endpoint)
            logger.info(f"Webhook set to: {webhook_endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def remove_webhook(self):
        """Remove webhook"""
        try:
            await self.bot.delete_webhook()
            logger.info("Webhook removed")
            return True
        except Exception as e:
            logger.error(f"Error removing webhook: {e}")
            return False
    
    def get_application(self):
        """Get the telegram application instance"""
        return self.application

def create_telegram_handler():
    """Create and return a TelegramBotHandler instance"""
    return TelegramBotHandler()

if __name__ == "__main__":
    # For testing purposes
    handler = create_telegram_handler()
    print(f"Telegram bot initialized with token: {handler.token[:10]}...")
    print(f"Bot username: {handler.bot_username}")