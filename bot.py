import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}", flush=True)

app = Flask(__name__)

@app.route('/')
def home():
    return "Nagromtrade Contest Bot is LIVE!"

WELCOME_TEXT = """
🏆 *Nagromtrade Trading Contest Bot* 🏆

Welcome to the Official Nagrom Trade Competition!

💰 Cash Prizes | 📊 Live Leaderboard

Commands:
/start - Show this message
/contest - Contest info & rules
/leaderboard - View live rankings
/register - How to join

🔗 Register here: https://one.exness-track.com/a/nagromtrade

Good luck trader! 📈
"""

CONTEST_TEXT = """
📋 *Contest Rules*

1. Register with Exness via our link
2. Trade and grow your account
3. Top 3 highest profit % win cash!

🏅 Prizes:
1st - $500
2nd - $300
3rd - $100

Contest ends monthly. Trade smart!
"""

LEADERBOARD_TEXT = """
📊 *Live Leaderboard* (Demo)

1. TraderGH_01 - +125%
2. AccraFX - +98%
3. KumasiBull - +76%

Real leaderboard coming soon!
Contact admin @Nagromtrade to update.

Full board: https://one.exness-track.com/a/nagromtrade
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode='Markdown')

async def contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CONTEST_TEXT, parse_mode='Markdown')

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(LEADERBOARD_TEXT, parse_mode='Markdown')

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ To join:\n1. Click: https://one.exness-track.com/a/nagromtrade\n2. Create trading account\n3. Send your account number to @Nagromtrade")

dedef run_bot():
    import asyncio
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set in Render Environment!", flush=True)
        return
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Starting Telegram bot polling...", flush=True)
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("contest", contest))
        application.add_handler(CommandHandler("leaderboard", leaderboard))
        application.add_handler(CommandHandler("register", register))
        application.run_polling()
    except Exception as e:
        print(f"Bot crashed: {e}", flush=True)
