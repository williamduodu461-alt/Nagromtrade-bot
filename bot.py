import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/4gaf9z8m5c"
LEADERBOARD_FILE = "leaderboard.json"
LOGO_FILE = "IMG_1161.jpeg"

app = Flask(__name__)
YOUR_USERNAME = "officialnagrom"

@app.route('/')
def home(): return "Nagromtrade AUTO REQUEST LIVE"

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
        [InlineKeyboardButton("💼 Account Management", callback_data="manage"), InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{YOUR_USERNAME}")]
    ]
    text = (
        "🏆 **NAGROM FOREX TRADING CONTEST** 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💰 **PRIZE POOL: $500 MONTHLY**\n"
        "🥇 1st: $250 | 🥈 2nd: $150 | 🥉 3rd: $100\n\n"
        "📌 **How to Participate:**\n"
        "• Create via our IB link below\n"
        "• Deposit **$50** minimum\n"
        "• Trade & climb leaderboard\n\n"
        "✅ Official Exness IB Partner\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
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
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id)!=ADMIN_ID: return
    if not context.args: 
        await update.message.reply_text("Use: /approve ACCOUNT")
        return
    acc=context.args[0].strip()
    board=load_board()
    for t in board:
        if str(t['account'])==acc:
            t['verified']=True
            t['balance']=50
    save_board(board)
    await update.message.reply_text(f"✅ Approved {acc}!")
    for t in board:
        if str(t['account'])==acc and t.get('chat_id'):
            try: 
                await context.bot.send_message(
                    chat_id=t['chat_id'], 
                    text=f"✅ **APPROVED!**\n\nYour account {acc} is verified under our IB!\n\nYou are now in leaderboard 🏆\n\nYou can now contact admin @{YOUR_USERNAME} for trading & payouts.",
                    parse_mode="Markdown"
                )
            except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    data=query.data
    user=query.from_user

    if data.startswith("admin_approve_"):
        acc=data.replace("admin_approve_","")
        board=load_board()
        for t in board:
            if str(t['account'])==acc:
                t['verified']=True
                t['balance']=50
        save_board(board)
        await query.edit_message_text(f"✅ Approved {acc} - User notified!")
        for t in board:
            if str(t['account'])==acc and t.get('chat_id'):
                try:
                    await context.bot.send_message(chat_id=t['chat_id'], text=f"✅ APPROVED! Your account {acc} verified! Contact @{YOUR_USERNAME} now.")
                except: pass
        return

    if data=="register":
        context.user_data['step']='awaiting_exness_id'
        await query.message.reply_text(f"🚀 **JOIN CONTEST**\n\nSend your Exness Account Number\nMust be via our IB link:\n{PARTNER_LINK}\n\nNow send number:", disable_web_page_preview=True)

    elif data=="howtostart":
        # THIS SENDS DIRECTLY TO YOU
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=f"❓ NEW QUESTION: How do I start?\n\nFrom: {user.first_name} @{user.username if user.username else 'NoUsername'} (ID: {user.id})\n\nUser clicked 'How do I start?' button"
            )
        except: pass
        await query.message.reply_text(
            "📘 **HOW TO START - NAGROM FOREX**\n"
            "━━━━━━━━━━━━━\n\n"
            "1️⃣ Create Exness account via our IB link:\n"
            f"{PARTNER_LINK}\n\n"
            "2️⃣ Verify & Deposit $50 minimum\n\n"
            "3️⃣ Click 🚀 Join Trading Contest & send your account number\n\n"
            "4️⃣ Wait for admin approval (we check if under our IB)\n\n"
            "5️⃣ After approval, you can contact admin & start trading\n\n"
            "6️⃣ Trade & climb leaderboard to win $500 monthly!\n\n"
            f"Need help? Contact @{YOUR_USERNAME}\n\n"
            "Your question has been sent to admin directly!",
            disable_web_page_preview=True
        )

    elif data=="leaderboard":
        board=load_board()
        verified=[t for t in board if t.get('verified')]
        if not verified:
            txt="🏆 **LEADERBOARD**\n━━━━━━━━━━━━━\n\nEmpty! Be first!"
        else:
            verified.sort(key=lambda x:x.get('profit',0), reverse=True)
            txt="🏆 **LEADERBOARD**\n━━━━━━━━━━━━━\n\n"
            for i,t in enumerate(verified[:10],1):
                medal=["🥇","🥈","🥉"][i-1] if i<=3 else f"{i}."
                txt+=f"{medal} {t['name']} | {t['account']} | {t['profit']}%\n"
        await query.message.reply_text(txt, parse_mode="Markdown")
    elif data=="rules":
        await query.message.reply_text(f"📜 **RULES**\n1️⃣ Must be under IB\n{PARTNER_LINK}\n2️⃣ Min $50\n3️⃣ Monthly winners\nSupport @{YOUR_USERNAME}", disable_web_page_preview=True)
    elif data=="manage":
        context.user_data['step']='awaiting_manage'
        await query.message.reply_text(f"💼 **ACCOUNT MANAGEMENT**\nSend: Account, Investor Password, Server, WhatsApp\nDM @{YOUR_USERNAME}")

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
        # AUTO SEND REQUEST TO YOU - NO CONTACT BEFORE APPROVAL
        try:
            kb=[[InlineKeyboardButton(f"✅ Approve {acc}",callback_data=f"admin_approve_{acc}")]]
            await context.bot.send_message(
                chat_id=int(ADMIN_ID), 
                text=f"🆕 **NEW JOIN REQUEST - AUTO**\n\n👤 Name: {user.first_name} {uname}\n💳 Account: {acc}\n🆔 Chat ID: {chat_id}\n\n⚠️ Check in Exness PA if account is under your IB link & has $50\n\nTap Approve to verify user.",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except Exception as e:
            print(f"Admin fail: {e}")

        await update.message.reply_text(
            f"✅ **Account {acc} Received!**\n\n"
            f"⏳ Request automatically sent to admin for verification.\n\n"
            f"Please wait — admin will verify if your account is under our IB: {PARTNER_LINK}\n\n"
            f"After approval, you will be notified & can contact admin @{YOUR_USERNAME}.\n\n"
            f"❓ Click 'How do I start?' for guide.",
            disable_web_page_preview=True
        )
        return

    if step=='awaiting_manage':
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT\nFrom: {user.first_name} {uname} ({chat_id})\n\n{text}")
        except: pass
        context.user_data.clear()
        await update.message.reply_text(f"✅ Sent to @{YOUR_USERNAME}")
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
