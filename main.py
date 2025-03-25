from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"
OWNER_ID = 7764863274  # آیدی عددی تلگرامت (فقط خودت به ربات دسترسی داری)

FILE_DIR = "my_files"
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

# منوی اصلی
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📤 ارسال فایل")],
            [KeyboardButton("📁 لیست فایل‌ها")],
        ],
        resize_keyboard=True
    )

# /start - فقط برای مالک ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه استفاده از این ربات را ندارید!")
        return

    await update.message.reply_text(
        "سلام! 📂 ربات مدیریت فایل شخصی تو آماده‌ست.\nاز منوی زیر انتخاب کن:",
        reply_markup=main_menu_keyboard()
    )

# دریافت و ذخیره فایل
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه استفاده از این ربات را ندارید!")
        return

    document = update.message.document
    if not document:
        await update.message.reply_text("❌ لطفاً فقط فایل بفرست، نه متن.")
        return

    # ذخیره file_id موقت تا بعداً نام بگیریم
    context.user_data["pending_file_id"] = document.file_id
    context.user_data["pending_file_name"] = document.file_name

    await update.message.reply_text("📌 چه نامی برای این فایل ذخیره کنم؟")

# دریافت نام و ذخیره فایل
async def get_file_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pending_file_id" not in context.user_data:
        await update.message.reply_text("❌ لطفاً ابتدا یک فایل ارسال کن.")
        return

    file_name = update.message.text.strip()
    file_id = context.user_data["pending_file_id"]

    file_path = os.path.join(FILE_DIR, file_name)

    # دریافت فایل و ذخیره
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ فایل با نام «{file_name}» ذخیره شد!")
    del context.user_data["pending_file_id"]

# نمایش لیست فایل‌ها
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه استفاده از این ربات را ندارید!")
        return

    files = os.listdir(FILE_DIR)
    if not files:
        await update.message.reply_text("📂 هنوز هیچ فایلی ذخیره نکردی.")
        return

    keyboard = [[InlineKeyboardButton(f"📄 {file}", callback_data=file)] for file in files]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("📁 لیست فایل‌های ذخیره‌شده:", reply_markup=reply_markup)

# ارسال فایل انتخاب‌شده
async def send_selected_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    file_name = query.data

    file_path = os.path.join(FILE_DIR, file_name)
    await query.message.reply_document(document=open(file_path, "rb"))

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, save_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_file_name))
    app.add_handler(MessageHandler(filters.Regex("^📁 لیست فایل‌ها$"), list_files))
    app.add_handler(CallbackQueryHandler(send_selected_file))

    print("📂 ربات مدیریت فایل شخصی آماده است!")
    app.run_polling()

if __name__ == "__main__":
    main()
