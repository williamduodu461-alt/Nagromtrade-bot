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
def home(): return "Nagromtrade with LOGO LIVE"

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
        [InlineKeyboardButton("🔗 Create Exness Account", url=PARTNER_LINK)],
        [InlineKeyboardButton("💼 Account Management", callback_data="manage"), InlineKeyboardButton("💬 Support", url=f"https://t.me/{YOUR_USERNAME}")]
    ]
    text = (
        "🏆 **NAGROM FOREX TRADING CONTEST** 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💰 **PRIZE POOL: $500 MONTHLY**\n"
        "🥇 1st: $250 | 🥈 2nd: $150 | 🥉 3rd: $100\n\n"
        "📌 **How to Participate:**\n"
        "• Create via our IB link below\n"
        "• Deposit **$10** minimum\n"
        "• Trade & climb leaderboard\n\n"
        "✅ Official Exness IB Partner\n"
        "📊 Live Ranking | ⚡️ Monthly Payouts\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 {PARTNER_LINK}\n"
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
            t['balance']=10
    save_board(board)
    await update.message.reply_text(f"✅ Approved {acc}!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    data=query.data
    if data.startswith("admin_approve_"):
        acc=data.replace("admin_approve_","")
        board=load_board()
        for t in board:
            if str(t['account'])==acc:
                t['verified']=True
                t['balance']=10
        save_board(board)
        await query.edit_message_text(f"✅ Approved {acc} - Added!")
        return
    if data=="register":
        context.user_data['step']='awaiting_exness_id'
        await query.message.reply_text(f"🚀 **JOIN CONTEST**\n\nSend your Exness Account Number\nMust be via our IB link\n\nNo account? {PARTNER_LINK}\n\nNow send number:", disable_web_page_preview=True)
    elif data=="leaderboard":
        board=load_board()
        verified=[t for t in board if t.get('verified')]
        if not verified:
            txt="🏆 **LEADERBOARD - $50+ Verified**\n━━━━━━━━━━━━━\n\nEmpty! Be first!\n1. Create via IB link\n2. Deposit $50"
        else:
            verified.sort(key=lambda x:x.get('profit',0), reverse=True)
            txt="🏆 **NAGROM FOREX LEADERBOARD**\n━━━━━━━━━━━━━\n\n"
            medals=["🥇","🥈","🥉"]
            for i,t in enumerate(verified[:10],1):
                medal=medals[i-1] if i<=3 else f"{i}."
                txt+=f"{medal} {t['name']} | {t['account']} | {t['profit']}%\n"
            txt+="\n━━━━━━━━━━━━━\nOnly $50+ verified"
        await query.message.reply_text(txt, parse_mode="Markdown")
    elif data=="rules":
        txt=f"📜 **CONTEST RULES**\n━━━━━━━━━━━━━\n\n1️⃣ Must be under our IB\n{PARTNER_LINK}\n\n2️⃣ Min deposit $50\n\n3️⃣ No cheating\n\n4️⃣ Winners 1st of month\n\n5️⃣ Prize: USDT / MoMo\n\nSupport: @{YOUR_USERNAME}"
        await query.message.reply_text(txt, disable_web_page_preview=True)
    elif data=="manage":
        context.user_data['step']='awaiting_manage'
        await query.message.reply_text(f"💼 **ACCOUNT MANAGEMENT**\n━━━━━━━━━━━━━\n\nWe manage & grow your account.\nProfit share after success.\n\n⚠️ Risky\n\nSend:\n• Account Number\n• Investor Password\n• Server\n• WhatsApp\n\nDM: @{YOUR_USERNAME}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_user.id
    text=update.message.text.strip() if update.message.text else ""
    user=update.effective_user
    uname=f"@{user.username}" if user.username else user.first_name
    step=context.user_data.get('step')
    if step=='awaiting_exness_id':
        context.user_data['account']=text
        context.user_data['step']='awaiting_proof'
        await update.message.reply_text(f"✅ Account: {text}\n\nNow send proof of $50 deposit.")
        return
    if step=='awaiting_proof':
        acc=context.user_data.get('account','Unknown')
        board=load_board()
        board.append({"name":user.first_name,"account":acc,"profit":0,"balance":0,"verified":False,"telegram":uname,"chat_id":chat_id,"proof":text})
        save_board(board)
        context.user_data.clear()
        try:
            kb=[[InlineKeyboardButton(f"✅ Approve {acc}",callback_data=f"admin_approve_{acc}")]]
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW JOIN - VERIFY $50\n\nName: {user.first_name} {uname}\nAccount: {acc}\nProof: {text}\nChat: {chat_id}\n\nCheck Exness PA, then /approve {acc}", reply_markup=InlineKeyboardMarkup(kb))
        except: pass
        await update.message.reply_text(f"⏳ Pending! Account {acc} sent to @{YOUR_USERNAME}")
        return
    if step=='awaiting_manage':
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT LEAD\nFrom: {user.first_name} {uname} ({chat_id})\n\n{text}")
        except: pass
        context.user_data.clear()
        await update.message.reply_text(f"✅ Sent to @{YOUR_USERNAME}")
        return
    if str(chat_id)!=ADMIN_ID and text:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"📩 {user.first_name} {uname}: {text}")
        except: pass

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
