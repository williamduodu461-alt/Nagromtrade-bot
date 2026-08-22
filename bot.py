import os, threading, asyncio, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "8941296115"
PARTNER_LINK = "https://one.exnessonelink.com/a/4gaf9z8m5c"
LEADERBOARD_FILE = "leaderboard.json"

app = Flask(__name__)
user_data_temp = {}

YOUR_USERNAME = "officialnagrom"
YOUR_CONTACT_LINK = "https://t.me/+18142709814"

@app.route('/')
def home(): return "Nagromtrade PRO Bot LIVE"

def load_board():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except: return []

def save_board(data):
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 Create Exness Account (Under My IB)", url=PARTNER_LINK)],
        [InlineKeyboardButton("✅ I Have Account - Join Contest ($50 min)", callback_data="register")],
        [InlineKeyboardButton("📊 Verified Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💼 Account Management", callback_data="manage")],
        [InlineKeyboardButton("👤 Contact @officialnagrom", url=f"https://t.me/{YOUR_USERNAME}")]
    ]
    await update.message.reply_text(
        f"🏆 **NAGROMTRADE OFFICIAL CONTEST**\n\n"
        f"Trade with Exness under my IB & Win Cash Monthly!\n\n"
        f"**HOW TO JOIN:**\n"
        f"1️⃣ Create account via my link below (auto-linked to me)\n"
        f"2️⃣ Deposit minimum **$50**\n"
        f"3️⃣ Click 'Join Contest' & send your account number\n\n"
        f"💰 Prize Pool: Monthly\n"
        f"✅ Verified IB: Nagromtrade\n"
        f"📞 Support: @{YOUR_USERNAME}\n\n"
        f"Tap to start:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id)!= ADMIN_ID:
        await update.message.reply_text("Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /approve ACCOUNT_NUMBER")
        return
    acc = context.args[0]
    board = load_board()
    found = False
    for trader in board:
        if trader['account'] == acc:
            trader['verified'] = True
            trader['balance'] = 50
            found = True
    if found:
        save_board(board)
        await update.message.reply_text(f"✅ Approved {acc} - Now on leaderboard!")
        try:
            for t in board:
                if t['account'] == acc:
                    await context.bot.send_message(chat_id=t['chat_id'], text=f"🎉 Your account {acc} has been VERIFIED! You are now on the leaderboard with $50 minimum! Good luck!")
        except: pass
    else:
        await update.message.reply_text(f"Account {acc} not found in pending list")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id

    if query.data == "register":
        user_data_temp[chat_id] = {"step": "awaiting_exness_id"}
        await query.message.reply_text(
            "✅ **Join Contest**\n\n"
            "Send your Exness Account Number (only accounts created via my link will be approved)\n\n"
            f"If you don't have account yet, create first here:\n{PARTNER_LINK}\n\n"
            "Now send your Account Number:",
            disable_web_page_preview=True
        )

    elif query.data == "leaderboard":
        board = load_board()
        verified_board = [t for t in board if t.get('verified') == True]
        if not verified_board:
            text = "📊 **Verified Leaderboard ( $50 min )**\n\nEmpty! No verified traders yet.\n\nTo join:\n1. Create account via my link\n2. Deposit $50\n3. Send account number"
        else:
            verified_board.sort(key=lambda x: x.get('profit',0), reverse=True)
            text = "🏆 **NAGROMTRADE LEADERBOARD - $50+ Verified**\n\n"
            for i, t in enumerate(verified_board[:15], 1):
                text += f"{i}. {t['name']} | {t['account']} | {t['profit']}%\n"
            text += f"\nOnly verified $50+ accounts count!"
        await query.message.reply_text(text, parse_mode="Markdown")

    elif query.data == "manage":
        user_data_temp[chat_id] = {"step": "awaiting_manage_details"}
        await query.message.reply_text(
            "💼 **Account Management**\n\n"
            "I will manage your account and make good profit. Thank me with anything you want after.\n\n"
            "⚠️ Trading is risky - invest what you can afford to lose\n\n"
            "Send in ONE message:\n"
            "1. Account Number\n2. Investor Password\n3. Server\n4. WhatsApp Number\n\n"
            f"Or DM @{YOUR_USERNAME} directly: {YOUR_CONTACT_LINK}"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.from_user.id
    text = update.message.text if update.message.text else ""
    photo = update.message.photo
    user = update.from_user
    username_str = f"@{user.username}" if user.username else f"{user.first_name}"

    if chat_id in user_data_temp:
        step = user_data_temp[chat_id].get("step")

        if step == "awaiting_exness_id":
            user_data_temp[chat_id]['account'] = text
            user_data_temp[chat_id]['step'] = "awaiting_balance_proof"
            await update.message.reply_text(
                f"Got account: {text}\n\n"
                f"Now to verify you deposited $50 minimum:\n"
                f"Send a screenshot of your Exness deposit / balance showing $50+\n\n"
                f"Or just type: 'I deposited $50 in {text}'\n\n"
                f"I will verify manually and add you!"
            )
            return

        elif step == "awaiting_balance_proof":
            acc = user_data_temp[chat_id].get('account')
            board = load_board()
            board.append({
                "name": user.first_name,
                "account": acc,
                "profit": 0,
                "balance": 0,
                "verified": False,
                "telegram": username_str,
                "chat_id": chat_id,
                "proof": text
            })
            save_board(board)

            # Notify admin with approve button
            try:
                keyboard = [[InlineKeyboardButton(f"✅ Approve {acc}", callback_data=f"admin_approve_{acc}")]]
                if photo:
                    await context.bot.send_photo(chat_id=int(ADMIN_ID), photo=photo[-1].file_id, caption=f"🆕 NEW CONTEST JOIN - NEEDS $50 VERIFICATION\n\nName: {user.first_name} {username_str}\nChat ID: {chat_id}\nAccount: {acc}\nProof: {text}\n\nTo approve, send: /approve {acc}")
                else:
                    await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🆕 NEW CONTEST JOIN - NEEDS $50 VERIFICATION\n\nName: {user.first_name} {username_str}\nChat ID: {chat_id}\nAccount: {acc}\nProof: {text}\n\nTo approve, send: /approve {acc}", reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as e:
                print(f"Admin notify error: {e}")

            del user_data_temp[chat_id]
            await update.message.reply_text(
                f"✅ Received! Your account **{acc}** is PENDING verification.\n\n"
                f"I will check if:\n"
                f"1. You created via my link: {PARTNER_LINK}\n"
                f"2. You deposited $50 minimum\n\n"
                f"Once I confirm, you will be added to leaderboard! Check back in few hours.\n\n"
                f"Questions? Contact @{YOUR_USERNAME}",
                parse_mode="Markdown"
            )
            return

        elif step == "awaiting_manage_details":
            try:
                if photo:
                    await context.bot.send_photo(chat_id=int(ADMIN_ID), photo=photo[-1].file_id, caption=f"💼 MANAGEMENT LEAD - GENUINE!\nFrom: {user.first_name} {username_str} ({chat_id})\n\nDETAILS:\n{text}\n\nREPLY NOW!")
                else:
                    await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"💼 MANAGEMENT LEAD - GENUINE!\nFrom: {user.first_name} {username_str} ({chat_id})\n\nDETAILS:\n{text}\n\nREPLY NOW!")
            except: pass
            del user_data_temp[chat_id]
            await update.message.reply_text(f"✅ Management details received! Forwarded to @{YOUR_USERNAME}. I will contact you within 12hrs! {YOUR_CONTACT_LINK}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contact Me Now", url=YOUR_CONTACT_LINK)]]))
            return

    # Forward other messages to admin
    if str(chat_id)!= str(ADMIN_ID) and text:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"📩 Message from {user.first_name} {username_str} ({chat_id}):\n\n{text}")
        except: pass

    # Admin quick approve via button
    if str(chat_id) == ADMIN_ID and update.callback_query and update.callback_query.data.startswith("admin_approve_"):
        acc = update.callback_query.data.replace("admin_approve_", "")
        board = load_board()
        for trader in board:
            if trader['account'] == acc:
                trader['verified'] = True
                trader['balance'] = 50
        save_board(board)
        await update.callback_query.edit_message_text(f"✅ Approved {acc} - Added to leaderboard!")

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("approve", approve))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))

def run_flask(): app.run(host="0.0.0.0", port=10000)
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("Bot polling with partner link")
    application.run_polling(drop_pending_updates=True, stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
