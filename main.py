from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"

FILE_DIR = "my_files"
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📤 ارسال فایل")],
            [KeyboardButton("📁 لیست فایل‌ها")],
        ],
        resize_keyboard=True
    )

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "سلام! ربات مدیریت فایل شخصی آماده‌ست. 👇",
        reply_markup=main_menu_keyboard()
    )

# وقتی کاربر گزینه "📤 ارسال فایل" رو میزنه
async def handle_upload_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["waiting_for_file"] = True
    await update.message.reply_text("لطفاً فایل مورد نظر رو بفرست 📎")

# وقتی فایل دریافت میشه
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_file"):
        await update.message.reply_text("⚠️ لطفاً اول گزینه «📤 ارسال فایل» رو بزن.")
        return

    document = update.message.document
    if not document:
        await update.message.reply_text("فقط فایل بفرست، نه متن.")
        return

    context.user_data["pending_file_id"] = document.file_id
    context.user_data["waiting_for_file"] = False
    context.user_data["waiting_for_filename"] = True

    await update.message.reply_text("چه نامی برای ذخیره‌ی این فایل انتخاب می‌کنی؟ 📝")

# دریافت نام فایل و ذخیره آن
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_filename"):
        return  # اگر منتظر نام نبود، کاری نکن

    file_name = update.message.text.strip()
    # جلوگیری از ذخیره‌سازی نام‌هایی که از منو هستن
    if file_name in ["📤 ارسال فایل", "📁 لیست فایل‌ها"]:
        await update.message.reply_text("❗ این نام قابل استفاده نیست. لطفاً یک نام مناسب وارد کن.")
        return

    file_id = context.user_data["pending_file_id"]
    file_path = os.path.join(FILE_DIR, file_name)

    try:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"✅ فایل با نام «{file_name}» ذخیره شد.", reply_markup=main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text("❌ خطا در ذخیره‌سازی فایل.")

    context.user_data.clear()

# لیست فایل‌ها
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    files = os.listdir(FILE_DIR)
    if not files:
        await update.message.reply_text("📂 هنوز فایلی ذخیره نشده.")
        return

    keyboard = [[InlineKeyboardButton(f"📄 {file}", callback_data=file)] for file in files]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 فایل‌های ذخیره‌شده:", reply_markup=reply_markup)

# ارسال فایل انتخاب‌شده از لیست
async def send_selected_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_name = query.data
    file_path = os.path.join(FILE_DIR, file_name)

    if os.path.exists(file_path):
        await query.message.reply_document(document=open(file_path, "rb"))
    else:
        await query.message.reply_text("❌ فایل پیدا نشد.")

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📤 ارسال فایل$"), handle_upload_mode))
    app.add_handler(MessageHandler(filters.Regex("^📁 لیست فایل‌ها$"), list_files))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_file))
    app.add_handler(CallbackQueryHandler(send_selected_file))

    print("📦 ربات روشنه...")
    app.run_polling()

if __name__ == "__main__":
    main()
