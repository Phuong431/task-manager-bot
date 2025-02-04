from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime
import os

# Token của bot Telegram
TOKEN = os.getenv("TOKEN")  # Lấy token từ biến môi trường trên Render

# Kết nối database
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

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

    # Thêm công việc mới
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO tasks (user_id, description, created_at, status)
    VALUES (?, ?, ?, ?)
    ''', (user_id, text, created_at, "Pending"))
    conn.commit()

    update.message.reply_text(
        f"✅ Đã ghi nhận công việc: {text}\n"
        f"📅 Tạo lúc: {created_at}"
    )

# Xem danh sách công việc chưa hoàn thành
def view_tasks(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    cursor.execute('''
    SELECT id, description, created_at FROM tasks
    WHERE user_id = ? AND status = "Pending"
    ''', (user_id,))
    tasks = cursor.fetchall()

    if not tasks:
        update.message.reply_text("🎉 Bạn không có công việc nào đang chờ xử lý.")
        return

    # Tạo danh sách nút chọn để hoàn thành công việc
    keyboard = [
        [InlineKeyboardButton(f"✅ {task[1]} (Tạo lúc: {task[2]})", callback_data=f"complete:{task[0]}")]
        for task in tasks
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "📋 Danh sách công việc chờ hoàn thành:",
        reply_markup=reply_markup
    )

# Đánh dấu hoàn thành công việc
def complete_task(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    task_id = query.data.split(":")[1]

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    UPDATE tasks
    SET status = "Completed", completed_at = ?
    WHERE id = ?
    ''', (completed_at, task_id))
    conn.commit()

    query.edit_message_text(
        text=f"🎉 Công việc đã hoàn thành! (ID: {task_id})\n"
        f"⏰ Hoàn thành lúc: {completed_at}"
    )

# Báo cáo tổng công việc theo trạng thái
def report(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    cursor.execute('''
    SELECT status, COUNT(*) FROM tasks
    WHERE user_id = ?
    GROUP BY status
    ''', (user_id,))
    data = cursor.fetchall()

    report_text = "**📊 Báo cáo công việc:**\n"
    total_tasks = 0
    for status, count in data:
        report_text += f"• {status}: {count} công việc\n"
        total_tasks += count

    report_text += f"\n**Tổng cộng:** {total_tasks} công việc"
    update.message.reply_text(report_text, parse_mode="Markdown")

# Cấu hình bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Xử lý tin nhắn
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Lệnh /view: Xem công việc chờ xử lý
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^Xem danh sách công việc$"), view_tasks))

    # Callback khi chọn hoàn thành công việc
    dispatcher.add_handler(CallbackQueryHandler(complete_task, pattern=r"^complete:\d+$"))

    # Lệnh /report: Báo cáo tổng công việc
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^Báo cáo công việc$"), report))

    # Khởi chạy bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
