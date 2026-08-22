import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/4gaf9z8m5c"
TELEGRAM_LINK = "https://t.me/+18142709814"
TELEGRAM_NUMBER = "+1 814 270 9814"
CHANNEL_USERNAME = "@nagromtradecontest"
CHANNEL_LINK = "https://t.me/nagromtradecontest"
LEADERBOARD_FILE = "leaderboard.json"

app = Flask(__name__)

@app.route('/')
def home(): return "Nagromtrade AUTO POST"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []
def save_board(d):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(d,f)

async def post_to_channel(context, text):
    try:
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Channel post failed: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🚀 Join Trading Contest", callback_data="register")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"), InlineKeyboardButton("📜 Rules", callback_data="rules")],
        [InlineKeyboardButton("❓ How do I start?", callback_data="howtostart")],
        [InlineKeyboardButton("🔗 Create Exness Account", url=PARTNER_LINK)],
        [InlineKeyboardButton(f"📱 Telegram {TELEGRAM_NUMBER}", url=TELEGRAM_LINK)]
    ]
    text = (
        "🏆 **NAGROM FOREX TRADING CONTEST** 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💰 **PRIZE POOL: $500 MONTHLY**\n"
        "🥇 1st: $250 | 🥈 2nd: $150 | 🥉 3rd: $100\n\n"
        "📢 Official Channel: @nagromtradecontest\n"
        "📌 How to Join:\n"
        "• Create via our IB link\n"
        "• Deposit $50 minimum\n"
        "• Tap Join Contest\n\n"
        "✅ Official Exness IB Partner\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 IB: {PARTNER_LINK}\n"
        f"📢 Channel: {CHANNEL_LINK}\n"
        f"📱 Support: {TELEGRAM_NUMBER}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 Choose an option:"
    )
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
    for t in board:
        if str(t['account'])==acc and t.get('chat_id'):
            try: await context.bot.send_message(chat_id=t['chat_id'], text=f"🎉 APPROVED! {acc} is in contest! Updates: {CHANNEL_LINK}")
            except: pass

async def postleaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id)!=ADMIN_ID: return
    board=load_board()
    verified=[t for t in board if t.get('verified')]
    if not verified:
        txt="🏆 **LEADERBOARD UPDATE**\n\nNo verified traders yet. Be the first to win $250!\n\nJoin now: @Nagrom_trade_bot"
    else:
        txt="🏆 **LIVE LEADERBOARD - NAGROM $500 CONTEST**\n━━━━━━━━━━━━━━\n\n" + "\n".join([f"{i+1}. {t['name']} | Acc: ...{str(t['account'])[-4:]}" for i,t in enumerate(verified[:10])]) + f"\n\nJoin: {PARTNER_LINK}\nBot: @Nagrom_trade_bot"
    await post_to_channel(context, txt)
    await update.message.reply_text("✅ Posted to channel!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    data=query.data
    user=query.from_user
    username = f"@{user.username}" if user.username else "No username"
    if data.startswith("admin_approve_"):
        acc=data.replace("admin_approve_","")
        board=load_board()
        approved_name=""
        for t in board:
            if str(t['account'])==acc: 
                t['verified']=True
                approved_name=t['name']
        save_board(board)
        await query.edit_message_text(f"✅ APPROVED {acc}!")
        # Auto post to channel
        await post_to_channel(context, f"🎉 **NEW VERIFIED TRADER**\n\n👤 {approved_name}\n🔢 Account ...{acc[-4:]}\n✅ Verified for $500 contest!\n\n{len([x for x in board if x.get('verified')])} traders now competing!\n\nJoin: @Nagrom_trade_bot")
        for t in board:
            if str(t['account'])==acc and t.get('chat_id'):
                try: await context.bot.send_message(chat_id=t['chat_id'], text=f"🎉 APPROVED! {acc} verified! Good luck! Channel: {CHANNEL_LINK}")
                except: pass
        return
    if data=="register":
        context.user_data['step']='awaiting_account'
        context.user_data['reg']={}
        await query.message.reply_text("🚀 **JOIN CONTEST**\n\nStep 1/3: Send Exness Account Number\nEx: 12345678", disable_web_page_preview=True)
        return
    if data=="howtostart":
        try:
            btns=[]
            if user.username:
                btns.append([InlineKeyboardButton(f"💬 Chat {user.first_name}", url=f"https://t.me/{user.username}")])
            btns.append([InlineKeyboardButton("📩 Open Chat", url=f"tg://user?id={user.id}")])
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"❓ How to start? From {user.first_name} {username} ID:{user.id}", reply_markup=InlineKeyboardMarkup(btns))
        except: pass
        await query.message.reply_text(f"📘 **HOW TO START**\n1️⃣ Create: {PARTNER_LINK}\n2️⃣ Deposit $50\n3️⃣ Join Contest\n\n📢 Channel: {CHANNEL_LINK}\n📱 {TELEGRAM_LINK}", disable_web_page_preview=True)
        return
    if data=="leaderboard":
        board=load_board()
        verified=[t for t in board if t.get('verified')]
        if not verified:
            txt="🏆 **LEADERBOARD**\n\nNo traders yet! Be first! $500 prize!"
        else:
            txt="🏆 **LEADERBOARD TOP 10**\n\n" + "\n".join([f"{i+1}. {t['name']} | {t['account']}" for i,t in enumerate(verified[:10])])
        await query.message.reply_text(txt)
        return
    elif data=="rules":
        await query.message.reply_text(f"📜 RULES: Use IB {PARTNER_LINK} Min $50\n📢 {CHANNEL_LINK}\n📱 {TELEGRAM_NUMBER}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_user.id
    text=update.message.text.strip() if update.message.text else ""
    user=update.effective_user
    uname=f"@{user.username}" if user.username else user.first_name
    step=context.user_data.get('step')
    if step=='awaiting_account':
        context.user_data['reg']['account']=text
        context.user_data['step']='awaiting_name'
        await update.message.reply_text("Step 2/3: Full Name\nEx: John Mensah")
        return
    if step=='awaiting_name':
        context.user_data['reg']['name']=text
        context.user_data['step']='awaiting_phone'
        await update.message.reply_text("Step 3/3: Phone/WhatsApp\nEx: +233XXXXXXXXX")
        return
    if step=='awaiting_phone':
        reg=context.user_data.get('reg',{})
        reg['phone']=text
        board=load_board()
        new_entry={"account":reg.get('account'),"name":reg.get('name'),"phone":reg.get('phone'),"telegram":uname,"chat_id":chat_id,"verified":False}
        board.append(new_entry)
        save_board(board)
        context.user_data.clear()
        try:
            kb=[[InlineKeyboardButton(f"✅ Approve {new_entry['account']}", callback_data=f"admin_approve_{new_entry['account']}")],[InlineKeyboardButton(f"💬 Chat {new_entry['name']}", url=f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}")]]
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW REQUEST\n👤 {new_entry['name']}\n🔢 {new_entry['account']}\n📱 {new_entry['phone']}\n💬 {uname} ID:{chat_id}", reply_markup=InlineKeyboardMarkup(kb))
        except: pass
        # Auto post new join to channel (without full number)
        await post_to_channel(context, f"🆕 **NEW CONTEST ENTRY**\n\n👤 Trader: {new_entry['name']}\n🔢 Acc: ...{str(new_entry['account'])[-4:]}\n⏳ Pending verification\n\nTotal entries: {len(board)}\nJoin now: @Nagrom_trade_bot")
        await update.message.reply_text(f"✅ Request Sent!\n{new_entry['name']} | {new_entry['account']}\nAdmin will approve. Check channel {CHANNEL_LINK}\nSupport: {TELEGRAM_LINK}")
        return

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("approve", approve))
application.add_handler(CommandHandler("postleaderboard", postleaderboard_cmd))
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
