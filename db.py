import sqlite3
import hashlib


def connect_to_db():
    try:
        return sqlite3.connect('tokb.db')
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def create_table():
    db = connect_to_db()
    if db is None:
        return

    try:
        with db:
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    permission TEXT NOT NULL
                );
            """)
    except sqlite3.Error as e:
        print(f"Ошибка создания таблицы: {e}")
    finally:
        if db:
            db.close()


def add_user(username, password, permission):
    """Добавляет пользователя в базу данных с хешированием пароля."""

    db = connect_to_db()
    if db is None:
        return False

    try:
        with db:
            cursor = db.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Хеширование пароля
            print(f"Хешированный пароль: {hashed_password}")
            cursor.execute("""
                INSERT INTO users (username, password, permission)
                VALUES (?, ?, ?)
            """, (username, hashed_password, permission))
    except sqlite3.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
        return False
    finally:
        if db:
            db.close()

    return True


def get_user(username):
    """Получает информацию о пользователе из базы данных."""

    db = connect_to_db()
    if db is None:
        return None

    try:
        with db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT id, username, password, permission
                FROM users
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Ошибка получения информации о пользователе: {e}")
        return None
    finally:
        if db:
            db.close()

    return user if user else None


if __name__ == "__main__":
    create_table()
    username = "root"
    password = "qwe123!@#"
    permission = "root"
    print(f"Добавление пользователя: {username}")
    add_user(username, password, permission)
    user = get_user(username)
    print(f"Информация о пользователе: {user}")
