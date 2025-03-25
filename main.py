^ برای حل مشکل عدم ارسال فایل‌ها در گزینه "لیست فایل‌ها"، باید اطمینان حاصل کنیم که کد مربوط به لیست کردن فایل‌ها به درستی کار می‌کند و فایل‌ها را به درستی به کاربر نمایش می‌دهد. بیایید کد مربوط به لیست کردن فایل‌ها را بررسی و اصلاح کنیم.

### کد اصلاح شده برای لیست کردن فایل‌ها

```python
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        await update.message.reply_text("❌ شما مجاز به مشاهده این بخش نیستید.")
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
```

### نکات مهم:
1. **بررسی مجوز کاربر**: در ابتدا، بررسی می‌شود که آیا کاربر احراز هویت شده است یا خیر. اگر کاربر احراز هویت نشده باشد، پیامی مبنی بر عدم دسترسی ارسال می‌شود.
  
2. **لیست فایل‌ها**: با استفاده از `os.listdir(FILE_DIR)`، لیست فایل‌ها در دایرکتوری مشخص شده دریافت می‌شود. اگر هیچ فایلی وجود نداشته باشد، پیامی به کاربر ارسال می‌شود.

3. **ایجاد دکمه‌ها**: برای هر فایل، دو دکمه ایجاد می‌شود: یکی برای دانلود و دیگری برای حذف. این دکمه‌ها به کاربر اجازه می‌دهند تا فایل‌ها را مدیریت کند.

4. **ارسال پیام**: در نهایت، لیست فایل‌ها به همراه دکمه‌ها به کاربر ارسال می‌شود.

### اطمینان از کارکرد صحیح
- اطمینان حاصل کنید که دایرکتوری `files` وجود دارد و فایل‌هایی در آن ذخیره شده‌اند.
- همچنین، مطمئن شوید که توکن ربات و رمز عبور به درستی تنظیم شده‌اند و کاربر به درستی احراز هویت شده است.

### کد کامل
در اینجا کد کامل ربات با اصلاحات مربوط به لیست کردن فایل‌ها آورده شده است:

```python
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os

# تنظیمات اصلی
TOKEN = "توکن_ربات_تو"  # توکن رباتت رو اینجا بذار
PASSWORD = "12345"  # رمز ورود مخصوص خودت
FILE_DIR = "files"
os.makedirs(FILE_DIR, exist_ok=True)

# ساخت منوی اصلی
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📤 ارسال فایل")],
        [KeyboardButton("📁 لیست فایل‌ها")]
    ], resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["auth"] = False
    await update.message.reply_text("🔐 لطفاً رمز عبور را وارد کنید:")

# بررسی رمز
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("auth"):
        return False
    if update.message.text == PASSWORD:
        context.user_data["auth"] = True
        await update.message.reply_text("✅ ورود موفق! خوش اومدی ✌️", reply_markup=main_menu())
    else:
        await update.message.reply_text("❌ رمز اشتباهه! لطفاً دوباره تلاش کن.")
    return True

# انتخاب "📤 ارسال فایل"
async def upload_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("auth"):
        return
    context.user_data["waiting_for_file"] = True
    await update.message.reply_text("📎 لطفاً فایل یا عکس مورد نظر را ارسال کن.")

# دریافت فایل
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_file"):
        return
    file = update.message.document or (update.message.photo[-1] if update.message.photo else None)
    if not file:
        await update.message.reply_text("❗️ فقط فایل یا عکس بفرست.")
        return
    file_id = file.file_id
    file_type = "photo" if update.message.photo else "document"
