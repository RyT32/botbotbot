import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import db  # Импортируем файл db.py для работы с базой данных
import os

API_TOKEN = '7550081505:AAFveyw_AxpWrAWbyJtWsOFxNjAUIQfhwOA'
bot = telebot.TeleBot(API_TOKEN)

# Путь к папке с книгами
dirname=os.path.dirname
path = os.path.join(dirname(dirname(__file__)), r'shop\books')
BOOKS_FOLDER = path

ADMIN_ID = 123456789  # Замените на настоящий ID администратора


# Функция для создания основной клавиатуры с кнопками "Кликер" и "Каталог"
def create_main_menu():
    markup = InlineKeyboardMarkup()
    button_clicker = InlineKeyboardButton(text="Кликер", callback_data="clicker")
    button_catalog = InlineKeyboardButton(text="Каталог", callback_data="catalog")
    markup.add(button_clicker, button_catalog)
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Добавляем пользователя в базу данных
    db.add_user(user_id, username)

    # Приветствие и вывод меню
    bot.send_message(message.chat.id, "Добро пожаловать в магазин! Выберите действие:", reply_markup=create_main_menu())

# Обработка кнопки "Кликер" для пополнения баланса
@bot.callback_query_handler(func=lambda call: call.data == 'clicker')
def process_clicker(call):
    user_id = call.from_user.id
    current_balance = db.get_user_balance(user_id)
    new_balance = current_balance + 1
    db.update_user_balance(user_id, new_balance)

    # Обновляем сообщение с текущим балансом в том же сообщении
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"Ваш баланс: {new_balance}\n\nВыберите действие:", reply_markup=create_main_menu())

# Обработка кнопки "Каталог"
@bot.callback_query_handler(func=lambda call: call.data == 'catalog')
def show_catalog(call):
    books = db.get_books()
    if books:
        markup = InlineKeyboardMarkup()
        for book in books:
            markup.add(InlineKeyboardButton(text=f"{book[1]} — {book[2]} монет", callback_data=f"buy_{book[0]}"))
        markup.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))

        # Обновляем сообщение, выводя каталог книг с inline-кнопками для покупки
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="Доступные книги:", reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="В магазине пока нет книг.", reply_markup=create_main_menu())

# Обработка возврата к главному меню
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text="Выберите действие:", reply_markup=create_main_menu())

# Обработка покупки книги
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_purchase(call):
    user_id = call.from_user.id
    book_id = int(call.data.split('_')[-1])

    # Получаем информацию о книге и балансе
    book = db.get_book_by_id(book_id)
    if not book:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="Книга не найдена.", reply_markup=create_main_menu())
        return
    
    price = book[0]
    current_balance = db.get_user_balance(user_id)

    # Проверяем, хватает ли у пользователя средств
    if current_balance >= price:

        # Отправка файла книги пользователю
        book_file_path = os.path.join(BOOKS_FOLDER, f"{book_id}.pdf")  # или другое расширение
        print(book_file_path)
        if os.path.exists(book_file_path):
            with open(book_file_path, 'rb') as book_file:
                bot.send_document(user_id, book_file)

            new_balance = current_balance - price
            db.update_user_balance(user_id, new_balance)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=f"Вы успешно купили книгу. Ваш новый баланс: {new_balance}", 
                                  reply_markup=create_main_menu())
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text="Извините, файл книги не найден.", reply_markup=create_main_menu())
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"Недостаточно средств для покупки. Ваш баланс: {current_balance}", 
                              reply_markup=create_main_menu())


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "Введите сообщение для рассылки:")
        bot.register_next_step_handler(msg, send_broadcast)
    else:
        bot.send_message(message.chat.id, "У вас нет прав для использования этой команды.")

def send_broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text
        users = db.get_all_users()
        for user in users:
            try:
                bot.send_message(user[0], text)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user[0]}: {e}")
        bot.send_message(message.chat.id, "Рассылка завершена.")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для использования этой команды.")




bot.infinity_polling()

