import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_name="my_db.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Таблица избранных десертов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS FavoriteDesserts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dessert_name TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id),
            UNIQUE(user_id, dessert_name)
        )
        """)

        # Таблица комментариев
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dessert_name TEXT NOT NULL,
            comment TEXT NOT NULL,
            rating INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        )
        """)

        connection.commit()
        connection.close()

    def caesar_cipher(self, text, shift):
        result = ''
        for char in text:
            if char.isalpha():
                base = ord('a') if char.islower() else ord('A')
                shifted_char = chr((ord(char) - base + shift) % 26 + base)
                result += shifted_char
            else:
                result += char
        return result

    def register_user(self, username, password):
        if self.user_exists(username):
            return False

        try:
            encrypted_password = self.caesar_cipher(password, 20)
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)",
                           (username, encrypted_password))
            connection.commit()
            connection.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Ошибка при регистрации: {e}")
            return False

    def user_exists(self, username):
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
            user = cursor.fetchone()
            connection.close()
            return user is not None
        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
            return False

    def login_user(self, username, password):
        try:
            encrypted_password = self.caesar_cipher(password, 20)
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?",
                           (username, encrypted_password))
            user = cursor.fetchone()
            connection.close()
            return user is not None
        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            return False

    def get_user_id(self, username):
        # Получить ID пользователя по имени
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()
            connection.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при получении ID пользователя: {e}")
            return None

    # Методы для избранных десертов
    def add_to_favorites(self, username, dessert_name):
        # Добавить десерт в избранное
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return False

            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO FavoriteDesserts (user_id, dessert_name) 
                VALUES (?, ?)
            """, (user_id, dessert_name))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении в избранное: {e}")
            return False

    def remove_from_favorites(self, username, dessert_name):
        # Удалить десерт из избранного
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return False

            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM FavoriteDesserts 
                WHERE user_id = ? AND dessert_name = ?
            """, (user_id, dessert_name))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка при удалении из избранного: {e}")
            return False

    def is_favorite(self, username, dessert_name):
        # Проверить, находится ли десерт в избранном
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return False

            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id FROM FavoriteDesserts 
                WHERE user_id = ? AND dessert_name = ?
            """, (user_id, dessert_name))
            result = cursor.fetchone()
            connection.close()
            return result is not None
        except Exception as e:
            print(f"Ошибка при проверке избранного: {e}")
            return False

    # Методы для комментариев
    def add_comment(self, username, dessert_name, comment, rating=0):
        # Добавить комментарий к десерту
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return False

            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Comments (user_id, dessert_name, comment, rating) 
                VALUES (?, ?, ?, ?)
            """, (user_id, dessert_name, comment, rating))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении комментария: {e}")
            return False

    def get_comments(self, dessert_name):
        # Получить все комментарии для десерта
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                SELECT u.username, c.comment, c.rating, c.created_at 
                FROM Comments c
                JOIN Users u ON c.user_id = u.id
                WHERE c.dessert_name = ?
                ORDER BY c.created_at DESC
            """, (dessert_name,))
            comments = cursor.fetchall()
            connection.close()
            return comments
        except Exception as e:
            print(f"Ошибка при получении комментариев: {e}")
            return []

    def get_average_rating(self, dessert_name):
        # Получить средний рейтинг десерта
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute("""
                SELECT AVG(rating) FROM Comments 
                WHERE dessert_name = ? AND rating > 0
            """, (dessert_name,))
            result = cursor.fetchone()
            connection.close()
            return round(result[0], 1) if result[0] else 0
        except Exception as e:
            print(f"Ошибка при получении рейтинга: {e}")
            return 0