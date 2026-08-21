import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏆 Join Contest", url="https://one.exness-track.com/a/v5lj6z4p?platform=mobile")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
    ]
    await update.message.reply_text(
        "🏆 Welcome to Nagromtrade!\n\nWe're glad to have you here.\n\n💰 Monthly trading contest - Win cash!\n👇 Click to join:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot Live!")
    app.run_polling()

if __name__ == "__main__":
    main()
