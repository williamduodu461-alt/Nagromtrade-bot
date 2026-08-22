import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
LEADERBOARD_FILE = "leaderboard.json"

app = Flask(__name__)
user_data_temp = {}

YOUR_USERNAME = "officailnagrom"
YOUR_CONTACT_LINK = "https://t.me/+18142709814"

@app.route('/')
def home(): return "Nagromtrade Contest Bot is LIVE"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []

def save_board(data):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏆 Join Contest / Register", callback_data="register")],
        [InlineKeyboardButton("📊 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💼 Account Management", callback_data="manage")],
        [InlineKeyboardButton("👤 Contact Admin Directly", url=f"https://t.me/{YOUR_USERNAME}")],
        [InlineKeyboardButton("📞 Join My Private Channel", url=YOUR_CONTACT_LINK)]
    ]
    await update.message.reply_text(
        "🏆 **Welcome to Nagromtrade Trading Contest!**\n\n"
        "Compete with traders globally, climb the leaderboard and win huge prizes monthly!\n\n"
        "✅ Verified Exness IB Partner\n"
        "📊 Live Leaderboard\n"
        "🎁 Monthly Cash Prizes\n"
        "💼 Account Management Available\n\n"
        f"Admin: @{YOUR_USERNAME}\n"
        "Tap START to join!",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    
    if query.data == "register":
        user_data_temp[chat_id] = {"step": "awaiting_exness_id"}
        await query.message.reply_text(
            "Great! Send your Exness Account Number\n\n"
            "⚠️ Make sure you created it with my Partner Link to qualify!\n\n"
            f"If you haven't, contact me first: @{YOUR_USERNAME}"
        )
    
    elif query.data == "leaderboard":
        board = load_board()
        if not board: 
            text = "Leaderboard is empty — be the first to register!"
        else:
            text = "🏆 **Top Traders - Nagromtrade Contest**\n\n"
            for i, trader in enumerate(board[:15], 1):
                text += f"{i}. {trader['name']} - {trader['account']} - {trader['profit']}% \n"
        keyboard = [[InlineKeyboardButton("Contact Admin", url=f"https://t.me/{YOUR_USERNAME}")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    elif query.data == "manage":
        user_data_temp[chat_id] = {"step": "awaiting_manage_details"}
        await query.message.reply_text(
            "💼 **Account Management Service**\n\n"
            "I will manage your account and make good profit for you. You can thank me with anything you want after.\n\n"
            "⚠️ RISK WARNING: Trading is risky.\n\n"
            "Please send in ONE message:\n"
            "1. MT4/MT5 Account Number\n"
            "2. Investor Password\n"
            "3. Server (e.g. Exness-Real)\n"
            "4. Your WhatsApp\n\n"
            f"Or contact me directly here: @{YOUR_USERNAME}\n"
            f"Or via link: {YOUR_CONTACT_LINK}\n\n"
            "Example:\n123456789\nInvestorPass123\nExness-Real\n+233XXXXXXXXX"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.from_user.id
    text = update.message.text
    user = update.from_user
    username_str = f"@{user.username}" if user.username else "No username"
    
    if chat_id in user_data_temp:
        step = user_data_temp[chat_id].get("step")
        
        if step == "awaiting_exness_id":
            board = load_board()
            board.append({"name": user.first_name, "account": text, "profit": 0, "telegram": username_str, "chat_id": chat_id})
            save_board(board)
            if ADMIN_ID:
                try:
                    await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW REGISTRATION!\nName: {user.first_name}\nUser: {username_str}\nID: {chat_id}\nExness Account: {text}")
                except: pass
            del user_data_temp[chat_id]
            keyboard = [
                [InlineKeyboardButton("💼 Request Account Management", callback_data="manage")],
                [InlineKeyboardButton(f"Chat with @{YOUR_USERNAME}", url=f"https://t.me/{YOUR_USERNAME}")]
            ]
            await update.message.reply_text(f"✅ Registered! Account {text} added to leaderboard!\n\nNow you can request Account Management if you need it.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        elif step == "awaiting_manage_details":
            if ADMIN_ID:
                try:
                    await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT REQUEST - GENUINE LEAD!\nFrom: {user.first_name} {username_str} (ID:{chat_id})\n\nDETAILS:\n{text}\n\nContact them NOW: https://t.me/{YOUR_USERNAME}")
                except: pass
            del user_data_temp[chat_id]
            keyboard = [[InlineKeyboardButton("📞 Contact Me Now", url=YOUR_CONTACT_LINK)]]
            await update.message.reply_text(
                f"✅ Received! I have sent your details to @{YOUR_USERNAME}.\n\nI will contact you within 12hrs to start.\nYou can also message me directly: {YOUR_CONTACT_LINK}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    
    # Forward any other message to you so you never miss
    if ADMIN_ID and str(chat_id) != str(ADMIN_ID):
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"📩 Message from {user.first_name} {username_str} ({chat_id}):\n\n{text}")
        except: pass

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

def run_flask(): app.run(host="0.0.0.0", port=10000)
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("Starting Telegram bot polling...")
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
