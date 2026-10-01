from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8561312569:AAEmCzD2V941Lo8BFlxCN3110aJ3EmJloZM"  # BotFather se API Token yahan dalein
WEBAPP_URL = "https://your-render-app.onrender.com"  # Render web service link

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ref_id = context.args[0] if context.args else ""
    full_url = f"{WEBAPP_URL}?ref={ref_id}" if ref_id else WEBAPP_URL

    keyboard = [
        [InlineKeyboardButton("🚀 Launch Eclipse Mini App", web_app=WebAppInfo(url=full_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 **Welcome to Eclipse Reward Bot!**\n\nDaily 3 tasks pooray karein, Eclipse Light ON karein aur Blue$ coins earn karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()