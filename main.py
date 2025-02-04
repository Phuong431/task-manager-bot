from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
from datetime import datetime
import time

# Thay YOUR_BOT_TOKEN bằng token API của bạn
TOKEN = "7243466598:AAGWDoDcUT3j6xDaeU37RNFLlxSJceuO_IY"

# Kết nối cơ sở dữ liệu SQLite
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng công việc
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

# Lệnh /start: Chào mừng người dùng
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Xin chào! Tôi là bot quản lý công việc.\n"
        "Các lệnh bạn có thể sử dụng:\n"
        "• /add [Mô tả công việc] - Thêm công việc mới\n"
        "• /done [ID công việc] - Đánh dấu công việc hoàn thành\n"
        "• /view - Xem công việc hôm nay\n"
        "• /report - Báo cáo công việc tháng này\n"
    )

# Lệnh /add: Thêm công việc mới
def add_task(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    text = " ".join(context.args)

    if not text:
        update.message.reply_text("⚠️ Vui lòng nhập mô tả công việc. Ví dụ: `/add Làm báo cáo`")
        return

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Thời gian hiện tại
    cursor.execute('''
    INSERT INTO tasks (user_id, description, created_at, status) VALUES (?, ?, ?, ?)
    ''', (user_id, text, created_at, "Pending"))
    conn.commit()

    update.message.reply_text(f"✅ Ghi nhận công việc: {text} (Tạo lúc: {created_at})")

# Lệnh /done: Đánh dấu công việc hoàn thành
def mark_done(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    task_id = " ".join(context.args)

    if not task_id.isdigit():
        update.message.reply_text("⚠️ Vui lòng nhập ID công việc bạn muốn đánh dấu hoàn thành.")
        return

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Thời gian hoàn thành
    cursor.execute('''
    SELECT created_at FROM tasks WHERE id = ? AND user_id = ? AND status = "Pending"
    ''', (task_id, user_id))
    task = cursor.fetchone()

    if not task:
        update.message.reply_text(f"⚠️ Không tìm thấy công việc với ID {task_id}.")
        return

    created_at = datetime.strptime(task[0], "%Y-%m-%d %H:%M:%S")
    completed_at_dt = datetime.strptime(completed_at, "%Y-%m-%d %H:%M:%S")
    time_taken = completed_at_dt - created_at  # Tính tổng thời gian hoàn thành

    cursor.execute('''
    UPDATE tasks SET status = "Done", completed_at = ? WHERE id = ? AND user_id = ?
    ''', (completed_at, task_id, user_id))
    conn.commit()

    update.message.reply_text(
        f"✅ Công việc ID {task_id} đã hoàn thành.\n"
        f"⏰ Tổng thời gian hoàn thành: {time_taken}."
    )

# Lệnh /view: Xem công việc hôm nay
def view_tasks(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    SELECT id, description, created_at FROM tasks
    WHERE user_id = ? AND status = "Pending"
    ''', (user_id,))
    tasks = cursor.fetchall()

    if not tasks:
        update.message.reply_text("📋 Bạn không có công việc nào cần làm hôm nay.")
    else:
        message = "**📋 Công việc cần làm hôm nay:**\n"
        for task in tasks:
            message += f"• ID {task[0]}: {task[1]} (Tạo lúc: {task[2]})\n"
        update.message.reply_text(message, parse_mode="Markdown")

# Lệnh /report: Báo cáo công việc hàng tháng
def report(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    current_month = datetime.now().strftime("%Y-%m")

    cursor.execute('''
    SELECT description, created_at, completed_at, status FROM tasks
    WHERE user_id = ? AND strftime('%Y-%m', created_at) = ?
    ''', (user_id, current_month))
    tasks = cursor.fetchall()

    if not tasks:
        update.message.reply_text("📊 Không có công việc nào trong tháng này.")
    else:
        message = "**📊 Báo cáo công việc tháng này:**\n"
        for task in tasks:
            message += f"• {task[0]} (Tạo: {task[1]}, Hoàn thành: {task[2]}, Trạng thái: {task[3]})\n"
        update.message.reply_text(message, parse_mode="Markdown")

# Khởi chạy bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_task))
    dispatcher.add_handler(CommandHandler("done", mark_done))
    dispatcher.add_handler(CommandHandler("view", view_tasks))
    dispatcher.add_handler(CommandHandler("report", report))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
import os

PORT = int(os.environ.get('PORT', '8443'))
updater.start_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN
)
updater.bot.set_webhook(f"https://<https://task-manager-bot-1.onrender.com>/{TOKEN}")
updater.idle()

