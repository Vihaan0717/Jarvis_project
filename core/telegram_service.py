import asyncio
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config.system_config import JarvisConfig

# Silence noisy network stack traces from python-telegram-bot
logging.getLogger("telegram.ext.Updater").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("TelegramService")

class TelegramService:
    def __init__(self, orchestrator=None):
        self.token = JarvisConfig.TELEGRAM_TOKEN
        try:
            self.authorized_chat_id = int(JarvisConfig.AUTHORIZED_CHAT_ID) if JarvisConfig.AUTHORIZED_CHAT_ID and JarvisConfig.AUTHORIZED_CHAT_ID != "your_id_here" else None
        except ValueError:
            logger.error(f"Invalid AUTHORIZED_CHAT_ID in config: {JarvisConfig.AUTHORIZED_CHAT_ID}. Expected an integer.")
            self.authorized_chat_id = None
        
        self.orchestrator = orchestrator
        self.application = None
        self.auth_response_event = asyncio.Event()
        self.last_auth_result = None

    async def start(self):
        if not self.token or self.token == "we_will_add_this_later":
            logger.warning("Telegram Bot Token is missing.")
            return

        try:
            self.application = ApplicationBuilder().token(self.token).build()
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("approve", self._approve_command))
            self.application.add_handler(CommandHandler("deny", self._deny_command))
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))
            self.application.add_handler(CallbackQueryHandler(self._button_callback))

            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Telegram Bot is online.")
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot: {e}")

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"Hello! Your Telegram Chat ID is: {chat_id}")
        if self.authorized_chat_id:
            if chat_id != self.authorized_chat_id:
                logger.warning(f"Unauthorized access attempt from Chat ID: {chat_id}")
                await update.message.reply_text("⛔ Access Denied.")
            else:
                await update.message.reply_text("✅ Identity Verified.")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if self.authorized_chat_id and chat_id != self.authorized_chat_id:
            logger.info(f"Ignoring message from unauthorized ID: {chat_id}")
            return
        
        user_input = update.message.text
        
        # FEATURE 4: Check if this is a reply to a forwarded WhatsApp message
        if update.message.reply_to_message and "Forwarded from" in update.message.reply_to_message.text:
            # Extract contact name from the forwarded header
            import re
            match = re.search(r"Forwarded from (.*?):", update.message.reply_to_message.text)
            if match:
                contact_name = match.group(1)
                logger.info(f"Telegram Bridge: Replying to WhatsApp contact {contact_name}")
                if self.orchestrator:
                    # Route to Action Engine / Messaging Agent
                    await self.orchestrator.hands.send_whatsapp_message(contact_name, user_input)
                    await update.message.reply_text(f"✅ Reply sent to {contact_name} via WhatsApp.")
                return

        if self.orchestrator:
            response = await self.orchestrator.process_telegram_command(user_input)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Orchestrator not initialized.")

    async def _approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Permission Approved.")

    async def _deny_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Permission Denied.")

    async def request_authorization(self, photo_path: str):
        if not self.application or not self.authorized_chat_id: return False
        self.auth_response_event.clear()
        keyboard = [[InlineKeyboardButton("✅ Approve", callback_data='auth_approve'),
                     InlineKeyboardButton("❌ Deny", callback_data='auth_deny')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open(photo_path, 'rb') as photo:
                await self.application.bot.send_photo(chat_id=self.authorized_chat_id, photo=photo, 
                                                     caption="🛡️ SECURITY ALERT", reply_markup=reply_markup)
            await asyncio.wait_for(self.auth_response_event.wait(), timeout=60.0)
            return self.last_auth_result
        except asyncio.TimeoutError:
            logger.warning("Telegram authorization request TIMED OUT (60s).")
            return False
        except Exception as e:
            logger.error(f"Failed to send authorization request to Telegram: {type(e).__name__} - {e}")
            return False

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == 'auth_approve':
            self.last_auth_result = True
            await query.edit_message_caption(caption="✅ Access GRANTED.")
        elif query.data == 'auth_deny':
            self.last_auth_result = False
            await query.edit_message_caption(caption="❌ Access DENIED.")
        self.auth_response_event.set()

    async def send_alert(self, message: str):
        if not self.application:
            logger.warning("Cannot send Telegram alert: Application not initialized.")
            return
        if not self.authorized_chat_id:
            logger.warning("Cannot send Telegram alert: AUTHORIZED_CHAT_ID is missing or invalid.")
            return

        try:
            logger.info(f"Sending Telegram alert to {self.authorized_chat_id}: {message[:50]}...")
            await self.application.bot.send_message(chat_id=self.authorized_chat_id, text=f"🚀 ALERT: {message}")
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}", exc_info=True)

    async def stop(self):
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
