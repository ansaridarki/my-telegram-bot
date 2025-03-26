from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import sqlite3
import os

# --- تنظیمات ---
BOT_TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"

# --- دیتابیس ---
conn = sqlite3.connect("files.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS files (name TEXT, file_id TEXT)")
conn.commit()

# --- کیبورد اصلی ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📤 ارسال فایل"), KeyboardButton("🗑 حذف فایل")],
        [KeyboardButton("📁 لیست فایل‌ها")]
    ],
    resize_keyboard=True
)

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! خوش اومدی 😊 یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=main_keyboard)

# --- هندل ارسال فایل ---
user_states = {}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📤 ارسال فایل":
        user_states[update.effective_user.id] = "waiting_for_file"
        await update.message.reply_text("منتظرم فایلت رو بفرستی...")

    elif text == "📁 لیست فایل‌ها":
        cursor.execute("SELECT name FROM files")
        rows = cursor.fetchall()
        if not rows:
            await update.message.reply_text("📂 هیچ فایلی وجود نداره!")
        else:
            msg = "📁 لیست فایل‌ها:\n\n" + "\n".join(f"• {r[0]}" for r in rows)
            await update.message.reply_text(msg)

    elif text == "🗑 حذف فایل":
        cursor.execute("SELECT name FROM files")
        rows = cursor.fetchall()
        if not rows:
            await update.message.reply_text("هیچ فایلی برای حذف وجود نداره ❌")
        else:
            keyboard = [
                [InlineKeyboardButton(text=row[0], callback_data=f"delete:{row[0]}")]
                for row in rows
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("کدوم فایل رو میخوای حذف کنی؟", reply_markup=reply_markup)

    elif user_states.get(update.effective_user.id) == "waiting_for_filename":
        context.user_data["filename"] = text
        await update.message.reply_text("نام ثبت شد. حالا فایلت رو بفرست.")
        user_states[update.effective_user.id] = "waiting_for_file_upload"

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)

    file = update.message.document or update.message.video or update.message.audio or update.message.photo[-1] if update.message.photo else None

    if not file:
        await update.message.reply_text("❌ لطفاً یک فایل معتبر ارسال کن.")
        return

    if state == "waiting_for_file":
        await update.message.reply_text("اسم دلخواهت برای فایل چیه؟")
        user_states[user_id] = "waiting_for_filename"

    elif state == "waiting_for_file_upload":
        file_id = file.file_id
        name = context.user_data.get("filename", "بدون‌نام")

        cursor.execute("INSERT INTO files (name, file_id) VALUES (?, ?)", (name, file_id))
        conn.commit()

        await update.message.reply_text(f"✅ فایل «{name}» ذخیره شد!")
        user_states[user_id] = None

# --- حذف فایل ---
async def delete_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete:"):
        file_name = query.data.split(":", 1)[1]

        cursor.execute("DELETE FROM files WHERE name = ?", (file_name,))
        conn.commit()

        await query.edit_message_text(f"✅ فایل «{file_name}» حذف شد!")

# --- راه‌اندازی ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL | filters.PHOTO, handle_file))
    app.add_handler(CallbackQueryHandler(delete_file_callback))

    print("🤖 ربات آماده است...")
    app.run_polling()

if __name__ == "__main__":
    main()
