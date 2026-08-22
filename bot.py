import os, threading, asyncio, json, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8941296115 # your ID - integer
PARTNER_LINK = "https://one.exnessonelink.com/a/0a3w8x5j"
CHANNEL_USERNAME = "@nagromtradecontest"
LEADERBOARD_FILE = "leaderboard.json"
PENDING_FILE = "pending.json"
PAY_BOT = "assitnagrompaybot"
SUPPORT = "NagromSupport"

app = Flask(__name__)
@app.route('/')
def home(): return "NagromTrade VERIFIED AUTO POST LIVE"

def load_json(file):
    try:
        with open(file, 'r') as f: return json.load(f)
    except: return []

def save_json(file, data):
    with open(file, 'w') as f: json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""🔥 **NAGROM TRADE CONTEST** 🔥

💰 Prize: $5000
📈 Join with Exness partner link

👇 How to join:
1. Register: {PARTNER_LINK}
2. Tap VERIFY below and send your Exness UID
3. Once verified, you enter leaderboard!

⚠️ If you register without our link, you will NOT be approved."""

    keyboard = [
        [InlineKeyboardButton("🚀 Register Exness (My Link)", url=PARTNER_LINK)],
        [InlineKeyboardButton("✅ Verify My Account", callback_data="verify")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💳 Get VIP Signals $60", url=f"https://t.me/{PAY_BOT}")],
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "verify":
        await q.message.reply_text("📩 **Send your Exness UID / Account Number now**\n\nExample: `123456789`\n\nWe will check if you are under our partnership in 5-10 mins.", parse_mode="Markdown")
        context.user_data["awaiting_uid"] = True

    elif data == "leaderboard":
        board = load_json(LEADERBOARD_FILE)
        if not board:
            txt = "🏆 Leaderboard empty - be first!"
        else:
            board = sorted(board, key=lambda x: x.get('profit',0), reverse=True)[:10]
            txt = "🏆 **LEADERBOARD**\n\n"
            for i, u in enumerate(board, 1):
                txt += f"{i}. {u['name']} - ${u['profit']}\n"
        await q.edit_message_text(txt, parse_mode="Markdown")

    elif data.startswith("approve_"):
        if q.from_user.id!= ADMIN_ID: return await q.answer("Only admin!", show_alert=True)
        uid = data.split("_")[1]
        pending = load_json(PENDING_FILE)
        user = next((p for p in pending if str(p['uid'])==uid), None)
        if user:
            board = load_json(LEADERBOARD_FILE)
            board.append({"uid": user['uid'], "name": user['name'], "profit": 0, "tg_id": user['tg_id']})
            save_json(LEADERBOARD_FILE, board)
            pending = [p for p in pending if str(p['uid'])!=uid]
            save_json(PENDING_FILE, pending)
            await context.bot.send_message(chat_id=user['tg_id'], text=f"✅ **VERIFIED!** Your Exness UID {uid} is under our partnership. You are now in leaderboard! Trade and send profit screenshots.", parse_mode="Markdown")
            await q.edit_message_text(f"✅ Approved {uid} - {user['name']}")

    elif data.startswith("reject_"):
        if q.from_user.id!= ADMIN_ID: return
        uid = data.split("_")[1]
        pending = load_json(PENDING_FILE)
        user = next((p for p in pending if str(p['uid'])==uid), None)
        if user:
            await context.bot.send_message(chat_id=user['tg_id'], text=f"❌ **REJECTED** UID {uid} is NOT under our partnership.\n\nPlease register again with correct link:\n{PARTNER_LINK}\n\nThen verify again.", parse_mode="Markdown")
            pending = [p for p in pending if str(p['uid'])!=uid]
            save_json(PENDING_FILE, pending)
            await q.edit_message_text(f"❌ Rejected {uid}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_uid"):
        uid = update.message.text.strip()
        if not uid.isdigit() or len(uid) < 5:
            return await update.message.reply_text("❌ Invalid UID. Send numbers only, e.g. `81234567`", parse_mode="Markdown")

        pending = load_json(PENDING_FILE)
        pending.append({"uid": uid, "name": update.effective_user.first_name, "tg_id": update.effective_user.id, "username": update.effective_user.username})
        save_json(PENDING_FILE, pending)
        context.user_data["awaiting_uid"] = False

        await update.message.reply_text(f"⏳ **UID {uid} received!** Checking if you are under our partnership...\n\nWait for admin approval (5-10 mins).", parse_mode="Markdown")

        # Send to ADMIN for verification
        keyboard = [[InlineKeyboardButton(f"✅ Approve {uid}", callback_data=f"approve_{uid}"), InlineKeyboardButton(f"❌ Reject {uid}", callback_data=f"reject_{uid}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 **New Verification Request**\n\nName: {update.effective_user.first_name} @{update.effective_user.username}\nUID: {uid}\nTG ID: {update.effective_user.id}\n\nGo to Exness Partner Area > Clients > Search {uid} -> If found, APPROVE, if not, REJECT.", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        # If user sends profit, forward to admin
        if update.message.photo:
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.id)
            await update.message.reply_text("📸 Screenshot received! Admin will update your profit on leaderboard.")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("leaderboard", lambda u,c: button_handler))
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_text))
    application.run_polling()

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()
run_bot()
