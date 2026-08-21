import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Nagromtrade Contest Bot is LIVE!"

WELCOME_TEXT = """🏆 Welcome to Nagromtrade Trading Contest!

💰 Cash Prizes for Top Traders!

/contest - View contest details
/leaderboard - See rankings
/register - How to join

Trade with Exness and win!"""

CONTEST_TEXT = """📊 Nagromtrade Trading Contest

🏅 Prize Pool:
1st: $500
2nd: $300
3rd: $200
4th-10th: $50 each

📅 Duration: This Month
Trade the most profit % to win!

Use our Exness link to qualify."""

LEADERBOARD_TEXT = """📈 Real leaderboard coming soon!
Contact admin @Nagromtrade to update.

Full board: https://one.exness-track.com/a/nagromtrade"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode='Markdown')

async def contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CONTEST_TEXT, parse_mode='Markdown')

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(LEADERBOARD_TEXT)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ To join:\n1. Register via our Exness link\n2. Start trading\n3. Use /leaderboard to check rank!")

def run_bot():
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
        print("Bot polling stopped", flush=True)
    except Exception as e:
        print(f"Bot crashed: {e}", flush=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port)
