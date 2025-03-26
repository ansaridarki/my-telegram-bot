import os
import sqlite3
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"

DB_PATH = "files.db"

# ایجاد دیتابیس و جدول
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            file_id TEXT,
            file_type TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ذخیره اطلاعات فایل در دیتابیس
def save_file_to_db(name, file_id, file_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO files (name, file_id, file_type) VALUES (?, ?, ?)', (name, file_id, file_type))
    conn.commit()
    conn.close()

# گرفتن لیست فایل‌ها
def get_files():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM files')
    files = c.fetchall()
    conn.close()
    return files

# گرفتن یک فایل خاص با آیدی
def get_file_by_id(file_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, file_id, file_type FROM files WHERE id = ?', (file_id,))
    result = c.fetchone()
    conn.close()
    return result

# حذف فایل
def delete_file(file_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()

# منوی اصلی
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📤 ارسال فایل")],
        [KeyboardButton("📁 لیست فایل‌ها")]
    ], resize_keyboard=True)

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! خوش اومدی 🙌", reply_markup=main_menu())

# ارسال فایل
async def prompt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["waiting_for_file"] = True
    await update.message.reply_text("لطفاً فایل مورد نظر رو بفرست...")

# دریافت فایل
async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_file"):
        return

    file = update.message.document or (update.message.photo[-1] if update.message.photo else None)
    if not file:
        await update.message.reply_text("❗ لطفاً فقط فایل یا عکس ارسال کن.")
        return

    context.user_data["file_id"] = file.file_id
    context.user_data["file_type"] = "photo" if update.message.photo else "document"
    context.user_data["waiting_for_name"] = True
    context.user_data["waiting_for_file"] = False

    await update.message.reply_text("📝 حالا یک نام دلخواه برای فایل وارد کن:")

# دریافت اسم فایل
async def receive_file_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_name"):
        return

    name = update.message.text.strip()
    file_id = context.user_data["file_id"]
    file_type = context.user_data["file_type"]

    save_file_to_db(name, file_id, file_type)

    await update.message.reply_text(f"✅ فایل «{name}» ذخیره شد!", reply_markup=main_menu())
    context.user_data.clear()

# لیست فایل‌ها
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = get_files()
    if not files:
        await update.message.reply_text("📂 فایلی ذخیره نشده.")
        return

    keyboard = []
    for file in files:
        keyboard.append([
            InlineKeyboardButton(f"📄 {file[1]}", callback_data=f"download|{file[0]}"),
            InlineKeyboardButton("🗑 حذف", callback_data=f"delete|{file[0]}")
        ])
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 لیست فایل‌ها:", reply_markup=markup)

# هندل دکمه‌ها
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, file_id = query.data.split("|")
    file_data = get_file_by_id(file_id)

    if not file_data:
        await query.message.reply_text("❌ فایل پیدا نشد.")
        return

    name, file_id, file_type = file_data

    if action == "download":
        if file_type == "photo":
            await query.message.reply_photo(file_id, caption=f"📷 {name}")
        else:
            await query.message.reply_document(file_id, caption=f"📄 {name}")
    elif action == "delete":
        delete_file(file_id=int(file_id))
        await query.message.reply_text(f"🗑 فایل «{name}» حذف شد.")

# اجرای ربات
def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📤 ارسال فایل$"), prompt_file))
    app.add_handler(MessageHandler(filters.Regex("^📁 لیست فایل‌ها$"), list_files))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, receive_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_file_name))
    app.add_handler(CallbackQueryHandler(handle_callbacks))

    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
