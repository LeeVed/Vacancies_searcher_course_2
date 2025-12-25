import pytest
from unittest.mock import Mock, patch
import requests

from src.base_vacancy import VacancyAPI
from src.hh_api import HeadHunterAPI


class TestVacancyAPI:
    """Тесты для абстрактного класса VacancyAPI"""

    def test_headhunter_api_is_valid_implementation(self):
        """Проверяем, что HeadHunterAPI — корректный наследник."""

        api = HeadHunterAPI()
        # Проверяем, что HeadHunterAPI наследник
        assert isinstance(api, VacancyAPI)
        # Проверяем, что у него есть обязательные методы
        assert hasattr(api, 'connect') and callable(api.connect)
        assert hasattr(api, 'get_vacancies') and callable(api.get_vacancies)

    def test_initialization_of_concrete_class(self):
        """Тест инициализации через HeadHunterAPI."""
        api = HeadHunterAPI()

        assert hasattr(api, 'base_url')
        assert hasattr(api, 'headers')
        print(f"Создан API с базовым URL: {api.base_url}")

    @patch('requests.get')
    def test_make_request_method(self, mock_requests_get):
        """Тестируем общий метод _make_request (используем HeadHunterAPI)."""
        # mock-объект для requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_requests_get.return_value = mock_response

        # создаем API и вызываем тестируемый метод
        api = HeadHunterAPI()

        response = api._make_request("/vacancies", params={"text": "python"})

        # проверка
        mock_requests_get.assert_called_once()
        assert response == mock_response

    @patch('requests.get')
    def test_make_request_handles_errors(self, mock_requests_get):
        """Проверяем, что _make_request корректно пробрасывает ошибки."""
        # Настраиваем mock так, чтобы он вызвал исключение
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Нет сети")

        api = HeadHunterAPI()

        with pytest.raises(requests.exceptions.RequestException):
            api._make_request("/vacancies")
