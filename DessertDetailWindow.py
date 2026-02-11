from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
                             QMessageBox, QLineEdit, QHBoxLayout, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont


class DessertDetailWindow(QMainWindow):
    def __init__(self, dessert_data, username, db_manager, parent_widget=None):
        super().__init__()
        self.dessert_data = dessert_data
        self.username = username
        self.db_manager = db_manager
        self.parent_widget = parent_widget
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"{self.dessert_data['name']} - Рецепт")
        self.setFixedSize(700, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout для центрального виджета
        main_layout = QVBoxLayout(central_widget)

        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Создаем виджет для содержимого
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)

        # Добавляем все элементы в content_layout
        self.add_content_to_layout()

        # Устанавливаем content_widget в scroll_area
        scroll_area.setWidget(content_widget)

        # Добавляем scroll_area в основной layout
        main_layout.addWidget(scroll_area)

    def add_content_to_layout(self):
        # Добавить все элементы в layout содержимого
        layout = self.content_layout

        # Название десерта
        title_label = QLabel(self.dessert_data['name'])
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Категория и народ
        info_layout = QHBoxLayout()

        category_label = QLabel(f"📂 Категория: {self.dessert_data.get('category', 'Не указана')}")
        category_font = QFont()
        category_font.setPointSize(12)
        category_label.setFont(category_font)
        category_label.setStyleSheet("color: #666;")

        nation_label = QLabel(f"🌍 Страна/Народ: {self.dessert_data.get('nation', 'Не указан')}")
        nation_font = QFont()
        nation_font.setPointSize(12)
        nation_label.setFont(nation_font)
        nation_label.setStyleSheet("color: #666; margin-left: 20px;")

        info_layout.addWidget(category_label)
        info_layout.addWidget(nation_label)
        info_layout.addStretch()

        layout.addLayout(info_layout)

        # Изображение десерта
        image_label = QLabel()
        pixmap = QPixmap(self.dessert_data['image'])
        if not pixmap.isNull():
            pixmap = pixmap.scaled(400, 250, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)

        # Время приготовления
        time_label = QLabel(f"⏱️ Время приготовления: {self.dessert_data['time']}")
        time_font = QFont()
        time_font.setPointSize(12)
        time_font.setBold(True)
        time_label.setFont(time_font)
        layout.addWidget(time_label)

        # Ингредиенты
        ingredients_label = QLabel("🍴 Ингредиенты:")
        ingredients_label.setFont(time_font)
        layout.addWidget(ingredients_label)

        ingredients_text = QLabel("\n".join([f"• {ingredient}" for ingredient in self.dessert_data['ingredients']]))
        ingredients_text.setWordWrap(True)
        layout.addWidget(ingredients_text)

        # Рецепт
        recipe_label = QLabel("📝 Рецепт:")
        recipe_label.setFont(time_font)
        layout.addWidget(recipe_label)

        recipe_text = QLabel(self.dessert_data['recipe'])
        recipe_text.setWordWrap(True)
        recipe_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        recipe_text.setStyleSheet(
            "QLabel { margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }")
        layout.addWidget(recipe_text)

        # Кнопки избранного
        favorites_layout = QHBoxLayout()
        self.favorite_button = QPushButton()
        self.update_favorite_button()
        self.favorite_button.clicked.connect(self.toggle_favorite)
        favorites_layout.addWidget(self.favorite_button)
        favorites_layout.addStretch()
        layout.addLayout(favorites_layout)

        # Раздел комментариев
        self.add_comments_section(layout)

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # Добавляем растяжку в конце, чтобы элементы не растягивались
        layout.addStretch()

    def update_favorite_button(self):
        # Обновить текст кнопки избранного
        is_fav = self.db_manager.is_favorite(self.username, self.dessert_data['name'])
        if is_fav:
            self.favorite_button.setText("❤️ Удалить из избранного")
            self.favorite_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffebee;
                    color: #d32f2f;
                    padding: 8px 15px;
                    border: 2px solid #d32f2f;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ffcdd2;
                }
            """)
        else:
            self.favorite_button.setText("🤍 Добавить в избранное")
            self.favorite_button.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    color: #666;
                    padding: 8px 15px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

    def toggle_favorite(self):
        # Добавить/удалить из избранного
        dessert_name = self.dessert_data['name']
        is_fav = self.db_manager.is_favorite(self.username, dessert_name)

        if is_fav:
            self.db_manager.remove_from_favorites(self.username, dessert_name)
            QMessageBox.information(self, "Избранное", "Десерт удален из избранного")
        else:
            self.db_manager.add_to_favorites(self.username, dessert_name)
            QMessageBox.information(self, "Избранное", "Десерт добавлен в избранное")

        self.update_favorite_button()

    def add_comments_section(self, layout):
        # Добавить раздел комментариев
        # Заголовок комментариев
        comments_label = QLabel("💬 Комментарии")
        comments_font = QFont()
        comments_font.setPointSize(14)
        comments_font.setBold(True)
        comments_label.setFont(comments_font)
        layout.addWidget(comments_label)

        # Средний рейтинг
        avg_rating = self.db_manager.get_average_rating(self.dessert_data['name'])
        rating_label = QLabel(f"⭐ Средний рейтинг: {avg_rating}/5")
        layout.addWidget(rating_label)

        # Форма добавления комментария
        comment_form_layout = QVBoxLayout()

        comment_label = QLabel("Ваш комментарий:")
        comment_form_layout.addWidget(comment_label)

        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Напишите ваш отзыв...")
        self.comment_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 5px;")
        comment_form_layout.addWidget(self.comment_input)

        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("Оценка:"))
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["0 - Без оценки", "1", "2", "3", "4", "5"])
        rating_layout.addWidget(self.rating_combo)
        rating_layout.addStretch()
        comment_form_layout.addLayout(rating_layout)

        add_comment_button = QPushButton("Добавить комментарий")
        add_comment_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_comment_button.clicked.connect(self.add_comment)
        comment_form_layout.addWidget(add_comment_button)

        layout.addLayout(comment_form_layout)

        # Список комментариев
        comments = self.db_manager.get_comments(self.dessert_data['name'])
        if comments:
            for username, comment, rating, created_at in comments:
                comment_widget = self.create_comment_widget(username, comment, rating, created_at)
                layout.addWidget(comment_widget)
        else:
            no_comments_label = QLabel("Пока нет комментариев. Будьте первым!")
            no_comments_label.setStyleSheet("color: gray; font-style: italic; padding: 20px; text-align: center;")
            layout.addWidget(no_comments_label)

    def create_comment_widget(self, username, comment, rating, created_at):
        # Создать виджет комментария
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 5px;
                background-color: #ffffff;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(5)

        # Заголовок комментария
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"👤 {username}"))

        if rating > 0:
            stars = "⭐" * rating
            rating_label = QLabel(f"{stars} ({rating}/5)")
            rating_label.setStyleSheet("color: #FFA000; font-weight: bold;")
            header_layout.addWidget(rating_label)

        header_layout.addStretch()

        # Форматируем дату
        date_parts = created_at.split()[0].split('-')
        if len(date_parts) == 3:
            formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
        else:
            formatted_date = created_at.split()[0]

        date_label = QLabel(f"📅 {formatted_date}")
        date_label.setStyleSheet("color: #666; font-size: 11px;")
        header_layout.addWidget(date_label)

        layout.addLayout(header_layout)

        # Текст комментария
        comment_label = QLabel(comment)
        comment_label.setWordWrap(True)
        comment_label.setStyleSheet("padding: 10px 5px; border-top: 1px solid #f0f0f0; margin-top: 5px;")
        layout.addWidget(comment_label)

        return widget

    def closeEvent(self, event):
        # При закрытии окна обновляем индикаторы в родительском виджете
        if self.parent_widget and hasattr(self.parent_widget, 'create_indicators'):
            self.parent_widget.create_indicators()
        super().closeEvent(event)

    def add_comment(self):
        # Добавить новый комментарий
        comment = self.comment_input.text().strip()
        if not comment:
            QMessageBox.warning(self, "Ошибка", "Введите текст комментария!")
            return

        rating = self.rating_combo.currentIndex()

        success = self.db_manager.add_comment(self.username, self.dessert_data['name'], comment, rating)
        if success:
            QMessageBox.information(self, "Успех", "Комментарий добавлен!")
            self.comment_input.clear()
            self.rating_combo.setCurrentIndex(0)

            # Обновляем рейтинг и комментарии
            self.close()
            self.__init__(self.dessert_data, self.username, self.db_manager, self.parent_widget)
            self.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить комментарий!")