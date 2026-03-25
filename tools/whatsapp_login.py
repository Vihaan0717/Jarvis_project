import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.async_api import async_playwright
from core.logger import get_logger

logger = get_logger("WhatsAppSetup")

async def run_setup():
    user_data_dir = os.path.join(os.getcwd(), "config", "whatsapp_user_profile")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        
    print(f"\n--- WhatsApp Web Setup ---")
    print(f"Profile Directory: {user_data_dir}")
    print(f"Launching browser (headful) for initial login...")
    print(f"Please scan the QR code and wait for chats to load.")
    print(f"Once logged in, you can close the browser window.\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        await page.goto("https://web.whatsapp.com")
        
        print("Waiting for you to scan the QR code and log in...")
        print("Press Ctrl+C in this terminal when you are finished and want to close the browser.")
        
        try:
            # Keep the browser open until the user closes it manually or kills the script
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nClosing setup...")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_setup())
