import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/4gaf9z8m5c"
LEADERBOARD_FILE = "leaderboard.json"
PENDING_FILE = "pending.json"

app = Flask(__name__)

YOUR_USERNAME = "officialnagrom"

@app.route('/')
def home(): return "Nagromtrade PRO Bot LIVE"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []

def save_board(data):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f)

def load_pending():
    try:
        with open(PENDING_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_pending(data):
    with open(PENDING_FILE, 'w') as f: json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 Create Exness Account (Under My IB)", url=PARTNER_LINK)],
        [InlineKeyboardButton("✅ I Have Account - Join Contest ($50 min)", callback_data="register")],
        [InlineKeyboardButton("📊 Verified Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💼 Account Management", callback_data="manage")],
        [InlineKeyboardButton("👤 Contact @officialnagrom", url=f"https://t.me/{YOUR_USERNAME}")]
    ]
    await update.message.reply_text(
        f"🏆 NAGROMTRADE OFFICIAL CONTEST\n\n"
        f"1️⃣ Create account via my link\n2️⃣ Deposit $50\n3️⃣ Join Contest\n\n"
        f"Link: {PARTNER_LINK}\nSupport: @{YOUR_USERNAME}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id)!= ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Usage: /approve 41626257")
        return
    acc = context.args[0].strip()
    board = load_board()
    for t in board:
        if str(t['account']).strip() == acc:
            t['verified'] = True
            t['balance'] = 50
    save_board(board)
    await update.message.reply_text(f"✅ Approved {acc}!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("admin_approve_"):
        acc = data.replace("admin_approve_", "")
        board = load_board()
        for t in board:
            if str(t['account']) == acc:
                t['verified'] = True
                t['balance'] = 50
        save_board(board)
        await query.edit_message_text(f"✅ Approved {acc} - Added!")
        return

    if data == "register":
        context.user_data['step'] = 'awaiting_exness_id'
        await query.message.reply_text(f"✅ Send your Exness Account Number:\n\nIf no account yet:\n{PARTNER_LINK}\n\nNow send number:")

    elif data == "leaderboard":
        board = load_board()
        verified = [t for t in board if t.get('verified')]
        if not verified:
            await query.message.reply_text("📊 Verified Leaderboard ($10 min)\n\nEmpty yet - Be first!")
        else:
            text = "🏆 LEADERBOARD $50+ Verified\n\n"
            for i, t in enumerate(verified[:15], 1):
                text += f"{i}. {t['name']} | {t['account']} | {t['profit']}%\n"
            await query.message.reply_text(text)

    elif data == "manage":
        context.user_data['step'] = 'awaiting_manage'
        await query.message.reply_text("💼 Account Management\n\nSend in ONE message:\n1. Account Number\n2. Investor Password\n3. Server\n4. WhatsApp")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    user = update.effective_user
    username_str = f"@{user.username}" if user.username else user.first_name
    step = context.user_data.get('step')

    # JOIN CONTEST FLOW
    if step == 'awaiting_exness_id':
        context.user_data['account'] = text
        context.user_data['step'] = 'awaiting_proof'
        await update.message.reply_text(f"Got account: {text}\n\nNow send proof of $50 deposit (screenshot or text 'Deposited $50')")
        return

    if step == 'awaiting_proof':
        acc = context.user_data.get('account', 'Unknown')
        board = load_board()
        board.append({"name": user.first_name, "account": acc, "profit": 0, "balance": 0, "verified": False, "telegram": username_str, "chat_id": chat_id, "proof": text})
        save_board(board)
        context.user_data.clear()
        try:
            kb = [[InlineKeyboardButton(f"✅ Approve {acc}", callback_data=f"admin_approve_{acc}")]]
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW JOIN NEEDS $50 VERIFY\n\nName: {user.first_name} {username_str}\nChat ID: {chat_id}\nAccount: {acc}\nProof: {text}\n\nApprove: /approve {acc}", reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(e)
        await update.message.reply_text(f"✅ Pending verification! Account {acc} sent to @{YOUR_USERNAME} for $50 check. Will be added after verification!")
        return

    if step == 'awaiting_manage':
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT LEAD\nFrom: {user.first_name} {username_str} ({chat_id})\n\n{text}")
        except: pass
        context.user_data.clear()
        await update.message.reply_text(f"✅ Sent to @{YOUR_USERNAME}")
        return

    # Default - forward to admin
    if str(chat_id)!= ADMIN_ID and text:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"📩 {user.first_name} {username_str} ({chat_id}): {text}")
        except: pass

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("approve", approve))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

def run_flask(): app.run(host="0.0.0.0", port=10000)
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
