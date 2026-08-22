import os, threading, asyncio, json, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue

BOT_TOKEN = os.getenv("BOT_TOKEN", "8642668602:AAG19zBWoQkv95eY2m6V0m02bm0K8CGs0x8")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/0a3w8x5j"
TELEGRAM_LINK = "https://t.me/+18142709814"
TELEGRAM_NUMBER = "+1 814 270 9814"
CHANNEL_USERNAME = "@nagromtradecontest"
CHANNEL_LINK = "https://t.me/nagromtradecontest"
LEADERBOARD_FILE = "leaderboard.json"
PAY_BOT = "assitnagrompaybot"
SUPPORT = "NagromSupport"

app = Flask(__name__)
@app.route('/')
def home(): return "NagromTrade AUTO POST + LEADERBOARD + PAYMENTS LIVE"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []

def save_board(d):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(d, f)

async def post_to_channel(context, text):
    try:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Post error: {e}")

# --- AUTO POST MESSAGES ---
AUTO_POSTS = [
    f"🔥 **NAGROM TRADE CONTEST** 🔥\n\n💰 Prize Pool: $5000\n🏆 Join the biggest Exness trading contest!\n\n👇 Register now with our partner link:\n{PARTNER_LINK}\n\n📊 Post your profits daily to climb leaderboard!\n🔗 {CHANNEL_LINK}",
    f"📈 **LIVE NOW - Smart Money Strategy**\n\nWe just banked +120 pips on GOLD!\n\nWant signals like this?\n1️⃣ Register Exness: {PARTNER_LINK}\n2️⃣ Join VIP: https://t.me/{PAY_BOT}\n\n{TELEGRAM_LINK}",
    f"🏆 **LEADERBOARD UPDATE**\n\nTop traders this week are winning big!\n\nWant to join contest?\nRegister here: {PARTNER_LINK}\nThen send your account screenshot to @{SUPPORT}\n\n{CHANNEL_LINK}"
]

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(AUTO_POSTS)
    await post_to_channel(context, msg)

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = f"""
🔥 **Welcome {name} to NAGROM TRADE** 🔥

We run 2 things:

1️⃣ **FREE Exness Contest** - Win $5000
   Register: {PARTNER_LINK}

2️⃣ **VIP Lifetime - $60**
   Daily Signals + Smart Money

👇 **Choose to Continue:**
"""
    keyboard = [
        [InlineKeyboardButton("🚀 Join Free Contest (Exness)", url=PARTNER_LINK)],
        [InlineKeyboardButton("🏆 View Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💳 Pay for VIP - MoMo Ghana", url=f"https://t.me/{PAY_BOT}?start=momo_ghana")],
        [InlineKeyboardButton("🎁 GiftCard / CashApp", url=f"https://t.me/{PAY_BOT}?start=gift_cashapp")],
        [InlineKeyboardButton("💳 Visa / GPay / Card", url=f"https://t.me/{PAY_BOT}?start=visa")],
        [InlineKeyboardButton("💰 USDT (TRC20)", url=f"https://t.me/{PAY_BOT}?start=usdt")],
        [InlineKeyboardButton("₿ Bitcoin", url=f"https://t.me/{PAY_BOT}?start=bitcoin")],
        [InlineKeyboardButton("🏦 Bank / Mpesa Africa", url=f"https://t.me/{PAY_BOT}?start=bank_africa")],
        [InlineKeyboardButton("📞 Support", url=f"https://t.me/{SUPPORT}"), InlineKeyboardButton("📢 Contest Channel", url=CHANNEL_LINK)]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = load_board()
    if not board:
        txt = "🏆 **Leaderboard is empty yet!**\n\nBe first to post profit:\n1. Register: " + PARTNER_LINK + "\n2. Trade and send screenshot to @" + SUPPORT
    else:
        board = sorted(board, key=lambda x: x.get('profit',0), reverse=True)[:10]
        txt = "🏆 **NAGROM TRADE LEADERBOARD** 🏆\n\n"
        for i, u in enumerate(board, 1):
            txt += f"{i}. {u['name']} - ${u['profit']} profit\n"
        txt += f"\nJoin now: {PARTNER_LINK}"
    keyboard = [[InlineKeyboardButton("🚀 Join Contest", url=PARTNER_LINK)], [InlineKeyboardButton("💳 Get VIP Signals", url=f"https://t.me/{PAY_BOT}")]]
    await update.message.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "leaderboard":
        board = load_board()
        if not board:
            txt = "🏆 Leaderboard empty! Trade and submit profit."
        else:
            board = sorted(board, key=lambda x: x.get('profit',0), reverse=True)[:10]
            txt = "🏆 **TOP 10 TRADERS**\n\n"
            for i, u in enumerate(board, 1):
                txt += f"{i}. {u['name']} - ${u['profit']}\n"
        await q.edit_message_text(txt, parse_mode="Markdown")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_builder = ApplicationBuilder().token(BOT_TOKEN).build()
    application = app_builder
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Auto Post every 6 hours
    job_queue = application.job_queue
    job_queue.run_repeating(auto_post_job, interval=21600, first=30)

    print("MAIN BOT STARTED - Auto Post + Leaderboard + Payments")
    application.run_polling()

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()
run_bot()
