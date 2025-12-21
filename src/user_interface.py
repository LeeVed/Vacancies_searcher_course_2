from src.hh_api import HeadHunterAPI
from src.vacancy import Vacancy
from config import VACANCIES_JSON
from src.json_saver import JSONSaver


class ConsoleInterface:
    """
    Класс для консольного интерфейса пользователя.
    Обеспечивает взаимодействие с системой через меню.
    """

    def __init__(self):
        """Инициализация интерфейса."""

        self.api = HeadHunterAPI()
        self.saver = JSONSaver(VACANCIES_JSON)
        self.is_running = True

    def run(self) -> None:
        """Основной цикл работы интерфейса."""
        self._print_welcome_message()

        while self.is_running:
            self._show_main_menu()
            choice = self._get_user_choice()
            self._process_choice(choice)

    def _print_welcome_message(self) -> None:
        """Вывод приветственного сообщения."""
        print("=" * 50)
        print("СИСТЕМА ДЛЯ РАБОТЫ С ВАКАНСИЯМИ")
        print("=" * 50)
        print("Поиск и сохранение вакансий с hh.ru")
        print()

    def _show_main_menu(self) -> None:
        """Отображение главного меню."""
        print("\nГЛАВНОЕ МЕНЮ:")
        print("1. Поиск вакансий на hh.ru")
        print("2. Показать все сохраненные вакансии")
        print("3. Получить топ N вакансий по зарплате")
        print("4. Поиск вакансий по ключевому слову")
        print("5. Добавить вакансию вручную")
        print("6. Удалить вакансию")
        print("7. Очистить все вакансии")
        print("8. Выход")
        print()

    def _get_user_choice(self) -> str:
        """Получение выбора пользователя."""
        while True:
            choice = input("Выберите действие (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            print("Неверный выбор. Пожалуйста, введите число от 1 до 8.")

    def _process_choice(self, choice: str) -> None:
        """Обработка выбора пользователя."""
        actions = {
            '1': self._search_vacancies,
            '2': self._show_all_vacancies,
            '3': self._get_top_vacancies,
            '4': self._search_by_keyword,
            '5': self._add_vacancy_manually,
            '6': self._delete_vacancy,
            '7': self._clear_all_vacancies,
            '8': self._exit_program
        }

        action = actions.get(choice)
        if action:
            action()

    def _search_vacancies(self) -> None:
        """Поиск вакансий на hh.ru."""
        print("\n--- ПОИСК ВАКАНСИЙ НА HH.RU ---")

        search_query = input("Введите поисковый запрос: ").strip()
        if not search_query:
            print("Поисковый запрос не может быть пустым.")
            return

        try:
            per_page = int(input("Сколько вакансий загрузить? (макс. 100): ").strip() or "50")
            per_page = min(max(1, per_page), 100)
        except ValueError:
            print("Неверное количество. Будет загружено 50 вакансий.")
            per_page = 50

        print(f"\nИщу вакансии по запросу: '{search_query}'...")

        vacancies_data = self.api.get_vacancies(search_query, per_page=per_page)

        if not vacancies_data:
            print("Не удалось найти вакансии по вашему запросу.")
            return

        print(f"Найдено {len(vacancies_data)} вакансий.")


        vacancies_objects = []
        for vacancy_dict in vacancies_data:
            try:

                vacancy = Vacancy.from_dict(vacancy_dict)
                vacancies_objects.append(vacancy)
            except Exception:
                continue

        self.saver.add_vacancies(vacancies_objects)

        print(f"Сохранено {len(vacancies_objects)} новых вакансий.")

        # Показываем первые 5 вакансий
        if vacancies_objects:
            print("\nПервые 5 найденных вакансий:")
            for i, vacancy in enumerate(vacancies_objects[:5], 1):
                print(f"\n{i}. {vacancy.title}")
                salary_str = f"{vacancy.salary:,.0f} руб." if vacancy.salary > 0 else "Зарплата не указана"
                print(f"   Зарплата: {salary_str}")
                print(f"   Описание: {vacancy.description[:100]}...")

    def _show_all_vacancies(self) -> None:
        """Показать все сохраненные вакансии."""
        print("\n--- ВСЕ СОХРАНЕННЫЕ ВАКАНСИИ ---")

        vacancies = self.saver.get_vacancies()

        if not vacancies:
            print("Нет сохраненных вакансий.")
            return

        print(f"Всего сохранено вакансий: {len(vacancies)}")

        for i, vacancy in enumerate(vacancies, 1):
            print(f"\n{i}. {vacancy.title}")
            salary_str = f"{vacancy.salary:,.0f} руб." if vacancy.salary > 0 else "Зарплата не указана"
            print(f"   Зарплата: {salary_str}")
            print(f"   Описание: {vacancy.description[:100]}...")
            print(f"   Ссылка: {vacancy.url if vacancy.url else 'Нет ссылки'}")

    def _get_top_vacancies(self) -> None:
        """Получить топ N вакансий по зарплате."""
        print("\n--- ТОП ВАКАНСИЙ ПО ЗАРПЛАТЕ ---")

        try:
            n = int(input("Сколько вакансий показать в топе? ").strip())
            if n <= 0:
                print("Число должно быть положительным.")
                return
        except ValueError:
            print("Неверный ввод. Будет показано 10 вакансий.")
            n = 10

        top_vacancies = self.saver.get_top_n_by_salary(n)

        if not top_vacancies:
            print("Нет вакансий с указанной зарплатой.")
            return

        print(f"\nТоп-{len(top_vacancies)} вакансий по зарплате:")

        for i, vacancy in enumerate(top_vacancies, 1):
            print(f"\n{i}. {vacancy.title}")
            print(f"   Зарплата: {vacancy.salary:,.0f} руб.")
            print(f"   Описание: {vacancy.description[:100]}...")
            print(f"   Ссылка: {vacancy.url}")

    def _search_by_keyword(self) -> None:
        """Поиск вакансий по ключевому слову в описании."""
        print("\n--- ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ ---")

        keyword = input("Введите ключевое слово для поиска: ").strip()

        if not keyword:
            print("Ключевое слово не может быть пустым.")
            return

        criteria = {'keyword': keyword}
        vacancies = self.saver.get_vacancies(criteria)

        if not vacancies:
            print(f"Не найдено вакансий с ключевым словом '{keyword}'.")
            return

        print(f"\nНайдено {len(vacancies)} вакансий с ключевым словом '{keyword}':")

        for i, vacancy in enumerate(vacancies, 1):
            print(f"\n{i}. {vacancy.title}")
            salary_str = f"{vacancy.salary:,.0f} руб." if vacancy.salary > 0 else "Зарплата не указана"
            print(f"   Зарплата: {salary_str}")
            print(f"   Описание: {vacancy.description[:200]}...")
            print(f"   Ссылка: {vacancy.url}")

    def _add_vacancy_manually(self) -> None:
        """Добавление вакансии вручную."""
        print("\n--- ДОБАВЛЕНИЕ ВАКАНСИИ ВРУЧНУЮ ---")

        try:
            title = input("Название вакансии: ").strip()
            if not title:
                print("Название не может быть пустым.")
                return

            url = input("Ссылка на вакансию: ").strip()
            if not url:
                print("Ссылка не может быть пустой.")
                return

            salary_str = input("Зарплата (руб., оставьте пустым если не указана): ").strip()
            salary = float(salary_str) if salary_str else 0.0

            description = input("Описание/требования: ").strip()
            if not description:
                description = "Описание отсутствует"

            vacancy = Vacancy(
                title=title,
                url=url,
                salary=salary,
                description=description
            )

            self.saver.add_vacancy(vacancy)

            print(f"\nВакансия '{title}' успешно добавлена!")

        except ValueError as e:
            print(f"Ошибка в данных: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def _delete_vacancy(self) -> None:
        """Удаление вакансии."""
        print("\n--- УДАЛЕНИЕ ВАКАНСИИ ---")

        vacancies = self.saver.get_vacancies()

        if not vacancies:
            print("Нет сохраненных вакансий для удаления.")
            return

        print("Сохраненные вакансии:")
        for i, vacancy in enumerate(vacancies, 1):
            salary_str = f"{vacancy.salary:,.0f} руб." if vacancy.salary > 0 else "Не указана"
            print(f"{i}. {vacancy.title} (Зарплата: {salary_str})")

        try:
            choice = int(input("\nВведите номер вакансии для удаления: ").strip())
            if 1 <= choice <= len(vacancies):
                vacancy_to_delete = vacancies[choice - 1]

                confirm = input(
                    f"Вы уверены, что хотите удалить вакансию '{vacancy_to_delete.title}'? (да/нет): ").strip().lower()

                if confirm == 'да':
                    self.saver.delete_vacancy(vacancy_to_delete)
                    print(f"Вакансия '{vacancy_to_delete.title}' удалена.")
                else:
                    print("Удаление отменено.")
            else:
                print("Неверный номер вакансии.")
        except ValueError:
            print("Неверный ввод. Введите номер вакансии.")

    def _clear_all_vacancies(self) -> None:
        """Очистить все вакансии."""
        print("\n--- ОЧИСТКА ВСЕХ ВАКАНСИЙ ---")

        confirm = input("Вы уверены, что хотите удалить ВСЕ вакансии? (да/нет): ").strip().lower()

        if confirm == 'да':
            self.saver.clear_all()
            print("Все вакансии удалены.")
        else:
            print("Очистка отменена.")

    def _exit_program(self) -> None:
        """Выход из программы."""
        print("\nСпасибо за использование программы! До свидания!")
        self.is_running = False
