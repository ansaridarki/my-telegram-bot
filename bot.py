import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# 🛡️ تنظیمات پایه
TOKEN = "7584412458:AAHf0DQODAmIFZLLN8bAve2rgxbiqgtQiNU"  # توکن ربات
PASSWORD = "1111"  # رمز ورود
STORAGE_DIR = r"X:\bot"  # مسیر ذخیره فایل (تغییر بده!)

# وضعیت‌ها برای ConversationHandler
ASK_PASSWORD, MAIN_MENU = range(2)

# کاربران تأیید شده
user_authenticated = set()


# 🎬 شروع: درخواست رمز
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 برای ادامه لطفاً رمز را وارد کنید:")
    return ASK_PASSWORD


# ✅ بررسی رمز
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == PASSWORD:
        user_authenticated.add(update.message.from_user.id)

        reply_keyboard = [["📥 ذخیره فایل", "📤 مشاهده فایل‌ها"]]
        await update.message.reply_text(
            "✅ رمز صحیح بود! لطفاً یک گزینه انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        )
        return MAIN_MENU
    else:
        await update.message.reply_text("❌ رمز اشتباه است. دوباره تلاش کنید:")
        return ASK_PASSWORD


# 📋 مدیریت منو
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📥 ذخیره فایل":
        await update.message.reply_text("لطفاً فایل، عکس یا ویدیوی خود را ارسال کنید.")
        return MAIN_MENU

    elif text == "📤 مشاهده فایل‌ها":
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)

        files = os.listdir(STORAGE_DIR)
        if not files:
            await update.message.reply_text("📂 هیچ فایلی ذخیره نشده.")
        else:
            file_list = "\n".join(f"📁 {f}" for f in files)
            await update.message.reply_text(f"فایل‌های ذخیره‌شده:\n{file_list}")
        return MAIN_MENU

    else:
        await update.message.reply_text("❗ گزینه نامعتبر. لطفاً از منو استفاده کنید.")
        return MAIN_MENU


# 💾 ذخیره فایل‌ها
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in user_authenticated:
        await update.message.reply_text("❗️ابتدا باید رمز ورود را وارد کنید با دستور /start")
        return

    file = None
    file_name = "unknown"

    if update.message.document:
        file = update.message.document
        file_name = file.file_name
    elif update.message.photo:
        file = update.message.photo[-1]
        file_name = f"photo_{update.message.message_id}.jpg"
    elif update.message.video:
        file = update.message.video
        file_name = f"video_{update.message.message_id}.mp4"
    else:
        await update.message.reply_text("❗ فقط فایل، عکس یا ویدیو ارسال کنید.")
        return

    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    file_obj = await file.get_file()
    file_path = os.path.join(STORAGE_DIR, file_name)
    await file_obj.download_to_drive(file_path)

    await update.message.reply_text(f"✅ فایل با موفقیت ذخیره شد به مسیر:\n{file_path}")


# 🚀 اجرای ربات
if __name__ == '__main__':
    os.makedirs(STORAGE_DIR, exist_ok=True)

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
        },
        fallbacks=[],
    )

    # افزودن هندلرها
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, file_handler))

    print("🤖 ربات روشن شد و در حال اجراست...")
    app.run_polling()
