from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime
import os
import threading

# Token của bot Telegram
TOKEN = os.getenv("TOKEN")  # Lấy token từ biến môi trường trên Render

# Kết nối database
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# Khóa để bảo vệ truy cập SQLite
db_lock = threading.Lock()

# Tạo bảng lưu công việc
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    description TEXT,
    created_at TEXT,
    completed_at TEXT,
    status TEXT
)
''')
conn.commit()

# Xử lý tin nhắn người dùng gửi
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    text = update.message.text.strip()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with db_lock:
        cursor.execute('''
        INSERT INTO tasks (user_id, description, created_at, status)
        VALUES (?, ?, ?, ?)
        ''', (user_id, text, created_at, "Pending"))
        conn.commit()

    update.message.reply_text(
        f"✅ Đã ghi nhận công việc: {text}\n"
        f"📅 Tạo lúc: {created_at}"
    )

