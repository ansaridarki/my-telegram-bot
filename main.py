from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

# 🔐 تنظیمات
TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"  # توکن ربات شما
BOT_PASSWORD = "1899"  # رمز عبور دلخواه

# 📁 مسیر ذخیره‌سازی فایل‌ها
FILE_DIR = "my_files"
os.makedirs(FILE_DIR, exist_ok=True)

# 🎛 کیبورد اصلی
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📤 ارسال فایل")],
        [KeyboardButton("📁 لیست فایل‌ها")],
        [KeyboardButton("🗑️ حذف فایل دلخواه")],
    ], resize_keyboard=True)

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["auth"] = False
    await update.message.reply_text("🔐 لطفاً رمز عبور را وارد کنید:")

# 🔐 بررسی رمز
async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("auth"):
        return False

    if update.message.text == BOT_PASSWORD:
        context.user_data["auth"] = True
        await update.message.reply_text("✅ ورود موفق! خوش اومدی 🤖", reply_markup=main_menu())
    else:
        await update.message.reply_text("❌ رمز اشتباهه! دوباره تلاش کن.")
    return True

# 📤 ارسال فایل - فعال کردن حالت آپلود
async def handle_upload_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        return
    
    # برای اطمینان از اینکه پیام در اینجا ارسال می‌شود
    context.user_data.clear()
    context.user_data["waiting_for_file"] = True
    await update.message.reply_text("در حال انتظار برای دریافت فایل... 📎")

# 📥 دریافت فایل
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_file"):
        return

    if update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
    else:
        await update.message.reply_text("❗ فقط فایل یا عکس بفرست.")
        return

    context.user_data["pending_file_id"] = file_id
    context.user_data["file_type"] = file_type
    context.user_data["waiting_for_filename"] = True
    context.user_data["waiting_for_file"] = False

    await update.message.reply_text("📝 چه نامی برای این فایل انتخاب می‌کنی؟")

# 💾 ذخیره فایل
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_filename"):
        return

    name = update.message.text.strip()
    if name in ["📤 ارسال فایل", "📁 لیست فایل‌ها", "🗑️ حذف فایل دلخواه"]:
        await update.message.reply_text("❗ این اسم قابل قبول نیست. یه اسم دیگه بده.")
        return

    file_id = context.user_data["pending_file_id"]
    file_type = context.user_data["file_type"]
    
    # ایجاد دایرکتوری خاص برای هر کاربر با استفاده از user_id
    user_id = update.message.from_user.id
    user_file_dir = os.path.join(FILE_DIR, str(user_id))
    os.makedirs(user_file_dir, exist_ok=True)

    file_path = os.path.join(user_file_dir, name)
    if file_type == "photo":
        file_path += ".jpg"

    file = await context.bot.get_file(file_id)
    await file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ فایل با نام «{os.path.basename(file_path)}» ذخیره شد.", reply_markup=main_menu())
    context.user_data.clear()

# 📁 لیست فایل‌ها
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        return

    # ایجاد دایرکتوری خاص برای هر کاربر با استفاده از user_id
    user_id = update.message.from_user.id
    user_file_dir = os.path.join(FILE_DIR, str(user_id))
    
    os.makedirs(user_file_dir, exist_ok=True)

    files = os.listdir(user_file_dir)
    if not files:
        await update.message.reply_text("❗ هنوز فایلی ذخیره نشده.")
        return

    keyboard = [
        [InlineKeyboardButton(f"📄 {f}", callback_data=f"download|{f}"),
         InlineKeyboardButton("🗑️ حذف", callback_data=f"delete|{f}")]
        for f in files
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 فایل‌های ذخیره شده:", reply_markup=markup)

# ⬇️ دریافت یا حذف فایل
async def handle_file_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, filename = query.data.split("|")
    
    # ایجاد دایرکتوری خاص برای هر کاربر با استفاده از user_id
    user_id = query.from_user.id
    user_file_dir = os.path.join(FILE_DIR, str(user_id))
    file_path = os.path.join(user_file_dir, filename)

    if action == "download":
        if os.path.exists(file_path):
            await query.message.reply_document(document=open(file_path, "rb"))
        else:
            await query.message.reply_text("❌ فایل وجود ندارد.")
    elif action == "delete":
        if os.path.exists(file_path):
            os.remove(file_path)
            await query.message.reply_text(f"🗑️ فایل «{filename}» حذف شد.")
        else:
            await query.message.reply_text("❌ فایل پیدا نشد.")

# 🧠 اجرای اصلی
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))
    app.add_handler(MessageHandler(filters.Regex("^📤 ارسال فایل$"), handle_upload_request))
    app.add_handler(MessageHandler(filters.Regex("^📁 لیست فایل‌ها$"), list_files))
    app.add_handler(MessageHandler(filters.Regex("^🗑️ حذف فایل دلخواه$"), handle_upload_request))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_file))
    app.add_handler(CallbackQueryHandler(handle_file_action))

    print("✅ ربات راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
