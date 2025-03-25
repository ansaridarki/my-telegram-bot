from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توکن ربات تلگرامی رو اینجا قرار بده
TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"

# وقتی کاربر دستور /start رو می‌زنن
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات تو هستم. هر چی بنویسی بهت برمی‌گردونم! یادت باشه که اول سلام کنی ممنون 🤖")

# وقتی کاربر یه پیام به ربات بفرسته
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"تو گفتی: {user_message}")

def main():
    # ساخت اپلیکیشن ربات
    app = ApplicationBuilder().token(TOKEN).build()

    # اضافه کردن دستور /start
    app.add_handler(CommandHandler("start", start))
    # اضافه کردن پاسخ به هر پیامی که ارسال می‌شود
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ ربات روشنه... برو تو تلگرام تستش کن.")
    app.run_polling()

if __name__ == "__main__":
    main()
