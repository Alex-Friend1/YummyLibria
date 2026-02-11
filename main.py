import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QScrollArea, QGridLayout,
                             QMessageBox, QDialog, QHBoxLayout, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import DatabaseManager
from LoginDialog import LoginDialog
from DessertWidget import DessertWidget


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.db_manager = DatabaseManager()
        self.all_desserts = self.load_desserts_from_file()  # Все десерты
        self.filtered_desserts = self.all_desserts.copy()  # Отфильтрованные десерты
        self.categories = self.extract_categories()  # Все уникальные категории
        self.nations = self.extract_nations()  # Все уникальные народы
        self.initUI()

    def load_desserts_from_file(self, filename="food.txt"):
        desserts = []

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # Разделяем на десерты
            dessert_blocks = content.split('===')

            for block in dessert_blocks:
                block = block.strip()
                if not block:
                    continue

                lines = block.split('\n')
                lines = [line.strip() for line in lines if line.strip()]

                if len(lines) >= 4:
                    dessert = {
                        'name': lines[0],
                        'image': lines[1],
                        'time': lines[2],
                        'ingredients': [],
                        'recipe': '',
                        'category': 'Не указана',  # Категория по умолчанию
                        'nation': 'Не указан'  # Народ по умолчанию
                    }

                    # Находим разделитель между ингредиентами и рецептом
                    separator_index = -1
                    for i, line in enumerate(lines[3:], 3):
                        if line == '---':
                            separator_index = i
                            break

                    if separator_index != -1:
                        # Ингредиенты - от 3-й строки до разделителя
                        dessert['ingredients'] = lines[3:separator_index]

                        # Рецепт и дополнительные параметры - всё после разделителя
                        recipe_lines = []
                        for line in lines[separator_index + 1:]:
                            if line.startswith('Категория:'):
                                # Извлекаем категорию
                                dessert['category'] = line.replace('Категория:', '').strip()
                            elif line.startswith('Народ:'):
                                # Извлекаем народ
                                dessert['nation'] = line.replace('Народ:', '').strip()
                            else:
                                recipe_lines.append(line)

                        dessert['recipe'] = '\n'.join(recipe_lines)
                    else:
                        # Если разделитель не найден, предполагаем что все оставшиеся строки - ингредиенты
                        dessert['ingredients'] = lines[3:]
                        dessert['recipe'] = "Рецепт не указан"

                    # Если категория не найдена в рецепте, пробуем определить автоматически
                    if dessert['category'] == 'Не указана':
                        dessert_name_lower = dessert['name'].lower()
                        if any(word in dessert_name_lower for word in ['торт', 'чизкейк', 'медовик']):
                            dessert['category'] = 'Торты'
                        elif any(word in dessert_name_lower for word in ['мороженое', 'тирамису', 'панна котта']):
                            dessert['category'] = 'Холодные десерты'
                        elif any(word in dessert_name_lower for word in ['печенье', 'булочка']):
                            dessert['category'] = 'Печенье'
                        elif any(word in dessert_name_lower for word in ['кекс', 'маффин', 'круассан']):
                            dessert['category'] = 'Выпечка'
                        elif any(word in dessert_name_lower for word in ['пирог']):
                            dessert['category'] = 'Пироги'

                    desserts.append(dessert)

        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден!")
            return []
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при чтении файла: {str(e)}")
            return []

        return desserts

    def extract_categories(self):
        # Извлекаем все уникальные категории из десертов
        categories = set()
        for dessert in self.all_desserts:
            categories.add(dessert['category'])

        # Сортируем категории и добавляем "Все" в начало
        sorted_categories = sorted(categories)
        return ['Все'] + sorted_categories

    def extract_nations(self):
        # Извлекаем все уникальные народы из десертов
        nations = set()
        for dessert in self.all_desserts:
            nations.add(dessert['nation'])

        # Сортируем народы и добавляем "Все" в начало
        sorted_nations = sorted(nations)
        return ['Все'] + sorted_nations

    def initUI(self):
        self.setWindowTitle(f'YummyLibria - Добро пожаловать, {self.username}!')
        self.setFixedSize(1100, 800)  # Увеличили окно для дополнительных фильтров

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel('Выберите блюдо для просмотра рецепта')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Панель поиска и фильтров
        search_filter_layout = QVBoxLayout()
        search_filter_layout.setSpacing(5)

        # Строка поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Поиск блюд:")
        search_label.setStyleSheet("font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название блюда или ингредиент...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """)
        self.search_input.textChanged.connect(self.filter_desserts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_filter_layout.addLayout(search_layout)

        # Фильтры: категория, народ, сортировка
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        # Фильтр по категориям
        filter_layout.addWidget(QLabel("📂 Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #0078d7;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.filter_desserts)
        filter_layout.addWidget(self.category_combo)

        # Фильтр по народам
        filter_layout.addWidget(QLabel("🌍 Страна/Народ:"))
        self.nation_combo = QComboBox()
        self.nation_combo.addItems(self.nations)
        self.nation_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #0078d7;
            }
        """)
        self.nation_combo.currentTextChanged.connect(self.filter_desserts)
        filter_layout.addWidget(self.nation_combo)

        # Кнопка сброса фильтров
        reset_button = QPushButton("🔄 Сбросить фильтры")
        reset_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)

        filter_layout.addWidget(reset_button)
        search_filter_layout.addLayout(filter_layout)

        main_layout.addLayout(search_filter_layout)

        # Кнопка выхода
        buttons_layout = QHBoxLayout()
        logout_button = QPushButton('🚪 Выйти')
        logout_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.logout)
        buttons_layout.addWidget(logout_button)
        buttons_layout.addStretch()

        # Информация о количестве десертов
        self.count_label = QLabel(f"Всего блюд: {len(self.all_desserts)}")
        self.count_label.setStyleSheet("color: #666; font-style: italic;")
        buttons_layout.addWidget(self.count_label)

        main_layout.addLayout(buttons_layout)

        # Область с прокруткой для десертов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)

        # Контейнер для десертов
        self.desserts_container = QWidget()
        self.desserts_layout = QGridLayout(self.desserts_container)
        self.desserts_layout.setSpacing(15)
        self.desserts_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area.setWidget(self.desserts_container)
        main_layout.addWidget(scroll_area)

        # Создание виджетов десертов
        self.create_dessert_widgets()

    def create_dessert_widgets(self):
        # Очищаем существующие виджеты
        for i in reversed(range(self.desserts_layout.count())):
            widget = self.desserts_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Обновляем счетчик
        self.count_label.setText(f"Показано: {len(self.filtered_desserts)} из {len(self.all_desserts)} блюд")

        # Создаем новые виджеты на основе отфильтрованного и отсортированного списка
        if not self.filtered_desserts:
            # Если десертов нет, показываем сообщение
            no_results_widget = QWidget()
            no_results_layout = QVBoxLayout(no_results_widget)
            no_results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            no_results_icon = QLabel("🍰")
            no_results_icon.setStyleSheet("font-size: 48px;")
            no_results_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            no_results_text = QLabel("Блюда не найдены")
            no_results_text.setStyleSheet("font-size: 16px; color: #666; font-weight: bold;")
            no_results_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

            no_results_hint = QLabel("Попробуйте изменить критерии поиска или выбрать другую категорию")
            no_results_hint.setStyleSheet("font-size: 12px; color: #999;")
            no_results_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

            no_results_layout.addWidget(no_results_icon)
            no_results_layout.addWidget(no_results_text)
            no_results_layout.addWidget(no_results_hint)

            self.desserts_layout.addWidget(no_results_widget, 0, 0, 1, 3)
            return

        row, col = 0, 0
        max_cols = 3  # 3 колонки для лучшего отображения

        for dessert_data in self.filtered_desserts:
            dessert_widget = DessertWidget(dessert_data, username=self.username, db_manager=self.db_manager)
            self.desserts_layout.addWidget(dessert_widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def filter_desserts(self):
        # Фильтрация десертов по поиску, категории и народу
        search_text = self.search_input.text().lower()
        selected_category = self.category_combo.currentText()
        selected_nation = self.nation_combo.currentText()

        self.filtered_desserts = []

        for dessert in self.all_desserts:
            # Проверка поиска (ищем в названии, категории, народе и ингредиентах)
            matches_search = False
            if search_text == "":
                matches_search = True
            else:
                # Поиск в различных полях
                if (search_text in dessert['name'].lower() or
                        search_text in dessert['category'].lower() or
                        search_text in dessert['nation'].lower()):
                    matches_search = True
                else:
                    # Поиск в ингредиентах
                    for ingredient in dessert['ingredients']:
                        if search_text in ingredient.lower():
                            matches_search = True
                            break

            # Проверка категории
            matches_category = (selected_category == "Все" or
                                dessert['category'] == selected_category)

            # Проверка народа
            matches_nation = (selected_nation == "Все" or
                              dessert['nation'] == selected_nation)

            if matches_search and matches_category and matches_nation:
                self.filtered_desserts.append(dessert)

        # Обновляем отображение
        self.create_dessert_widgets()

    def reset_filters(self):
        # Сбросить все фильтры
        self.search_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.nation_combo.setCurrentIndex(0)
        self.filtered_desserts = self.all_desserts.copy()
        self.create_dessert_widgets()
        QMessageBox.information(self, "Фильтры сброшены",
                                "Все фильтры были сброшены. Показаны все блюда.")

    def show_statistics(self):

        # Показать статистику по категориям и народам
        category_stats = {}
        nation_stats = {}

        for dessert in self.all_desserts:
            category = dessert['category']
            nation = dessert['nation']

            category_stats[category] = category_stats.get(category, 0) + 1
            nation_stats[nation] = nation_stats.get(nation, 0) + 1

        # Создаем сообщение со статистикой
        message = "📊 Статистика:\n\n"

        message += "По категориям:\n"
        for category, count in sorted(category_stats.items()):
            message += f"• {category}: {count} блюд(а)\n"

        message += "\nПо народам:\n"
        for nation, count in sorted(nation_stats.items()):
            message += f"• {nation}: {count} блюд(а)\n"

        message += f"\nВсего блюд: {len(self.all_desserts)}"

        QMessageBox.information(self, "Статистика", message)

    def logout(self):
        # Выход из системы
        reply = QMessageBox.question(self, 'Выход',
                                     'Вы уверены, что хотите выйти?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()


def main():
    app = QApplication(sys.argv)

    db_manager = DatabaseManager()
    login_dialog = LoginDialog(db_manager)

    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        username = login_dialog.username_input.text().strip()
        window = MainWindow(username)  # Передаем имя пользователя
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
