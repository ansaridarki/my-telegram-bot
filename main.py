from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = "7764863274:AAFuvcTiox1jkx84j-4MG86FbnGGFINmsx4"

SONG_DIR = "songs"

# ایجاد پوشه اگه وجود نداشت
if not os.path.exists(SONG_DIR):
    os.makedirs(SONG_DIR)

# صفحه کلید اصلی
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎵 ارسال آهنگ")],
            [KeyboardButton("⬇️ دانلود آهنگ"), KeyboardButton("🎼 لیست آهنگ‌هام")],
            [KeyboardButton("🗑 حذف آهنگ")]
        ],
        resize_keyboard=True
    )

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 🎶 لطفاً یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=main_menu_keyboard()
    )

# هندلر دکمه‌ها
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬇️ دانلود آهنگ":
        await update.message.reply_text("اسم آهنگی که می‌خوای دانلود کنی رو بفرست 🎼")
    elif text == "🎵 ارسال آهنگ":
        await update.message.reply_text("لطفاً آهنگ مورد نظرت رو ارسال کن تا ذخیره کنم 🎧")
    elif text == "🗑 حذف آهنگ":
        await update.message.reply_text("اسم آهنگی که می‌خوای حذف کنی رو بفرست ❌")
    elif text == "🎼 لیست آهنگ‌هام":
        await list_songs(update)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

# ذخیره آهنگ با نام اختصاصی
async def save_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    audio = update.message.audio or update.message.voice or update.message.document

    if not audio:
        await update.message.reply_text("فقط فایل صوتی بفرست لطفاً 🎧")
        return

    file = await context.bot.get_file(audio.file_id)
    
    file_name = audio.file_name if hasattr(audio, "file_name") else f"song_{audio.file_id}.mp3"
    file_path = os.path.join(SONG_DIR, f"{user_id}_{file_name}")

    await file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ آهنگ {file_name} ذخیره شد!")

# لیست آهنگ‌های کاربر
async def list_songs(update: Update):
    user_id = update.message.from_user.id
    user_files = [f.split("_", 1)[1] for f in os.listdir(SONG_DIR) if f.startswith(str(user_id))]

    if user_files:
        song_list = "\n".join(user_files)
        await update.message.reply_text(f"🎼 آهنگ‌های شما:\n{song_list}\n\nبرای دانلود یا حذف، اسم آهنگ رو بفرست.")
    else:
        await update.message.reply_text("❌ شما هنوز هیچ آهنگی ذخیره نکردی.")

# دانلود آهنگ
async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    song_name = update.message.text.strip()

    file_path = os.path.join(SONG_DIR, f"{user_id}_{song_name}")

    if os.path.exists(file_path):
        await update.message.reply_audio(audio=open(file_path, "rb"))
    else:
        await update.message.reply_text("❌ چنین آهنگی پیدا نشد. لطفاً اسم درست رو بفرست.")

# حذف آهنگ
async def delete_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    song_name = update.message.text.strip()

    file_path = os.path.join(SONG_DIR, f"{user_id}_{song_name}")

    if os.path.exists(file_path):
        os.remove(file_path)
        await update.message.reply_text(f"🗑 آهنگ {song_name} حذف شد!")
    else:
        await update.message.reply_text("❌ چنین آهنگی پیدا نشد.")

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.Document.AUDIO, save_song))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\w+\.\w+$"), download_song))  # تشخیص دانلود
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\w+\.\w+$"), delete_song))  # تشخیص حذف

    print("🎧 ربات با مدیریت آهنگ‌ها آماده‌ست!")
    app.run_polling()

if __name__ == "__main__":
    main()
