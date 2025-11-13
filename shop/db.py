import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('telegram_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY,
        title TEXT,
        price INTEGER
    )
''')

conn.commit()

# Добавление пользователя
def add_user(user_id, username):
    cursor.execute('''
        INSERT INTO users (user_id, username, balance)
        VALUES (?, ?, 0)
        ON CONFLICT(user_id) DO NOTHING
    ''', (user_id, username))
    conn.commit()

# Получение баланса пользователя
def get_user_balance(user_id):
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# Обновление баланса
def update_user_balance(user_id, new_balance):
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()

# Добавление книги
def add_book(title, price):
    cursor.execute('''
        INSERT INTO books (title, price)
        VALUES (?, ?)
    ''', (title, price))
    conn.commit()

# Получение списка книг
def get_books():
    cursor.execute('SELECT book_id, title, price FROM books')
    return cursor.fetchall()

# Получение информации о книге
def get_book_by_id(book_id):
    cursor.execute('SELECT price FROM books WHERE book_id = ?', (book_id,))
    return cursor.fetchone()

# Получение списка всех пользователей
def get_all_users():
    cursor.execute('SELECT user_id FROM users')
    return cursor.fetchall()
