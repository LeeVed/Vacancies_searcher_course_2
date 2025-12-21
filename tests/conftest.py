import pytest
from unittest.mock import Mock, patch
import requests
from src.base_vacancy import VacancyAPI


@pytest.fixture
def mock_vacancy_api():
    """Фикстура для создания тестового экземпляра VacancyAPI"""

    class TestAPI(VacancyAPI):
        def connect(self):
            return True

        def get_vacancies(self, search_query, **kwargs):
            return [{"name": f"Test {search_query} Position"}]

    return TestAPI("https://api.test.com")


@pytest.fixture
def mock_requests_get():
    """Фикстура для мокирования requests.get"""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def successful_response():
    """Фикстура для успешного HTTP-ответа"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"items": [], "found": 0}
    return response


@pytest.fixture
def error_response():
    """Фикстура для ошибки HTTP"""
    response = Mock()
    response.status_code = 404
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
    return response


import tempfile
from pathlib import Path
from unittest.mock import Mock
import json


@pytest.fixture
def temp_json_file():
    """Создает временный JSON файл для тестов JSONSaver"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w', encoding='utf-8') as f:
        tmp_path = Path(f.name)

    yield tmp_path  # Передаем путь тесту

    # После теста удаляем
    if tmp_path.exists():
        tmp_path.unlink()


@pytest.fixture
def json_saver(temp_json_file):
    """Фикстура для создания JSONSaver с временным файлом"""
    from src.json_saver import JSONSaver
    return JSONSaver(temp_json_file)


@pytest.fixture
def mock_vacancy():
    """Фикстура для создания мока Vacancy"""
    vacancy = Mock()
    vacancy.to_dict.return_value = {
        "title": "Test Developer",
        "url": "https://test.com/vacancy/1",
        "salary": 100000,
        "description": "Test description"
    }
    vacancy.url = "https://test.com/vacancy/1"
    # Добавляем другие необходимые атрибуты, если нужно
    vacancy.title = "Test Developer"
    vacancy.salary = 100000
    vacancy.description = "Test description"
    return vacancy


@pytest.fixture
def mock_vacancy_without_url():
    """Фикстура для Vacancy без URL (для тестов валидации)"""
    vacancy = Mock(spec='src.vacancy.Vacancy')
    vacancy.to_dict.return_value = {
        "title": "Test Job",
        "url": "",  # Пустой URL
        "salary": 0,
        "description": "Test"
    }
    vacancy.url = ""
    return vacancy


@pytest.fixture
def sample_vacancy_data():
    """Пример данных вакансии для тестов"""
    return {
        "title": "Python Developer",
        "url": "https://hh.ru/vacancy/123",
        "salary": 150000.0,
        "description": "Python development experience required"
    }


@pytest.fixture
def corrupted_json_file():
    """Создает временный файл с поврежденным JSON"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w', encoding='utf-8') as f:
        tmp_path = Path(f.name)
        f.write('{invalid json')  # Поврежденный JSON

    yield tmp_path

    if tmp_path.exists():
        tmp_path.unlink()
