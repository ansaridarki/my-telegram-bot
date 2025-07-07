from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات شما هستم.")

app = ApplicationBuilder().token("7584412458:AAHf0DQODAmIFZLLN8bAve2rgxbiqgtQiNU").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
