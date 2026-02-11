from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QPushButton,
                             QMessageBox, QLineEdit, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class LoginDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YummyLibria - Авторизация')
        self.setFixedSize(300, 200)
        self.setModal(True)

        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel('Вход в систему')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Поле имени пользователя
        layout.addWidget(QLabel('Имя пользователя:'))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Введите имя пользователя')
        layout.addWidget(self.username_input)

        # Поле пароля
        layout.addWidget(QLabel('Пароль:'))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Кнопки
        buttons_layout = QHBoxLayout()

        login_button = QPushButton('Войти')
        login_button.clicked.connect(self.login)
        buttons_layout.addWidget(login_button)

        register_button = QPushButton('Регистрация')
        register_button.clicked.connect(self.register)
        buttons_layout.addWidget(register_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return

        try:
            if self.db_manager.login_user(username, password):
                self.accept()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверное имя пользователя или пароль!')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}')

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля!')
            return

        if len(username) < 3:
            QMessageBox.warning(self, 'Ошибка', 'Имя пользователя должно содержать минимум 3 символа!')
            return

        if len(password) < 4:
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен содержать минимум 4 символа!')
            return

        if self.db_manager.register_user(username, password):
            QMessageBox.information(self, 'Успех', 'Регистрация прошла успешно! Теперь вы можете войти.')
            # Очистка поля пароля
            self.password_input.clear()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким именем уже существует!')