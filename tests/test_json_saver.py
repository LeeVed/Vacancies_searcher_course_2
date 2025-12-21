import pytest
import json
from unittest.mock import Mock, patch
from src.json_saver import JSONSaver
from src.vacancy import Vacancy


class TestJSONSaver:
    """Тесты для JSONSaver с использованием фикстур"""

    def test_init_creates_object(self, temp_json_file):
        """Тест создания объекта"""
        saver = JSONSaver(temp_json_file)
        assert saver.filename == temp_json_file

    def test_add_and_get_vacancy(self, json_saver, mock_vacancy):
        """Базовый тест добавления и получения"""
        json_saver.add_vacancy(mock_vacancy)
        vacancies = json_saver.get_vacancies()
        assert len(vacancies) == 1

    def test_add_vacancy_no_duplicates(self, json_saver, mock_vacancy):
        """Дубликаты по URL не добавляются"""
        # Создаем вторую вакансию с тем же URL
        vacancy2 = Mock(spec=Vacancy)
        vacancy2.to_dict.return_value = {
            "title": "Different Job",
            "url": "https://test.com/vacancy/1",  # Тот же URL!
            "salary": 200000,
            "description": "Different"
        }

        json_saver.add_vacancy(mock_vacancy)
        json_saver.add_vacancy(vacancy2)  # Не должна добавиться

        assert len(json_saver.get_vacancies()) == 1

    def test_delete_vacancy(self, json_saver, mock_vacancy):
        """Удаление вакансии"""
        json_saver.add_vacancy(mock_vacancy)
        json_saver.delete_vacancy(mock_vacancy)
        assert len(json_saver.get_vacancies()) == 0

    def test_get_vacancies_no_criteria(self, json_saver, mock_vacancy):
        """Получение всех вакансий без фильтров"""
        json_saver.add_vacancy(mock_vacancy)

        result = json_saver.get_vacancies()  # Без аргументов
        assert len(result) == 1

        result_none = json_saver.get_vacancies(None)  # С явным None
        assert len(result_none) == 1

    def test_clear_all(self, json_saver, mock_vacancy):
        """Очистка всех вакансий"""
        json_saver.add_vacancy(mock_vacancy)
        json_saver.clear_all()
        assert len(json_saver.get_vacancies()) == 0

    def test_corrupted_json_handling(self, corrupted_json_file):
        """Упрощенный тест обработки поврежденного JSON"""

        saver = JSONSaver(corrupted_json_file)

        result = saver.get_vacancies()
        assert result == []

        vacancy = Mock()
        vacancy.to_dict.return_value = {
            "title": "Test",
            "url": "https://test.com",
            "salary": 100000,
            "description": "Test"
        }

        saver.add_vacancy(vacancy)
        assert len(saver.get_vacancies()) == 1

    def test_get_top_n_by_salary(self, temp_json_file):
        """Получение топ N вакансий по зарплате"""
        saver = JSONSaver(temp_json_file)

        # Мокаем Vacancy.from_dict
        with patch('src.json_saver.Vacancy.from_dict') as mock_from_dict:
            # Создаем моки с разными зарплатами
            mock_vacancies = []
            salaries = [50000, 200000, 100000]

            for salary in salaries:
                mock_vac = Mock(spec=Vacancy)
                mock_vac.salary = salary
                mock_vacancies.append(mock_vac)

            mock_from_dict.side_effect = mock_vacancies

            # Сохраняем данные напрямую
            test_data = [
                {"title": "Job 1", "salary": 50000},
                {"title": "Job 2", "salary": 200000},
                {"title": "Job 3", "salary": 100000}
            ]
            with open(temp_json_file, 'w') as f:
                json.dump(test_data, f)

            # Топ 2
            result = saver.get_top_n_by_salary(2)
            assert len(result) == 2
            assert result[0].salary == 200000
            assert result[1].salary == 100000

    def test_stub_methods(self, json_saver):
        """Тест заглушек для БД"""
        # get_vacancy_by_id всегда возвращает None
        assert json_saver.get_vacancy_by_id("any_id") is None

        # delete_vacancy_by_id всегда возвращает False
        assert json_saver.delete_vacancy_by_id("any_id") is False

    def test_get_vacancies_with_keyword_in_title(self, temp_json_file):
        """Поиск по ключевому слову в названии"""
        saver = JSONSaver(temp_json_file)

        # Сохраняем данные напрямую
        test_data = [
            {"title": "Python Developer", "salary": 100000, "url": "url1"},
            {"title": "Java Developer", "salary": 120000, "url": "url2"}
        ]

        with open(temp_json_file, 'w') as f:
            json.dump(test_data, f)

        # Мокаем Vacancy.from_dict
        with patch('src.json_saver.Vacancy.from_dict') as mock_from_dict:
            mock_vac1 = Mock()
            mock_vac1.title = "Python Developer"
            mock_vac1.description = ""
            mock_vac1.salary = 100000

            mock_vac2 = Mock()
            mock_vac2.title = "Java Developer"
            mock_vac2.description = ""
            mock_vac2.salary = 120000

            mock_from_dict.side_effect = [mock_vac1, mock_vac2]

            # Ищем Python
            result = saver.get_vacancies({'keyword': 'python'})
            assert len(result) == 1
            assert result[0].title == "Python Developer"

    def test_get_vacancies_with_keyword_in_description(self, temp_json_file):
        """Поиск по ключевому слову в описании"""
        saver = JSONSaver(temp_json_file)

        test_data = [
            {"title": "Job1", "description": "Python required", "salary": 100000, "url": "url1"},
            {"title": "Job2", "description": "Java required", "salary": 120000, "url": "url2"}
        ]

        with open(temp_json_file, 'w') as f:
            json.dump(test_data, f)

        with patch('src.json_saver.Vacancy.from_dict') as mock_from_dict:
            mock_vac1 = Mock()
            mock_vac1.title = "Job1"
            mock_vac1.description = "Python required"
            mock_vac1.salary = 100000

            mock_vac2 = Mock()
            mock_vac2.title = "Job2"
            mock_vac2.description = "Java required"
            mock_vac2.salary = 120000

            mock_from_dict.side_effect = [mock_vac1, mock_vac2]

            result = saver.get_vacancies({'keyword': 'python'})
            assert len(result) == 1

    def test_get_vacancies_with_salary_filters(self, temp_json_file):
        """Фильтрация по зарплате"""
        saver = JSONSaver(temp_json_file)

        test_data = [
            {"title": "Low", "salary": 50000, "url": "url1"},
            {"title": "High", "salary": 150000, "url": "url2"}
        ]

        with open(temp_json_file, 'w') as f:
            json.dump(test_data, f)

        with patch('src.json_saver.Vacancy.from_dict') as mock_from_dict:
            mock_vac1 = Mock()
            mock_vac1.salary = 50000
            mock_vac1.title = "Low"
            mock_vac1.description = ""

            mock_vac2 = Mock()
            mock_vac2.salary = 150000
            mock_vac2.title = "High"
            mock_vac2.description = ""

            mock_from_dict.side_effect = [mock_vac1, mock_vac2]

            # min_salary
            result_min = saver.get_vacancies({'min_salary': 100000})
            assert len(result_min) == 1
            assert result_min[0].salary == 150000

            # Нужно сбросить mock для второго теста
            mock_from_dict.side_effect = [mock_vac1, mock_vac2]

            # max_salary
            result_max = saver.get_vacancies({'max_salary': 100000})
            assert len(result_max) == 1
            assert result_max[0].salary == 50000

    def test_get_vacancies_with_salary_only(self, temp_json_file):
        """Только вакансии с зарплатой"""
        saver = JSONSaver(temp_json_file)

        test_data = [
            {"title": "With Salary", "salary": 100000, "url": "url1"},
            {"title": "No Salary", "salary": 0, "url": "url2"}
        ]

        with open(temp_json_file, 'w') as f:
            json.dump(test_data, f)

        with patch('src.json_saver.Vacancy.from_dict') as mock_from_dict:
            mock_vac1 = Mock()
            mock_vac1.salary = 100000
            mock_vac1.title = "With Salary"

            mock_vac2 = Mock()
            mock_vac2.salary = 0
            mock_vac2.title = "No Salary"

            mock_from_dict.side_effect = [mock_vac1, mock_vac2]

            result = saver.get_vacancies({'with_salary_only': True})
            assert len(result) == 1
            assert result[0].salary == 100000
