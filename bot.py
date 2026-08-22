import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/4gaf9z8m5c"
TELEGRAM_LINK = "https://t.me/+18142709814"
TELEGRAM_NUMBER = "+1 814 270 9814"
LEADERBOARD_FILE = "leaderboard.json"
LOGO_FILE = "IMG_1161.jpeg"

app = Flask(__name__)
YOUR_USERNAME = "officialnagrom"

@app.route('/')
def home(): return "Nagromtrade TME LINK LIVE"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []
def save_board(d):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(d,f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Join Trading Contest", callback_data="register")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"), InlineKeyboardButton("📜 Rules", callback_data="rules")],
        [InlineKeyboardButton("❓ How do I start?", callback_data="howtostart")],
        [InlineKeyboardButton("🔗 Create Exness Account", url=PARTNER_LINK)],
        [InlineKeyboardButton(f"📱 Telegram {TELEGRAM_NUMBER}", url=TELEGRAM_LINK)],
        [InlineKeyboardButton("💬 Contact Admin Direct", url=TELEGRAM_LINK)]
    ]
    text = (
        "🏆 **NAGROM FOREX TRADING CONTEST** 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💰 **PRIZE POOL: $500 MONTHLY**\n"
        "🥇 1st: $250 | 🥈 2nd: $150 | 🥉 3rd: $100\n\n"
        "📌 Create via IB link → Deposit $50 → Join\n\n"
        "✅ Official Exness IB Partner\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 IB: {PARTNER_LINK}\n"
        f"📱 Telegram: {TELEGRAM_NUMBER}\n"
        f"🔗 Direct: {TELEGRAM_LINK}\n"
        f"👤 @{YOUR_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 Choose an option:"
    )
    try:
        if os.path.exists(LOGO_FILE):
            with open(LOGO_FILE, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                return
    except: pass
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id)!=ADMIN_ID: return
    if not context.args: return
    acc=context.args[0].strip()
    board=load_board()
    for t in board:
        if str(t['account'])==acc: t['verified']=True
    save_board(board)
    await update.message.reply_text(f"✅ Approved {acc}!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    data=query.data
    user=query.from_user
    username = f"@{user.username}" if user.username else "No username"
    if data.startswith("admin_approve_"):
        acc=data.replace("admin_approve_","")
        board=load_board()
        for t in board:
            if str(t['account'])==acc: t['verified']=True
        save_board(board)
        await query.edit_message_text(f"✅ Approved {acc}!")
        for t in board:
            if str(t['account'])==acc and t.get('chat_id'):
                try: await context.bot.send_message(chat_id=t['chat_id'], text=f"✅ APPROVED! {acc} verified! Contact {TELEGRAM_LINK} now.")
                except: pass
        return
    if data=="register":
        context.user_data['step']='awaiting_exness_id'
        await query.message.reply_text(f"🚀 Send Exness Account Number via {PARTNER_LINK}:")
        return
    if data=="howtostart":
        chat_buttons=[]
        if user.username:
            chat_buttons.append([InlineKeyboardButton(f"💬 Chat {user.first_name}", url=f"https://t.me/{user.username}")])
        chat_buttons.append([InlineKeyboardButton("📩 Open Chat ID", url=f"tg://user?id={user.id}")])
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"❓ How do I start? From {user.first_name} {username} ID:{user.id}", reply_markup=InlineKeyboardMarkup(chat_buttons))
        except: pass
        await query.message.reply_text(f"📘 HOW TO START:\n1. {PARTNER_LINK}\n2. $50\n3. Join\nAdmin {TELEGRAM_LINK} notified!")
        return
    if data=="leaderboard":
        board=load_board()
        verified=[t for t in board if t.get('verified')]
        txt="🏆 Empty!" if not verified else "🏆 Leaderboard:\n" + "\n".join([f"{i+1}. {t['name']} | {t['account']}" for i,t in enumerate(verified[:10])])
        await query.message.reply_text(txt)
    elif data=="rules":
        await query.message.reply_text(f"📜 RULES: IB {PARTNER_LINK} Min $50 Contact {TELEGRAM_LINK}")
    elif data=="manage":
        context.user_data['step']='awaiting_manage'
        await query.message.reply_text(f"💼 Send details to {TELEGRAM_LINK}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_user.id
    text=update.message.text.strip() if update.message.text else ""
    user=update.effective_user
    uname=f"@{user.username}" if user.username else user.first_name
    step=context.user_data.get('step')
    if step=='awaiting_exness_id':
        acc=text
        board=load_board()
        board.append({"name":user.first_name,"account":acc,"profit":0,"balance":0,"verified":False,"telegram":uname,"chat_id":chat_id})
        save_board(board)
        context.user_data.clear()
        try:
            kb=[[InlineKeyboardButton(f"✅ Approve {acc}",callback_data=f"admin_approve_{acc}")],[InlineKeyboardButton(f"💬 Chat {user.first_name}", url=f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}")]]
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW JOIN {user.first_name} {uname} Account {acc} ID {chat_id}", reply_markup=InlineKeyboardMarkup(kb))
        except: pass
        await update.message.reply_text(f"✅ {acc} sent! Contact {TELEGRAM_LINK}")
        return
    if step=='awaiting_manage':
        try: await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT {uname}: {text}")
        except: pass
        context.user_data.clear()
        await update.message.reply_text(f"✅ Sent to {TELEGRAM_LINK}")
        return

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("approve", approve))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

def run_flask(): app.run(host="0.0.0.0", port=10000)
def run_bot():
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__=="__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
