#!/usr/bin/env python3
"""
Simple, Reliable Telegram Bot for ArogyaAI (Windows-friendly)
This version avoids event loop issues common on Windows.
"""

import asyncio
import sys
import logging
import requests
import time
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# Fix Windows event loop issues
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration - UPDATE THIS WITH YOUR BOT TOKEN
BOT_TOKEN = "INPUT_TOKEN_HERE"  # Your actual token
BACKEND_URL = "https://arogyaai-yr7b.onrender.com/api/query"

class SimpleArogyaBot:
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        
        # Create application
        self.app = Application.builder().token(token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Bot initialized successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = (
            "🏥 **Welcome to ArogyaAI!** 🤖\n\n"
            "I'm your intelligent multilingual health assistant!\n\n"
            "**What I can help with:**\n"
            "• Disease information & symptoms 📋\n"
            "• Treatment guidance 💊\n"
            "• Home remedies 🏠\n"
            "• WHO guidelines 🏛️\n"
            "• Multilingual support 🌍\n\n"
            "**Try asking:**\n"
            "• \"What is diabetes?\"\n"
            "• \"Symptoms of asthma\"\n"
            "• \"मुझे सिरदर्द है\" (Hindi)\n"
            "• \"¿Qué es la hipertensión?\" (Spanish)\n\n"
            "Type /help for more info or /test to check my status!"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
        logger.info(f"Start command sent to user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = (
            "🤖 **ArogyaAI Help Guide**\n\n"
            "**Commands:**\n"
            "• `/start` - Welcome message\n"
            "• `/help` - This help guide\n"
            "• `/test` - Check bot status\n\n"
            "**What I can help with:**\n"
            "• Disease symptoms & information\n"
            "• Treatment recommendations\n"
            "• Prevention tips\n"
            "• Home remedies\n"
            "• Medical guidance\n\n"
            "**Languages I support:** 🌍\n"
            "English, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic, and more!\n\n"
            "**Just ask naturally!**\n"
            "Example: \"Tell me about high blood pressure\""
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command"""
        # Test backend connection
        backend_status = await self.test_backend()
        
        test_msg = (
            f"🔧 **Bot Status Check**\n\n"
            f"✅ Bot is online and responding\n"
            f"✅ Chat ID: `{update.effective_chat.id}`\n"
            f"✅ User ID: `{update.effective_user.id}`\n"
            f"{'✅' if backend_status else '⚠️'} Backend API: {'Connected' if backend_status else 'Disconnected'}\n\n"
            f"**Try asking:** \"What is asthma?\""
        )
        await update.message.reply_text(test_msg, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        try:
            user_msg = update.message.text
            user_id = str(update.effective_user.id)
            username = update.effective_user.username or f"user_{user_id}"
            
            logger.info(f"Message from {username}: {user_msg[:50]}...")
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action="typing"
            )
            
            # Get response
            response = await self.get_health_response(user_msg, user_id)
            
            # Send response (split if too long)
            await self.send_long_message(update, response)
            
            logger.info(f"Response sent to {username}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            error_msg = (
                "😔 Sorry, I encountered an error processing your request.\n\n"
                "🔄 **Quick fixes:**\n"
                "• Try rephrasing your question\n"
                "• Use simpler terms\n"
                "• Try /test to check my status\n\n"
                "The backend server might be starting up. Please try again in a minute!"
            )
            await update.message.reply_text(error_msg)
    
    async def get_health_response(self, message: str, user_id: str) -> str:
        """Get health response from backend or provide fallback"""
        try:
            # Try backend API
            payload = {
                "query": message,
                "user_id": f"telegram_{user_id}"
            }
            
            response = requests.post(
                BACKEND_URL, 
                json=payload, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('response'):
                    bot_response = data['response']
                    
                    # Add language info if translated
                    if data.get('was_translated') and data.get('detected_language', '').lower() != 'english':
                        bot_response = f"🌍 *Language: {data['detected_language']}*\n\n{bot_response}"
                    
                    return bot_response
                else:
                    logger.warning(f"API returned error: {data}")
            else:
                logger.warning(f"API returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning("Backend API timeout")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Backend API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        # Fallback response
        return (
            "🤖 I'm having trouble connecting to my knowledge base right now.\n\n"
            "🔄 **This usually helps:**\n"
            "• Wait 1-2 minutes (server might be starting up)\n"
            "• Try your question again\n"
            "• Use /test to check status\n\n"
            "💡 **For urgent health issues:**\n"
            "• Contact local healthcare providers\n"
            "• Call emergency services: 108 (India)\n\n"
            "I'll be back online shortly! 🏥"
        )
    
    async def send_long_message(self, update: Update, message: str):
        """Send long messages by splitting them if needed"""
        max_length = 4096
        if len(message) <= max_length:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            # Split message into chunks
            parts = []
            current = ""
            
            for line in message.split('\n'):
                if len(current + line + '\n') > max_length:
                    if current:
                        parts.append(current.strip())
                        current = line + '\n'
                    else:
                        # Single line too long, split by words
                        words = line.split(' ')
                        for word in words:
                            if len(current + word + ' ') > max_length:
                                parts.append(current.strip())
                                current = word + ' '
                            else:
                                current += word + ' '
                else:
                    current += line + '\n'
            
            if current:
                parts.append(current.strip())
            
            # Send all parts
            for i, part in enumerate(parts):
                if i > 0:
                    await asyncio.sleep(0.5)  # Small delay between messages
                try:
                    await update.message.reply_text(part, parse_mode='Markdown')
                except:
                    # Fallback without markdown if parsing fails
                    await update.message.reply_text(part)
    
    async def test_backend(self) -> bool:
        """Test if backend is reachable"""
        try:
            response = requests.get(BACKEND_URL.replace('/api/query', '/health'), timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def run(self):
        """Run the bot with proper error handling"""
        logger.info("🚀 Starting ArogyaAI Telegram Bot...")
        logger.info(f"🏥 Backend URL: {BACKEND_URL}")
        logger.info("💬 Bot is ready to receive messages")
        logger.info("\nPress Ctrl+C to stop\n")
        
        try:
            # Use run_polling with proper error handling
            self.app.run_polling(
                drop_pending_updates=True,
                close_loop=False
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            logger.info("Retrying with alternative method...")
            
            # Alternative method using asyncio.run
            try:
                asyncio.run(self._run_async())
            except Exception as e2:
                logger.error(f"Alternative method failed: {e2}")
                raise
    
    async def _run_async(self):
        """Alternative async run method"""
        async with self.app:
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            
            logger.info("Bot is now running with async method...")
            try:
                # Keep running until interrupted
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("Stopping bot...")
            finally:
                await self.app.updater.stop()
                await self.app.stop()

def main():
    """Main function"""
    print("🏥 ArogyaAI Telegram Bot")
    print("=" * 40)
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TOKEN_HERE":
        print("❌ Error: Please set your bot token in BOT_TOKEN variable")
        print("\n📝 How to get a token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot")
        print("3. Follow the instructions")
        print("4. Copy the token and paste it in this script")
        return
    
    try:
        # Test bot token first
        bot = Bot(token=BOT_TOKEN)
        
        async def test_connection():
            try:
                me = await bot.get_me()
                print(f"✅ Bot connected: @{me.username}")
                print(f"🤖 Bot name: {me.first_name}")
                print(f"🆔 Bot ID: {me.id}\n")
                return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False
        
        # Test connection
        if not asyncio.run(test_connection()):
            return
        
        # Create and run bot
        arogyai_bot = SimpleArogyaBot(BOT_TOKEN)
        arogyai_bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your bot token")
        print("2. Make sure you have internet connection")
        print("3. Try running as administrator")

if __name__ == "__main__":
    main()
