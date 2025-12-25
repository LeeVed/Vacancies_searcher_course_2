import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Теперь можем импортировать модули из src
    from src.user_interface import ConsoleInterface


    def main():
        """
        Основная функция программы.
        Запускает консольный интерфейс для работы с вакансиями.
        """
        try:
            print("=" * 50)
            print("СИСТЕМА ДЛЯ РАБОТЫ С ВАКАНСИЯМИ")
            print("=" * 50)
            print("Поиск и сохранение вакансий с hh.ru")
            print()

            # Создаем и запускаем интерфейс
            interface = ConsoleInterface()
            interface.run()

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            print("Пожалуйста, проверьте настройки и попробуйте снова.")


    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Проверьте структуру проекта:")
    print("1. Убедитесь, что main.py находится в корне проекта")
    print("2. Убедитесь, что папка src существует и содержит все модули")
    sys.exit(1)
