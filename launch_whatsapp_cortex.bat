@echo off
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME_PATH%" (
    echo Chrome not found in standard locations. 
    echo Please edit this script and set CHROME_PATH manually.
    pause
    exit /b
)

echo Launching Chrome with Remote Debugging on port 9222...
echo You can use this window for WhatsApp. JARVIS will connect to it.
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%CD%\config\whatsapp_user_profile" https://web.whatsapp.com
