import pytest
import re
from src.vacancy import Vacancy


class TestVacancy:
    """Тесты для класса Vacancy"""

    # Тесты инициализации(2)
    def test_init_with_all_parameters(self):
        """Тест создания вакансии со всеми параметрами"""

        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/123",
            salary=150000.0,
            description="Разработка на Python"
        )

        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123"
        assert vacancy.salary == 150000.0
        assert vacancy.description == "Разработка на Python"

    def test_init_with_minimal_parameters(self):
        """Тест создания вакансии с минимальными параметрами"""

        vacancy = Vacancy(
            title="Developer",
            url="https://hh.ru/vacancy/456"
        )

        assert vacancy.title == "Developer"
        assert vacancy.url == "https://hh.ru/vacancy/456"
        assert vacancy.salary == 0.0  # По умолчанию
        assert vacancy.description == "Описание отсутствует" # По умолчанию

    # Тесты валидации (7)
    def test_validate_title_empty(self):
        """Тест валидации пустого названия"""

        vacancy = Vacancy(title="", url="https://test.com")
        assert vacancy.title == "Без названия"

    def test_validate_url_invalid(self):
        """Тест валидации некорректного URL"""

        # Без http/https
        vacancy1 = Vacancy(title="Test", url="hh.ru/vacancy/123")
        assert vacancy1.url == ""

        # Пустая строка
        vacancy2 = Vacancy(title="Test", url="")
        assert vacancy2.url == ""

        # Не строка
        vacancy3 = Vacancy(title="Test", url=None)
        assert vacancy3.url == ""

    def test_validate_url_valid(self):
        """Тест валидации корректного URL"""

        vacancy1 = Vacancy(title="Test", url="https://hh.ru/vacancy/123")
        assert vacancy1.url == "https://hh.ru/vacancy/123"

        vacancy2 = Vacancy(title="Test", url="http://example.com")
        assert vacancy2.url == "http://example.com"

    def test_validate_salary_positive(self):
        """Тест валидации положительной зарплаты"""

        vacancy = Vacancy(title="Test", url="https://test.com", salary=100000.5)
        assert vacancy.salary == 100000.5

    def test_validate_salary_negative(self):
        """Тест валидации отрицательной зарплаты"""
        vacancy = Vacancy(title="Test", url="https://test.com", salary=-50000)
        assert vacancy.salary == 0.0  # Отрицательная становится 0

    def test_validate_salary_none(self):
        """Тест валидации отсутствующей зарплаты"""

        vacancy = Vacancy(title="Test", url="https://test.com", salary=None)
        assert vacancy.salary == 0.0

    def test_validate_description_empty(self):
        """Тест валидации пустого описания"""

        vacancy1 = Vacancy(title="Test", url="https://test.com", description="")
        assert vacancy1.description == "Описание отсутствует"

        vacancy2 = Vacancy(title="Test", url="https://test.com", description=None)
        assert vacancy2.description == "Описание отсутствует"

        vacancy3 = Vacancy(title="Test", url="https://test.com", description="   ")
        assert vacancy3.description == "Описание отсутствует"

    # Тесты сравнения (7)
    def test_eq_same_salary(self):
        """Тест равенства вакансий с одинаковой зарплатой"""

        v1 = Vacancy("Job1", "url1", 100000)
        v2 = Vacancy("Job2", "url2", 100000)
        assert v1 == v2

    def test_eq_different_salary(self):
        """Тест равенства вакансий с разной зарплатой"""

        v1 = Vacancy("Job1", "url1", 100000)
        v2 = Vacancy("Job2", "url2", 150000)
        assert not (v1 == v2)

    def test_eq_with_non_vacancy(self):
        """Тест сравнения с не-вакансией"""
        vacancy = Vacancy("Test", "url", 100000)
        assert not (vacancy == "not a vacancy")
        assert not (vacancy == 123)
        assert not (vacancy == None)

    def test_less_than(self):
        """Тест оператора <"""

        v1 = Vacancy("Junior", "url1", 50000)
        v2 = Vacancy("Senior", "url2", 150000)

        assert v1 < v2
        assert not (v2 < v1)

    def test_greater_than(self):
        """Тест оператора >"""

        v1 = Vacancy("Senior", "url1", 150000)
        v2 = Vacancy("Junior", "url2", 50000)

        assert v1 > v2
        assert not (v2 > v1)

    def test_less_or_equal(self):
        """Тест оператора <="""

        v1 = Vacancy("Junior", "url1", 50000)
        v2 = Vacancy("Middle", "url2", 100000)
        v3 = Vacancy("Another", "url3", 50000)

        assert v1 <= v2
        assert v1 <= v3  # Равные зарплаты
        assert not (v2 <= v1)

    def test_greater_or_equal(self):
        """Тест оператора >="""

        v1 = Vacancy("Senior", "url1", 150000)
        v2 = Vacancy("Middle", "url2", 100000)
        v3 = Vacancy("Another", "url3", 150000)

        assert v1 >= v2
        assert v1 >= v3  # Равные зарплаты
        assert not (v2 >= v1)

    # Тесты строкового представления (4)
    def test_str_representation(self):
        """Тест строкового представления"""

        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/123",
            salary=150000,
            description="Разработка на Python и Django"
        )

        str_repr = str(vacancy)

        assert "Должность: Python Developer" in str_repr
        assert "Зарплата: 150 000 руб." in str_repr
        assert "Ссылка: https://hh.ru/vacancy/123" in str_repr
        assert "Описание: Разработка на Python и Django" in str_repr

    def test_str_no_salary(self):
        """Тест строкового представления без зарплаты"""

        vacancy = Vacancy(
            title="Developer",
            url="https://hh.ru/vacancy/456",
            salary=0.0,
            description="Test"
        )

        str_repr = str(vacancy)
        assert "Зарплата: Не указана" in str_repr

    def test_str_no_url(self):
        """Тест строкового представления без URL"""

        vacancy = Vacancy(
            title="Developer",
            url="",  # Некорректный URL
            salary=100000
        )

        str_repr = str(vacancy)
        assert "Ссылка: Нет ссылки" in str_repr

    def test_repr_representation(self):
        """Тест repr представления"""

        vacancy = Vacancy("Python Developer", "url", 150000)
        repr_str = repr(vacancy)

        assert "Vacancy(" in repr_str
        assert "'Python Developer'" in repr_str
        assert "salary=150000" in repr_str

    # Тесты преобразования (2)
    def test_to_dict(self):
        """Тест преобразования в словарь"""

        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/123",
            salary=150000.5,
            description="Разработка"
        )

        data = vacancy.to_dict()

        assert data["title"] == "Python Developer"
        assert data["url"] == "https://hh.ru/vacancy/123"
        assert data["salary"] == 150000.5
        assert data["description"] == "Разработка"
        assert len(data) == 4  # Только 4 поля

    def test_from_dict_standard(self):
        """Тест создания из стандартного словаря"""

        data = {
            "title": "Python Developer",
            "url": "https://test.com",
            "salary": 100000,
            "description": "Test description"
        }

        vacancy = Vacancy.from_dict(data)

        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://test.com"
        assert vacancy.salary == 100000
        assert vacancy.description == "Test description"

    # Тесты HH API данных (
    def test_from_hh_data_full(self):
        """Тест создания из полных данных HH API"""

        hh_data = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUR"
            },
            "snippet": {
                "requirement": "Опыт работы с Python",
                "responsibility": "Разработка backend"
            }
        }

        vacancy = Vacancy.from_hh_data(hh_data)

        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123"
        assert vacancy.salary == 100000.0  # Берет from
        assert "Опыт работы с Python" in vacancy.description or "Разработка backend" in vacancy.description

    def test_from_hh_data_salary_from_none(self):
        """Тест создания из HH данных когда salary.from = None"""
        hh_data = {
            "name": "Developer",
            "alternate_url": "https://hh.ru/vacancy/456",
            "salary": {
                "from": None,  # from отсутствует
                "to": 120000,  # но есть to
                "currency": "RUR"
            },
            "snippet": {}
        }

        vacancy = Vacancy.from_hh_data(hh_data)
        assert vacancy.salary == 120000.0  # Должен взять to

    def test_from_hh_data_no_salary(self):
        """Тест создания из HH данных без зарплаты"""

        hh_data = {
            "name": "Developer",
            "alternate_url": "https://hh.ru/vacancy/789",
            "salary": None,  # Нет зарплаты
            "snippet": {}
        }

        vacancy = Vacancy.from_hh_data(hh_data)
        assert vacancy.salary == 0.0

    def test_from_hh_data_html_in_description(self):
        """Тест очистки HTML из описания"""

        hh_data = {
            "name": "Developer",
            "alternate_url": "https://hh.ru/vacancy/999",
            "salary": {"from": 100000},
            "snippet": {
                "requirement": "<strong>Python</strong> experience<br/>Required",
                "responsibility": "Develop <em>backend</em>"
            }
        }

        vacancy = Vacancy.from_hh_data(hh_data)
        # Проверяем, что HTML теги удалены
        assert "<" not in vacancy.description
        assert ">" not in vacancy.description
        assert "Python experience" in vacancy.description