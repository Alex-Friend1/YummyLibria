from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QLabel, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from DessertDetailWindow import DessertDetailWindow


class DessertWidget(QWidget):
    def __init__(self, dessert_data, username, db_manager, parent=None):
        super().__init__(parent)
        self.dessert_data = dessert_data
        self.username = username
        self.db_manager = db_manager
        self.initUI()
        # Сразу создаем и обновляем индикаторы
        self.create_indicators()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Изображение десерта
        self.image_label = QLabel()
        pixmap = QPixmap(self.dessert_data['image'])
        if not pixmap.isNull():
            pixmap = pixmap.scaled(250, 180, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            # Если изображение не найдено, показываем заглушку
            self.image_label.setText("Изображение не найдено")
            self.image_label.setStyleSheet("color: gray; font-style: italic;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #ddd; border-radius: 10px; padding: 5px;")

        # Название десерта
        self.name_label = QLabel(self.dessert_data['name'])
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.name_label.setFont(font)

        # Время приготовления
        self.time_label = QLabel(f"⏱️ {self.dessert_data['time']}")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #666; font-size: 11px;")

        # Категория
        self.category_label = QLabel(f"📁 {self.dessert_data.get('category', 'Не указана')}")
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_label.setStyleSheet("color: #666; font-size: 11px;")

        # Народ
        self.nation_label = QLabel(f"🌍 {self.dessert_data.get('nation', 'Не указан')}")
        self.nation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nation_label.setStyleSheet("color: #666; font-size: 11px;")

        # Контейнер для индикаторов (будет обновляться)
        self.indicators_container = QWidget()
        self.indicators_layout = QHBoxLayout(self.indicators_container)
        self.indicators_layout.setContentsMargins(0, 0, 0, 0)
        self.indicators_layout.setSpacing(10)

        # Располагаем контейнер с индикаторами в макете
        indicators_wrapper_layout = QHBoxLayout()
        indicators_wrapper_layout.addStretch()
        indicators_wrapper_layout.addWidget(self.indicators_container)
        indicators_wrapper_layout.addStretch()

        # Добавляем все элементы в основной макет
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.name_label)

        # Индикаторы располагаются здесь - между названием и временем
        self.layout.addLayout(indicators_wrapper_layout)

        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.nation_label)

        # Стиль виджета
        self.setStyleSheet("""
            DessertWidget {
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 5px;
                background-color: #ffffff;
                margin: 5px;
            }
            DessertWidget:hover {
                border-color: #0078d7;
                background-color: #f0f8ff;
                transform: translateY(-2px);
            }
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(280)

    def create_indicators(self):
        # Создать/обновить индикаторы избранного и рейтинга
        # Очищаем предыдущие индикаторы
        for i in reversed(range(self.indicators_layout.count())):
            widget = self.indicators_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Индикатор избранного
        if self.db_manager.is_favorite(self.username, self.dessert_data['name']):
            favorite_indicator = QLabel("❤️")
            favorite_indicator.setToolTip("В избранном")
            favorite_indicator.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    padding: 2px;
                }
            """)
            self.indicators_layout.addWidget(favorite_indicator)

        # Рейтинг
        avg_rating = self.db_manager.get_average_rating(self.dessert_data['name'])
        if avg_rating > 0:
            rating_label = QLabel(f"⭐ {avg_rating}")
            rating_label.setToolTip(f"Средний рейтинг: {avg_rating}/5")
            rating_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #FFA000;
                    padding: 2px;
                }
            """)
            self.indicators_layout.addWidget(rating_label)

        # Если нет индикаторов, добавляем невидимый спейсер для сохранения расположения
        if self.indicators_layout.count() == 0:
            invisible_spacer = QLabel(" ")
            invisible_spacer.setStyleSheet("color: transparent;")
            self.indicators_layout.addWidget(invisible_spacer)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.showDetailWindow()

    def showDetailWindow(self):
        self.detail_window = DessertDetailWindow(self.dessert_data, self.username, self.db_manager, self)
        self.detail_window.show()