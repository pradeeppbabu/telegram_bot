import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in environment variables")

# =========================
# FILES CONFIG
# =========================
FILES_DIR = "files"   # files folder

# =========================
# ANTI-FRAUD MEMORY
# =========================
downloaded_users = {}  # user_id -> set(files)

# =========================
# UTILITY: GET FILE LIST
# =========================
def get_available_files():
    if not os.path.exists(FILES_DIR):
        return []

    return [
        f for f in os.listdir(FILES_DIR)
        if os.path.isfile(os.path.join(FILES_DIR, f))
        and f.lower().endswith(".pdf")   # 👈 ONLY PDF
    ]
# =========================
# /start COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TNPSC Resources Bot 😊\n\n"
        "📂 Available PDFs & files பார்க்க:\n"
        "👉 /files"
    )

# =========================
# /files COMMAND
# =========================
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = get_available_files()

    if not files:
        await update.message.reply_text("❌ Currently no files available.")
        return

    keyboard = [
        [InlineKeyboardButton(text=f, callback_data=f"GETFILE::{f}")]
        for f in files
    ]

    await update.message.reply_text(
        "📂 Available Files:\nSelect the file you want 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# TEXT MESSAGE HANDLER
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip().lower()

    if text in ["hi", "hello", "hai"]:
        await update.message.reply_text(
            "👋 Hi! Welcome to TNPSC Resources Bot 😊\n\n"
            "📂 Files பார்க்க 👉 /files"
        )
        return

    await update.message.reply_text(
        "ℹ️ Please use commands:\n"
        "/files – View available files"
    )

# =========================
# FILE DOWNLOAD HANDLER
# =========================
async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not data.startswith("GETFILE::"):
        return

    filename = data.replace("GETFILE::", "")
    file_path = os.path.join(FILES_DIR, filename)

    if not os.path.exists(file_path):
        await query.message.reply_text("❌ File not found.")
        return

    user_files = downloaded_users.get(user_id, set())
    if filename in user_files:
        await query.message.reply_text("⚠️ You already downloaded this file.")
        return

    downloaded_users.setdefault(user_id, set()).add(filename)

    await query.message.reply_text("⬇️ Downloading your file...")

    with open(file_path, "rb") as f:
        await query.message.reply_document(
            document=f,
            caption=f"📄 {filename}\n\nAll the best 💪"
        )

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("files", list_files))
    app.add_handler(CallbackQueryHandler(file_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot is running securely...")
    app.run_polling()

if __name__ == "__main__":
    main()
