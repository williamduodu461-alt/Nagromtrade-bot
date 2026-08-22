import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"  # YOUR ID - Official NagromTrade
LEADERBOARD_FILE = "leaderboard.json"

app = Flask(__name__)
user_data_temp = {}

YOUR_USERNAME = "officialnagrom"
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
        [InlineKeyboardButton("📞 Join Private Channel", url=YOUR_CONTACT_LINK)]
    ]
    await update.message.reply_text(
        f"🏆 **Welcome to Nagromtrade Contest!**\n\n"
        "Compete globally, climb leaderboard & win cash monthly!\n\n"
        "✅ Verified Exness Partner\n"
        "📊 Live Leaderboard\n"
        "🎁 Monthly Cash Prizes\n"
        "💼 Account Management Available\n\n"
        f"Admin: @{YOUR_USERNAME}\n"
        "Tap below to start:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    
    if query.data == "register":
        user_data_temp[chat_id] = {"step": "awaiting_exness_id"}
        await query.message.reply_text(f"Send your Exness Account Number\nMake sure you used my Partner Link!\n\nNeed link? Contact @{YOUR_USERNAME}")
    
    elif query.data == "leaderboard":
        board = load_board()
        if not board: text = "Leaderboard empty — be the first!"
        else:
            text = "🏆 **Top Traders**\n\n"
            for i, t in enumerate(board[:15], 1):
                text += f"{i}. {t['name']} - {t['account']} - {t['profit']}%\n"
        await query.message.reply_text(text, parse_mode="Markdown")
    
    elif query.data == "manage":
        user_data_temp[chat_id] = {"step": "awaiting_manage_details"}
        await query.message.reply_text(
            "💼 **Account Management**\n\n"
            "I will manage your account and make good profit. Thank me with anything you want after.\n\n"
            "⚠️ Trading is risky\n\n"
            "Send in ONE message:\n"
            "1. Account Number\n2. Investor Password\n3. Server\n4. WhatsApp\n\n"
            f"Or contact @{YOUR_USERNAME} directly\n{YOUR_CONTACT_LINK}\n\n"
            "Ex: 123456789\nInvestorPass\nExness-Real\n+233..."
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
            try:
                await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW CONTEST REGISTRATION!\nName: {user.first_name}\nUser: {username_str}\nID: {chat_id}\nExness Account: {text}\n\nCheck if they used your Partner ID!")
            except: pass
            del user_data_temp[chat_id]
            await update.message.reply_text(f"✅ Registered {text}! You are on leaderboard!\n\nWant account management? Tap below.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💼 Request Management", callback_data="manage")]]))
            return
        elif step == "awaiting_manage_details":
            try:
                await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 GENUINE MANAGEMENT LEAD!\nFrom: {user.first_name} {username_str} (ID:{chat_id})\n\nDETAILS:\n{text}\n\nREPLY TO THEM NOW!")
            except: pass
            del user_data_temp[chat_id]
            await update.message.reply_text(f"✅ Got it! Forwarded to @{YOUR_USERNAME}. I will contact you within 12hrs!\nYou can also DM me: {YOUR_CONTACT_LINK}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contact Me Now", url=YOUR_CONTACT_LINK)]]))
            return
    
    # Forward all other messages to you
    if str(chat_id) != str(ADMIN_ID):
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
