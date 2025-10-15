# database.py
import sqlite3
import datetime

def init_db():
    """Инициализация базы данных и создание таблицы, если её нет"""
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_text TEXT NOT NULL,
            due_date TEXT,  -- Будем хранить в формате YYYY-MM-DD HH:MM
            is_done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_task(user_id, task_text, due_date=None):
    """Добавление новой задачи"""
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (user_id, task_text, due_date) VALUES (?, ?, ?)',
                (user_id, task_text, due_date))
    conn.commit()
    conn.close()

def get_tasks(user_id, period="all"):
    """Получение задач пользователя"""
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    if period == "today":
        cur.execute('SELECT id, task_text, due_date, is_done FROM tasks WHERE user_id=? AND date(due_date)=? ORDER BY due_date', (user_id, today))
    elif period == "tomorrow":
        cur.execute('SELECT id, task_text, due_date, is_done FROM tasks WHERE user_id=? AND date(due_date)=? ORDER BY due_date', (user_id, tomorrow))
    else:  # "all"
        cur.execute('SELECT id, task_text, due_date, is_done FROM tasks WHERE user_id=? ORDER BY due_date', (user_id,))
    
    tasks = cur.fetchall()
    conn.close()
    return tasks

def mark_task_done(task_id, user_id):
    """Отметка задачи как выполненной"""
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET is_done=1 WHERE id=? AND user_id=?', (task_id, user_id))
    conn.commit()
    conn.close()

def delete_task(task_id, user_id):
    """Удаление задачи"""
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id=? AND user_id=?', (task_id, user_id))
    conn.commit()
    conn.close()

# Инициализируем базу при импорте
init_db()