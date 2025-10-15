# bot.py
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta
import database as db
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем клавиатуру для главного меню
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📝 Добавить задачу")],
        [KeyboardButton("📋 Все задачи"), KeyboardButton("📅 Задачи на сегодня")],
        [KeyboardButton("🚀 Задачи на завтра"), KeyboardButton("✅ Выполненные")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! Я бот для управления твоими задачами.\n"
        "Выбери действие в меню ниже:",
        reply_markup=main_menu_keyboard()
    )

# Обработчик текстовых сообщений (кнопки главного меню)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "📝 Добавить задачу":
        await update.message.reply_text("Введите задачу в формате:\n\n`Задача / 2024-12-31 18:30`\n\nДата и время необязательны.", parse_mode='Markdown')
        # Можно добавить более сложный многошаговый сценарий через ConversationHandler
        return

    elif text == "📋 Все задачи":
        tasks = db.get_tasks(user_id, "all")
        await show_task_list(update, tasks, "Все задачи:")

    elif text == "📅 Задачи на сегодня":
        tasks = db.get_tasks(user_id, "today")
        await show_task_list(update, tasks, "Задачи на сегодня:")

    elif text == "🚀 Задачи на завтра":
        tasks = db.get_tasks(user_id, "tomorrow")
        await show_task_list(update, tasks, "Задачи на завтра:")

    elif text == "✅ Выполненные":
        # Для простоты покажем все задачи и отметим выполненные
        tasks = db.get_tasks(user_id, "all")
        done_tasks = [t for t in tasks if t[3] == 1]  # is_done == 1
        await show_task_list(update, done_tasks, "Выполненные задачи:")

    else:
        # Пытаемся разобрать сообщение как новую задачу
        if " / " in text:
            parts = text.split(" / ", 1)
            task_text = parts[0].strip()
            due_date_str = parts[1].strip() if len(parts) > 1 else None

            # Простая валидация даты (можно улучшить)
            due_date = None
            if due_date_str:
                try:
                    # Пробуем распарсить дату
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    await update.message.reply_text("Неверный формат даты. Используйте: ГГГГ-ММ-ДД ЧЧ:ММ")
                    return

            db.add_task(user_id, task_text, due_date)
            reply_text = f"Задача добавлена: *{task_text}*"
            if due_date:
                reply_text += f"\nНапоминание: {due_date}"
            await update.message.reply_text(reply_text, parse_mode='Markdown')
        else:
            # Если формат не распознан, просто добавляем задачу без даты
            db.add_task(user_id, text)
            await update.message.reply_text(f"Задача добавлена: *{text}*", parse_mode='Markdown')

# Вспомогательная функция для отображения списка задач
async def show_task_list(update, tasks, title):
    if not tasks:
        await update.message.reply_text("Задач нет.")
        return

    task_list = f"*{title}*\n\n"
    for task in tasks:
        task_id, task_text, due_date, is_done = task
        status = "✅" if is_done else "⏳"
        date_str = f" ({due_date})" if due_date else ""
        task_list += f"{status} {task_text}{date_str} [/done{task_id}] [/del{task_id}]\n"

    await update.message.reply_text(task_list, parse_mode='Markdown')

# Обработчик для inline-кнопок (можно заменить на обработку сообщений с /done и /del)
# Для простоты сделаем обработку текстовых команд /done и /del
async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text.startswith('/done'):
        try:
            task_id = int(text[5:])  # Извлекаем ID из /done123
            db.mark_task_done(task_id, user_id)
            await update.message.reply_text("Задача отмечена как выполненная! ✅")
        except (ValueError, IndexError):
            await update.message.reply_text("Неверный формат команды.")

    elif text.startswith('/del'):
        try:
            task_id = int(text[4:])  # Извлекаем ID из /del123
            db.delete_task(task_id, user_id)
            await update.message.reply_text("Задача удалена! 🗑️")
        except (ValueError, IndexError):
            await update.message.reply_text("Неверный формат команды.")

def main():
    # Создаем приложение и передаем ему токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Regex(r'^/(done|del)\d+'), handle_command))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()