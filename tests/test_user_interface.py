import pytest
from unittest.mock import Mock, patch, call
from src.user_interface import ConsoleInterface


class TestConsoleInterface:
    """тесты для ConsoleInterface"""

    def test_init_creates_objects(self):
        """Тест инициализации интерфейса"""

        interface = ConsoleInterface()

        assert hasattr(interface, 'api')
        assert hasattr(interface, 'saver')
        assert interface.is_running is True

    def test_get_user_choice_valid(self):
        """Тест получения валидного выбора пользователя"""

        interface = ConsoleInterface()

        # Мокаем input для возврата валидного значения
        with patch('builtins.input', return_value='3'):
            choice = interface._get_user_choice()
            assert choice == '3'

    def test_process_choice_valid(self):
        """Тест обработки валидного выбора"""

        interface = ConsoleInterface()

        interface._search_vacancies = Mock()

        interface._process_choice('1')

        interface._search_vacancies.assert_called_once()

    def test_get_user_choice_invalid_then_valid(self):
        """Тест обработки невалидного, затем валидного выбора"""

        interface = ConsoleInterface()

        # input будет сначала возвращать невалидное, затем валидное значение
        with patch('builtins.input', side_effect=['0', '12', 'abc', '5']):
            with patch('builtins.print') as mock_print:
                choice = interface._get_user_choice()

                # Проверяем, что было сообщение об ошибке
                mock_print.assert_called_with("Неверный выбор. Пожалуйста, введите число от 1 до 8.")
                assert choice == '5'

    def test_process_choice_invalid(self):
        """Тест обработки невалидного выбора (edge case)"""

        interface = ConsoleInterface()

        try:
            interface._process_choice('99')
            interface._process_choice('0')
            interface._process_choice('')
            print("✓ Невалидный выбор обрабатывается без ошибок")
        except Exception as e:
            pytest.fail(f"Невалидный выбор вызвал исключение: {e}")

    @patch('src.user_interface.Vacancy.from_dict')
    @patch('src.user_interface.HeadHunterAPI')
    def test_search_vacancies_success(self, mock_api_class, mock_from_dict):
        """Тест успешного поиска вакансий"""

        mock_api = Mock()
        mock_api_class.return_value = mock_api

        mock_saver = Mock()

        # Тестовые данные от API
        test_vacancy_dict = {"title": "Python Developer", "salary": 100000}
        mock_api.get_vacancies.return_value = [test_vacancy_dict]

        # Mock Vacancy.from_dict
        mock_vacancy = Mock()
        mock_vacancy.title = "Python Developer"
        mock_vacancy.salary = 100000
        mock_vacancy.description = "Python development"
        mock_from_dict.return_value = mock_vacancy

        # Создаем интерфейс с мокнутым saver
        interface = ConsoleInterface()
        interface.saver = mock_saver

        # Мокаем input для симуляции пользовательского ввода
        with patch('builtins.input', side_effect=['Python', '10']):
            with patch('builtins.print'):
                interface._search_vacancies()

        # Проверяем вызовы
        mock_api.get_vacancies.assert_called_once_with('Python', per_page=10)
        mock_saver.add_vacancies.assert_called_once()

    @patch('builtins.input')
    def test_delete_vacancy_cancel(self, mock_input):
        """Тест отмены удаления вакансии"""

        interface = ConsoleInterface()

        # Мокаем saver
        mock_vacancy = Mock()
        mock_vacancy.title = "Test Vacancy"
        mock_vacancy.salary = 100000

        interface.saver.get_vacancies = Mock(return_value=[mock_vacancy])
        interface.saver.delete_vacancy = Mock()

        # Пользователь выбирает вакансию 1, но отменяет удаление
        mock_input.side_effect = ['1', 'нет']  # номер вакансии, затем отмена

        with patch('builtins.print'):
            interface._delete_vacancy()

        # delete_vacancy не должен быть вызван
        interface.saver.delete_vacancy.assert_not_called()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_vacancy_manually_invalid_salary(self, mock_print, mock_input):
        """Тест добавления вакансии с некорректной зарплатой"""

        interface = ConsoleInterface()
        interface.saver.add_vacancy = Mock()

        mock_input.side_effect = ['Test', 'https://test.com', 'abc', 'Desc']

        interface._add_vacancy_manually()

        # проверяем, что вакансия НЕ была добавлена
        interface.saver.add_vacancy.assert_not_called()

    def test_exit_program(self):
        """Тест выхода из программы"""
        interface = ConsoleInterface()
        assert interface.is_running is True

        interface._exit_program()

        assert interface.is_running is False

    def test_search_vacancies_empty_query(self):
        """Тест поиска с пустым запросом"""
        interface = ConsoleInterface()

        with patch('builtins.input', return_value=''):
            with patch('builtins.print') as mock_print:
                interface._search_vacancies()

                # Должно быть сообщение об ошибке
                mock_print.assert_called_with("Поисковый запрос не может быть пустым.")

    def test_search_vacancies_invalid_per_page(self):
        """Тест поиска с некорректным количеством вакансий"""
        interface = ConsoleInterface()

        # Мокаем API напрямую в объекте interface
        interface.api.get_vacancies = Mock(return_value=[])

        # Пользователь вводит некорректное число
        with patch('builtins.input', side_effect=['Python', 'not-a-number']):
            with patch('builtins.print') as mock_print:
                interface._search_vacancies()

                # Проверяем сообщение о некорректном вводе
                mock_print.assert_any_call("Неверное количество. Будет загружено 50 вакансий.")
                # Проверяем, что API было вызвано с per_page=50
                interface.api.get_vacancies.assert_called_once_with('Python', per_page=50)

    def test_search_vacancies_no_results(self):
        """Тест поиска, когда API не возвращает результатов"""

        interface = ConsoleInterface()

        interface.api.get_vacancies = Mock(return_value=[])

        interface.saver.add_vacancies = Mock()

        with patch('builtins.input', side_effect=['Python', '10']):
            with patch('builtins.print') as mock_print:
                interface._search_vacancies()

                # Проверяем, что сообщение было напечатано
                mock_print.assert_any_call("Не удалось найти вакансии по вашему запросу.")

                # Проверяем, что saver не был вызван (нет данных для сохранения)
                interface.saver.add_vacancies.assert_not_called()

    def test_show_all_vacancies_empty(self):
        """Тест показа всех вакансий, когда их нет"""
        interface = ConsoleInterface()
        interface.saver.get_vacancies = Mock(return_value=[])

        with patch('builtins.print') as mock_print:
            interface._show_all_vacancies()

            # Должно быть сообщение о пустом списке
            mock_print.assert_called_with("Нет сохраненных вакансий.")

    def test_show_all_vacancies_with_results(self):
        """Тест показа всех вакансий с результатами"""
        interface = ConsoleInterface()

        # Мокаем вакансии
        mock_vacancy1 = Mock()
        mock_vacancy1.title = "Python Developer"
        mock_vacancy1.salary = 100000
        mock_vacancy1.description = "Python development"
        mock_vacancy1.url = "https://test.com/1"

        mock_vacancy2 = Mock()
        mock_vacancy2.title = "Java Developer"
        mock_vacancy2.salary = 120000
        mock_vacancy2.description = "Java development"
        mock_vacancy2.url = ""

        interface.saver.get_vacancies = Mock(return_value=[mock_vacancy1, mock_vacancy2])

        with patch('builtins.print') as mock_print:
            interface._show_all_vacancies()

            # Проверяем, что вызов print был
            assert mock_print.call_count > 0
            # Проверяем, что первая строка содержит общее количество
            calls = [str(call[0][0]) for call in mock_print.call_args_list if call[0]]
            assert any("Всего сохранено вакансий: 2" in call for call in calls)

    def test_get_top_vacancies_valid(self):
        """Тест получения топ N вакансий с валидным вводом"""
        interface = ConsoleInterface()

        # Мокаем топ вакансии
        mock_vacancy = Mock()
        mock_vacancy.title = "Top Job"
        mock_vacancy.salary = 200000
        mock_vacancy.description = "Top description"
        mock_vacancy.url = "https://test.com/top"

        interface.saver.get_top_n_by_salary = Mock(return_value=[mock_vacancy])

        with patch('builtins.input', return_value='5'):
            with patch('builtins.print') as mock_print:
                interface._get_top_vacancies()

                # Проверяем, что метод был вызван с правильным параметром
                interface.saver.get_top_n_by_salary.assert_called_once_with(5)

    def test_delete_vacancy_empty_list(self):
        """Тест удаления вакансии из пустого списка"""
        interface = ConsoleInterface()
        interface.saver.get_vacancies = Mock(return_value=[])

        with patch('builtins.print') as mock_print:
            interface._delete_vacancy()

            # Должно быть сообщение о пустом списке
            mock_print.assert_called_with("Нет сохраненных вакансий для удаления.")

    def test_delete_vacancy_success(self):
        """Тест успешного удаления вакансии"""
        interface = ConsoleInterface()

        mock_vacancy = Mock()
        mock_vacancy.title = "Test Vacancy"
        mock_vacancy.salary = 100000

        interface.saver.get_vacancies = Mock(return_value=[mock_vacancy])
        interface.saver.delete_vacancy = Mock()

        # Пользователь подтверждает удаление
        with patch('builtins.input', side_effect=['1', 'да']):
            with patch('builtins.print'):
                interface._delete_vacancy()

                # Вакансия должна быть удалена
                interface.saver.delete_vacancy.assert_called_once_with(mock_vacancy)

    def test_search_by_keyword_empty(self):
        """Поиск по ключевому слову с пустым вводом"""
        interface = ConsoleInterface()

        with patch('builtins.input', return_value=''):
            with patch('builtins.print') as mock_print:
                interface._search_by_keyword()
                mock_print.assert_called_with("Ключевое слово не может быть пустым.")

    def test_search_by_keyword_no_results(self):
        """Поиск по ключевому слову без результатов"""
        interface = ConsoleInterface()
        interface.saver.get_vacancies = Mock(return_value=[])

        with patch('builtins.input', return_value='nonexistent'):
            with patch('builtins.print') as mock_print:
                interface._search_by_keyword()
                mock_print.assert_any_call("Не найдено вакансий с ключевым словом 'nonexistent'.")

    def test_search_by_keyword_with_results(self):
        """Поиск по ключевому слову с результатами"""
        interface = ConsoleInterface()

        mock_vacancy = Mock()
        mock_vacancy.title = "Python Developer"
        mock_vacancy.salary = 100000
        mock_vacancy.description = "Python and Django development"
        mock_vacancy.url = "https://test.com"

        interface.saver.get_vacancies = Mock(return_value=[mock_vacancy])

        with patch('builtins.input', return_value='python'):
            with patch('builtins.print') as mock_print:
                interface._search_by_keyword()
                interface.saver.get_vacancies.assert_called_once_with({'keyword': 'python'})

    def test_add_vacancy_manually_success(self):
        """Успешное добавление вакансии вручную"""
        interface = ConsoleInterface()
        interface.saver.add_vacancy = Mock()

        with patch('builtins.input', side_effect=[
            'Python Developer',  # title
            'https://test.com',  # url
            '150000',  # salary
            'Python development'  # description
        ]):
            with patch('builtins.print') as mock_print:
                interface._add_vacancy_manually()
                interface.saver.add_vacancy.assert_called_once()
                mock_print.assert_any_call("\nВакансия 'Python Developer' успешно добавлена!")

    def test_add_vacancy_manually_empty_title(self):
        """Добавление с пустым названием"""
        interface = ConsoleInterface()

        with patch('builtins.input', side_effect=['', 'https://test.com', '100000', 'Desc']):
            with patch('builtins.print') as mock_print:
                interface._add_vacancy_manually()
                mock_print.assert_called_with("Название не может быть пустым.")

    def test_add_vacancy_manually_empty_url(self):
        """Добавление с пустым URL"""
        interface = ConsoleInterface()

        with patch('builtins.input', side_effect=['Test Job', '', '100000', 'Desc']):
            with patch('builtins.print') as mock_print:
                interface._add_vacancy_manually()
                mock_print.assert_called_with("Ссылка не может быть пустой.")



