from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import openai

# توکن ربات تلگرام
TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"  # توکن ربات خود را اینجا وارد کنید

# توکن OpenAI
OPENAI_API_KEY = "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"  # توکن OpenAI خود را اینجا وارد کنید

# تنظیم OpenAI API
openai.api_key = OPENAI_API_KEY

# تابع ارسال پیام به مدل GPT-3
async def answer_question(update: Update, context):
    question = update.message.text  # دریافت سوال از کاربر

    # ارسال سوال به مدل GPT-3
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # یا هر مدل دلخواهی که می‌خواهید استفاده کنید
            prompt=question,
            max_tokens=150  # محدودیت تعداد کلمات
        )

        # استخراج پاسخ از OpenAI
        answer = response.choices[0].text.strip()

        # ارسال پاسخ به کاربر
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("❌ مشکلی پیش آمد. لطفاً دوباره امتحان کنید.")

# تابع برای /start
async def start(update: Update, context):
    await update.message.reply_text("سلام! از من هر سوالی بپرس و من جواب میدم.")

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # افزودن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))

    # اجرای ربات
    print("✅ ربات در حال اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()
