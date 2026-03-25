import asyncio
import os
import json
import time
from playwright.async_api import async_playwright
from core.logger import get_logger

print("DEBUG: MessagingAgent file loaded from: " + __file__)
logger = get_logger("MessagingAgent")

# Robust selectors for WhatsApp Web (updated for 2026 UI)
SELECTOR_LOGGED_IN = 'div[role="textbox"][data-tab="3"], p.selectable-text[data-lexical-editor="true"], div[contenteditable="true"][data-tab="3"]'
SELECTOR_QR_CODE = 'canvas[aria-label="Scan me!"], div[data-ref]'
SELECTOR_UNREAD_BADGE = 'span[aria-label*="unread message"], span[aria-label*="unread"], span[aria-label*="notification"], span[aria-label*="silenced"]'
SELECTOR_CHAT_ROW = 'div[role="listitem"], div[role="row"]'
SELECTOR_MSG_INPUT = 'div[role="textbox"][data-tab="10"], div[contenteditable="true"][data-tab="10"], div[title="Type a message"]'


class MessagingAgent:
    """
    JARVIS 2.0 Messaging Agent.
    Uses Playwright with a persistent browser context for reliability.
    """
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.user_data_dir = os.path.join(os.getcwd(), "config", "whatsapp_user_profile")
        self.is_running = False
        logger.info(f"Messaging Agent initialized (Persistent Context mode). Path: {self.user_data_dir}")

    async def _get_persistent_context(self, p, headless=True):
        """Launches a persistent browser context with anti-detection."""
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=headless,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="Asia/Kolkata",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
            )
            return context
        except Exception as e:
            logger.error(f"Failed to launch persistent context: {e}")
            return None

    async def _wait_for_whatsapp_load(self, page, max_attempts=12, interval=5000):
        """Waits for WhatsApp Web to fully load. Returns True if logged in."""
        for attempt in range(max_attempts):
            logger.info(f"Waiting for WhatsApp Web to load (attempt {attempt + 1}/{max_attempts})...")
            try:
                await page.wait_for_selector(SELECTOR_LOGGED_IN, timeout=interval)
                logger.info("WhatsApp Web loaded successfully.")
                return True
            except:
                # Check if QR code appeared (session expired)
                if await page.query_selector(SELECTOR_QR_CODE):
                    logger.warning("WhatsApp session expired - QR code detected.")
                    return False
        return None  # Timed out without QR or login

    async def _extract_unread_chats(self, page):
        """Extracts unread chat details using JavaScript for maximum reliability."""
        # The DOM dump confirmed both badges have aria-label containing 'unread message'
        chats = await page.evaluate("""() => {
            const results = [];
            // Find all badge spans that have aria-label with 'unread'
            const badges = document.querySelectorAll('span[aria-label*="unread message"]');
            
            for (const badge of badges) {
                const unreadCount = badge.textContent.trim();
                if (!unreadCount) continue;
                
                // Walk up to the chat row
                let row = badge;
                for (let i = 0; i < 20; i++) {
                    row = row.parentElement;
                    if (!row) break;
                    if (row.getAttribute('role') === 'row' || row.getAttribute('role') === 'listitem') break;
                }
                if (!row) continue;
                
                // Sender name
                const senderEl = row.querySelector('span[title]');
                const sender = senderEl ? senderEl.getAttribute('title') : 'Unknown';
                
                // Message preview — first line, max 80 chars
                const previewSpans = row.querySelectorAll('span[dir="ltr"]');
                let preview = 'Media/No text';
                for (const ps of previewSpans) {
                    const t = ps.textContent.trim();
                    if (t && t !== sender && t.length > 1) {
                        preview = t.split('\\n')[0].substring(0, 80);
                        break;
                    }
                }
                
                results.push({ sender: sender, preview: preview, unread_count: unreadCount });
            }
            return results;
        }""")

        logger.info(f"JS Scanner found {len(chats)} unread chats: {chats}")
        return chats

    async def monitor(self, telegram_service=None, presence_callback=None):
        async with async_playwright() as p:
            self.is_running = True
            context = await self._get_persistent_context(p, headless=True)
            if not context:
                logger.error("Could not start WhatsApp Monitor.")
                return

            page = await context.new_page()
            await page.goto("https://web.whatsapp.com")

            while self.is_running:
                try:
                    logger.info("WhatsApp Monitor: Checking for unread messages...")

                    load_status = await self._wait_for_whatsapp_load(page, max_attempts=3, interval=10000)
                    if load_status is False:
                        logger.warning("WhatsApp NOT LOGGED IN.")
                        if telegram_service:
                            await telegram_service.send_alert("⚠️ WhatsApp requires login. Please run the setup to scan the QR code.")
                        await asyncio.sleep(self.check_interval)
                        continue
                    elif load_status is None:
                        logger.warning("WhatsApp page not ready. Will retry next cycle.")
                        await asyncio.sleep(self.check_interval)
                        continue

                    chats = await self._extract_unread_chats(page)
                    if chats:
                        logger.info(f"Detected {len(chats)} unread chats.")
                        for chat in chats:
                            logger.info(f"New Message from {chat['sender']}: {chat['preview']}")
                            if telegram_service and presence_callback:
                                if presence_callback() == "Away":
                                    await telegram_service.send_alert(
                                        f"Forwarded from {chat['sender']}: {chat['preview']}"
                                    )

                except Exception as e:
                    logger.error(f"WhatsApp Monitor Error: {e}")

                await asyncio.sleep(self.check_interval)

            await context.close()

    async def send_message(self, contact_name, message_text):
        """Sends a WhatsApp message via persistent context."""
        async with async_playwright() as p:
            context = await self._get_persistent_context(p, headless=True)
            if not context: return False
            page = await context.new_page()
            try:
                await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=30000)
                logger.info(f"Messaging Agent: Sending message to {contact_name}...")

                load_status = await self._wait_for_whatsapp_load(page)
                if not load_status:
                    logger.error("WhatsApp not ready for sending.")
                    return False

                # Click the search box and type the contact name
                search_box = await page.wait_for_selector(SELECTOR_LOGGED_IN, timeout=5000)
                await search_box.click()
                await search_box.fill(contact_name)
                await page.keyboard.press("Enter")

                await asyncio.sleep(2)

                msg_box = await page.wait_for_selector(SELECTOR_MSG_INPUT, timeout=10000)
                await msg_box.fill(message_text)
                await page.keyboard.press("Enter")

                await asyncio.sleep(2)
                logger.info(f"Message sent to {contact_name}.")
                return True
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                return False
            finally:
                await context.close()

    async def check_whatsapp_messages(self):
        """Perform a one-time check for unread messages and return a summary."""
        logger.info("One-time WhatsApp check initiated...")
        async with async_playwright() as p:
            context = await self._get_persistent_context(p, headless=True)
            if not context:
                return "I couldn't initialize the browser context, Sir."

            page = await context.new_page()
            try:
                await page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=30000)

                load_status = await self._wait_for_whatsapp_load(page)
                if load_status is False:
                    return "WhatsApp is not logged in, Sir. Please scan the QR code using the setup utility."
                elif load_status is None:
                    # Save debug screenshot
                    debug_path = os.path.join(os.getcwd(), "whatsapp_debug_state.png")
                    await page.screenshot(path=debug_path)
                    logger.error(f"WhatsApp failed to load. Debug screenshot saved to {debug_path}")
                    return "WhatsApp Web is taking too long to load, Sir. Please try again in a moment."

                # Scroll the chat list to ensure all rows are rendered
                await page.evaluate("""() => {
                    const chatList = document.querySelector('div[aria-label="Chat list"]') || 
                                     document.querySelector('[data-tab="3"]');
                    if (chatList) {
                        const parent = chatList.closest('[role="region"]') || chatList.parentElement;
                        if (parent) parent.scrollTop = parent.scrollHeight;
                    }
                }""")
                await asyncio.sleep(1)  # Let it render
                # Scroll back to top
                await page.evaluate("""() => {
                    const chatList = document.querySelector('div[aria-label="Chat list"]') || 
                                     document.querySelector('[data-tab="3"]');
                    if (chatList) {
                        const parent = chatList.closest('[role="region"]') || chatList.parentElement;
                        if (parent) parent.scrollTop = 0;
                    }
                }""")
                await asyncio.sleep(0.5)

                # Save debug screenshot at scan time
                debug_path = os.path.join(os.getcwd(), "whatsapp_scan_state.png")
                await page.screenshot(path=debug_path)
                logger.info(f"Scan-time screenshot saved to {debug_path}")

                chats = await self._extract_unread_chats(page)

                if not chats:
                    return "You have no unread messages at the moment, Sir."

                summary = f"Sir, you have {len(chats)} unread conversations:\n"
                for chat in chats:
                    summary += f"- {chat['sender']} ({chat['unread_count']} new): {chat['preview']}\n"
                return summary
            except Exception as e:
                logger.error(f"Error checking messages: {e}")
                return "I encountered an error while scanning your inbox, Sir."
            finally:
                await context.close()

    def execute_task(self, task_text: str):
        """Sync wrapper to parse and execute a WhatsApp task."""
        logger.info(f"MessagingAgent: Executing task '{task_text}'")
        if "send whatsapp to" in task_text.lower():
            try:
                # Format: "send whatsapp to Name: Message"
                parts = task_text.split(":", 1)
                contact = parts[0].lower().replace("send whatsapp to", "").strip()
                message = parts[1].strip()
                
                # Execute async
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.run_coroutine_threadsafe(self.send_message(contact, message), loop)
                except RuntimeError:
                    asyncio.run(self.send_message(contact, message))
                return True
            except Exception as e:
                logger.error(f"Failed to parse task: {e}")
        return False
