@echo off
title JARVIS-X Unified System
cd /d "%~dp0"

echo [SYSTEM] Activating Virtual Environment...
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

echo [SYSTEM] Starting JARVIS-X Master Orchestrator...
python run_jarvis.py

pause
