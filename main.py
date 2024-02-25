import sqlite3
import hashlib
import pickle
import telebot

# Словарь для хранения объектов, доступных пользователям
objects = {}

# Словарь для определения прав доступа к объектам
access_matrix = {}


def is_user_registered(username):
    connection = sqlite3.connect("tokb.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return count > 0


def add_user_to_db(username, password, permission):
    connection = sqlite3.connect("tokb.db")
    cursor = connection.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password, permission) VALUES (?, ?, ?)",
                       (username, hashed_password, permission))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        cursor.close()
        connection.close()


def authenticate_user(username, password):
    connection = sqlite3.connect("tokb.db")
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    hashed_password = cursor.fetchone()
    cursor.close()
    connection.close()
    if hashed_password is None:
        return False
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password[0]


def main():
    try:
        # Загрузка переменных из pickle
        with open("variables.pkl", "rb") as f:
            variables = pickle.load(f)

        # Создание экземпляра TeleBot
        bot = telebot.TeleBot('')

        # Обработка команды /start
        @bot.message_handler(commands=['start'])
        def start_command(message):
            bot.send_photo(message.chat.id, variables["start_pic"])
            bot.send_message(message.chat.id, "Добро пожаловать!")
            ask_credentials(bot, message, variables)

        # Обработка команды /cancel
        @bot.message_handler(commands=['cancel'])
        def quit_command(message):
            bot.send_message(message.chat.id, "До свидания!")
            bot.send_photo(message.chat.id, variables["bye_pic"])

        @bot.message_handler(commands=['login'])
        def login_command(message):
            bot.send_message(message.chat.id, "Введите логин:")
            bot.register_next_step_handler(message, ask_password, bot, variables)

        # Функция для запроса пароля
        def ask_password(message, bot, variables):
            username = message.text
            if is_user_registered(username):
                bot.send_message(message.chat.id, "Введите пароль:")
                bot.register_next_step_handler(message, process_credentials, username, bot, variables)
            else:
                bot.send_message(message.chat.id, "Неверный логин. Попробуйте еще раз.")
                ask_credentials(bot, message, variables)

        # Функция для обработки введенных данных и предоставления доступа к боту
        def process_credentials(message, username, bot, variables):
            password = message.text
            if authenticate_user(username, password):
                bot.send_message(message.chat.id, "Успешная авторизация!")
                bot.send_photo(message.chat.id, variables["success_pic"])
                # Здесь вы можете добавить логику, которая должна произойти после успешной авторизации,
                # например, загрузить данные пользователя или настроить сессию
            else:
                bot.send_message(message.chat.id, "Неверный пароль. Попробуйте еще раз.")
                ask_credentials(bot, message, variables)

        # Функция для запроса логина и пароля
        def ask_credentials(bot, message, variables):
            bot.send_message(message.chat.id, "Введите логин:")
            bot.register_next_step_handler(message, ask_password, bot, variables)

        # Обработка команды /help
        @bot.message_handler(commands=['help'])
        def help_command(message):
            bot.send_message(message.chat.id, "Доступные команды: /start, /cancel, /help, /add_user")

        # Обработка команды /add_user
        @bot.message_handler(commands=['adduser'])
        def add_user_command(message):
            if access_matrix.get(message.chat.id, "user") != "root":
                bot.send_message(message.chat.id, "У вас нет прав для добавления пользователей.")
                return

            bot.send_message(message.chat.id, "Введите имя пользователя:")
            bot.register_next_step_handler(message, ask_password_for_new_user, bot)

        # Запуск бота
        bot.polling(non_stop=True)

    except FileNotFoundError:
        print("Error: variables.pkl not found!")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Функция для запроса пароля для нового пользователя
def ask_password_for_new_user(message, bot, username):
    bot.send_message(message.chat.id, "Введите пароль для пользователя:")
    bot.register_next_step_handler(message, ask_permission_for_new_user, bot, username)


# Функция для запроса прав доступа для нового пользователя
def ask_permission_for_new_user(message, bot, username):
    password = message.text
    bot.send_message(message.chat.id, "Введите права доступа для пользователя (user/admin):")
    bot.register_next_step_handler(message, process_new_user, bot, username, password)


# Функция для обработки нового пользователя
def process_new_user(message, bot, username, password, permission):
    if add_user_to_db(username, password, permission):
        bot.send_message(message.chat.id, f"Пользователь {username} успешно добавлен.")
    else:
        bot.send_message(message.chat.id,
                         "Ошибка при добавлении пользователя. Возможно, пользователь с таким именем уже существует.")


def show_help(bot, message, variables):
    help_text = """
*Доступные команды:*

/start - Начать работу с ботом
/help - Показать это меню
/cancel - Отменить текущую операцию

*Описание команд:*

/start - Запускает бота и предлагает ввести логин для авторизации.
/help - Показывает это меню с описанием доступных команд.
/cancel - Отменяет текущую операцию, например, отменяет запрос пароля при вводе логина.

*Для использования бота:*
1. Отправьте команду /start.
2. Следуйте инструкциям бота для входа в систему.
3. Используйте доступные команды для выполнения задач.

*Если у вас возникнут вопросы или проблемы:*
Пожалуйста, свяжитесь с нашей службой поддержки для получения помощи.
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


if __name__ == "__main__":
    main()
