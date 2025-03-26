from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

# 🔐 تنظیمات
TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"
PASSWORD = "12345"       # ← رمز ورود مخصوص خودت
FILE_DIR = "files"
os.makedirs(FILE_DIR, exist_ok=True)

# 📋 منوی اصلی
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📤 ارسال فایل")],
        [KeyboardButton("📁 لیست فایل‌ها")]
    ], resize_keyboard=True)

# 🚪 استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["auth"] = False
    await update.message.reply_text("🔐 لطفاً رمز عبور را وارد کنید:")

# 🧠 بررسی رمز
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == PASSWORD:
        context.user_data["auth"] = True
        await update.message.reply_text("✅ ورود موفق! خوش اومدی ✌️", reply_markup=main_menu())
    else:
        await update.message.reply_text("❌ رمز اشتباهه! لطفاً دوباره تلاش کن.")

# 🔒 هندلر شرطی برای رمز
async def handle_password_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        await handle_password(update, context)

# ➕ درخواست ارسال فایل
async def upload_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        await update.message.reply_text("❌ ابتدا باید وارد شوید. لطفاً رمز را وارد کنید.")
        return
    context.user_data.clear()
    context.user_data["auth"] = True
    context.user_data["waiting_for_file"] = True
    await update.message.reply_text("📡 منتظر ارسال فایل هستم...")

# 📎 دریافت فایل
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_file"):
        return
    file = update.message.document or (update.message.photo[-1] if update.message.photo else None)
    if not file:
        await update.message.reply_text("❗ لطفاً فقط فایل یا عکس ارسال کن.")
        return

    context.user_data["pending_file_id"] = file.file_id
    context.user_data["file_type"] = "photo" if update.message.photo else "document"
    context.user_data["waiting_for_filename"] = True
    context.user_data["waiting_for_file"] = False

    await update.message.reply_text("📝 لطفاً یک نام دلخواه برای فایل وارد کن:")

# 💾 ذخیره فایل با نام دلخواه
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_filename"):
        return

    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("❗ لطفاً یک نام معتبر وارد کن.")
        return

    file_id = context.user_data["pending_file_id"]
    file_type = context.user_data["file_type"]
    file_path = os.path.join(FILE_DIR, name)

    if file_type == "photo" and not file_path.lower().endswith(".jpg"):
        file_path += ".jpg"

    telegram_file = await context.bot.get_file(file_id)
    await telegram_file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ فایل با نام «{os.path.basename(file_path)}» ذخیره شد.", reply_markup=main_menu())
    context.user_data.clear()
    context.user_data["auth"] = True  # حفظ ورود بعد از ذخیره فایل

# 📁 لیست فایل‌ها
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        await update.message.reply_text("❌ ابتدا باید وارد شوید. لطفاً رمز را وارد کنید.")
        return

    files = os.listdir(FILE_DIR)
    if not files:
        await update.message.reply_text("📂 هنوز فایلی ذخیره نشده.")
        return

    keyboard = []
    for f in files:
        keyboard.append([
            InlineKeyboardButton(f"📄 {f}", callback_data=f"download|{f}"),
            InlineKeyboardButton("🗑 حذف", callback_data=f"delete|{f}")
        ])

    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 لیست فایل‌ها:", reply_markup=markup)

# 🧾 مدیریت دانلود/حذف
async def handle_file_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, filename = query.data.split("|", 1)
    filepath = os.path.join(FILE_DIR, filename)

    if action == "download":
        if os.path.exists(filepath):
            await query.message.reply_document(document=open(filepath, "rb"))
        else:
            await query.message.reply_text("❌ فایل پیدا نشد.")
    elif action == "delete":
        if os.path.exists(filepath):
            os.remove(filepath)
            await query.message.reply_text(f"🗑 فایل «{filename}» حذف شد.")
        else:
            await query.message.reply_text("❌ فایل پیدا نشد.")

# ▶️ اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_filter))
    app.add_handler(MessageHandler(filters.Regex("^📤 ارسال فایل$"), upload_request))
    app.add_handler(MessageHandler(filters.Regex("^📁 لیست فایل‌ها$"), list_files))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_file))
    app.add_handler(CallbackQueryHandler(handle_file_action))

    print("🤖 ربات روشنه... برو تستش کن!")
    app.run_polling()

if __name__ == "__main__":
    main()
