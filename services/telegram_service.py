import asyncio
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config.system_config import JarvisConfig

logger = logging.getLogger("TelegramService")

class TelegramService:
    def __init__(self, orchestrator=None):
        self.token = JarvisConfig.TELEGRAM_TOKEN
        self.authorized_chat_id = JarvisConfig.AUTHORIZED_CHAT_ID
        self.orchestrator = orchestrator
        self.application = None
        self.auth_response_event = asyncio.Event()
        self.last_auth_result = None

    async def start(self):
        """Starts the Telegram bot polling in the background."""
        if not self.token or self.token == "we_will_add_this_later":
            logger.warning("Telegram Bot Token is missing. Bot will not start.")
            return

        try:
            self.application = ApplicationBuilder().token(self.token).build()

            # Command Handlers
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("approve", self._approve_command))
            self.application.add_handler(CommandHandler("deny", self._deny_command))
            
            # Message Handler (Chat with JARVIS)
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))
            
            # Button Callback Handler
            self.application.add_handler(CallbackQueryHandler(self._button_callback))

            logger.info("Telegram Bot is starting...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Telegram Bot is online.")
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot: {e}")

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        
        # Always show ID to help with setup
        await update.message.reply_text(f"Hello! Your Telegram Chat ID is: {chat_id}")
        
        if self.authorized_chat_id and self.authorized_chat_id != "your_id_here":
            if chat_id != str(self.authorized_chat_id):
                await update.message.reply_text("⛔ Access Denied. This ID is not in the authorized whitelist.")
                logger.warning(f"Unauthorized access attempt from Chat ID: {chat_id}")
                return
            else:
                await update.message.reply_text("✅ Identity Verified. I am standing by for your commands, Boss.")
        else:
            await update.message.reply_text("⚠️ Security Note: No authorized Chat ID is set in .env yet. Please provide this ID to the developer.")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        if self.authorized_chat_id and chat_id != str(self.authorized_chat_id):
            return

        user_input = update.message.text
        logger.info(f"Telegram Message received: {user_input}")

        if self.orchestrator:
            # Route to orchestrator (Assuming it has a way to process text and return it)
            # This is a placeholder for actual integration. 
            # In a real scenario, we might want to run this in a thread or await it if the orchestrator is async.
            response = await self.orchestrator.process_telegram_command(user_input)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("I am connected, but my brain (Orchestrator) is not initialized properly.")

    async def _approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Placeholder for permission logic
        await update.message.reply_text("Permission Approved.")

    async def _deny_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Placeholder for permission logic
        await update.message.reply_text("Permission Denied.")

    async def request_authorization(self, photo_path: str):
        """Sends a photo to the user with Approve/Deny buttons and waits for response."""
        if not self.application or not self.authorized_chat_id:
            logger.error("Telegram Service not fully initialized. Cannot request auth.")
            return False

        self.auth_response_event.clear()
        self.last_auth_result = None

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data='auth_approve'),
                InlineKeyboardButton("❌ Deny", callback_data='auth_deny'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            with open(photo_path, 'rb') as photo:
                await self.application.bot.send_photo(
                    chat_id=self.authorized_chat_id,
                    photo=photo,
                    caption="🛡️ SECURITY ALERT: Unrecognized face detected. Do you authorize access?",
                    reply_markup=reply_markup
                )
            
            # Wait for user input (60 second timeout)
            try:
                await asyncio.wait_for(self.auth_response_event.wait(), timeout=60.0)
                return self.last_auth_result
            except asyncio.TimeoutError:
                logger.warning("Authorization request timed out.")
                await self.application.bot.send_message(
                    chat_id=self.authorized_chat_id,
                    text="⏳ Authorization request timed out. Access denied automatically."
                )
                return False

        except Exception as e:
            logger.error(f"Error sending auth request: {e}")
            return False

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles button clicks for Approve/Deny."""
        query = update.callback_query
        await query.answer()

        if query.data == 'auth_approve':
            self.last_auth_result = True
            await query.edit_message_caption(caption="✅ Access GRANTED by Boss.")
        elif query.data == 'auth_deny':
            self.last_auth_result = False
            await query.edit_message_caption(caption="❌ Access DENIED by Boss.")

        self.auth_response_event.set()

    async def send_alert(self, message: str):
        """Sends a proactive alert to the authorized user."""
        if not self.application or not self.authorized_chat_id:
            return
        
        try:
            await self.application.bot.send_message(chat_id=self.authorized_chat_id, text=f"🚀 ALERT: {message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    async def stop(self):
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
