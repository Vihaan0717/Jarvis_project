# 🚀 JARVIS Cloud Brain: Render.com Deployment Guide

This guide explains how to deploy the lightweight `render_jarvis.py` system to Render's Free Tier for 24/7 uptime.

## 1. Prerequisites
- A **GitHub** account with this repository pushed.
- A **Render.com** account.
- A **Telegram Bot Token** (from @BotFather).
- Your **Telegram User ID** (get it from @userinfobot).

## 2. Render Deployment Steps
1.  **New Web Service:** Log in to Render and click `New` -> `Web Service`.
2.  **Connect Repo:** Connect your GitHub repository.
3.  **Settings:**
    - **Name:** `jarvis-cloud-brain`
    - **Environment:** `Python 3`
    - **Build Command:** `pip install -r render_requirements.txt`
    - **Start Command:** `gunicorn render_jarvis:app`
4.  **Environment Variables:** Click `Advanced` -> `Add Environment Variable`:
    - `TELEGRAM_TOKEN`: `your_bot_token_here`
    - `MY_USER_ID`: `your_numeric_id_here`
    - `PYTHON_VERSION`: `3.11.0` (Optional but recommended)
5.  **Deploy:** Click `Create Web Service`.

## 3. Keep Awake (24/7 Uptime)
Render's free tier spins down after 15 minutes of inactivity. To keep it awake:
1.  Go to [cron-job.org](https://cron-job.org/).
2.  Create a new Cronjob.
3.  **URL:** `https://your-service-name.onrender.com/`
4.  **Schedule:** Every **14 minutes**.
5.  This will ping the Flask `/` endpoint, preventing the service from sleeping.

## 4. Security
- The bot is hard-coded to ignore any messages not sent by `MY_USER_ID`.
- No heavy libraries (OpenCV, Torch) are included to ensure it stays within Render's 512MB RAM limit.
