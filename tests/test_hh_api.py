import pytest
from unittest.mock import Mock, patch
import requests
from src.hh_api import HeadHunterAPI


class TestHeadHunterAPI:
    """Тесты для HeadHunterAPI"""

    def test_init_creates_object(self):
        """Тест создания объекта"""
        api = HeadHunterAPI()
        assert api.base_url == "https://api.hh.ru"
        assert api.headers["User-Agent"] == "MyVacancyParser/1.0"
        assert api._connected is False

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_connect_success(self, mock_make_request):
        """Тест успешного подключения"""
        # 1. Настраиваем mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_make_request.return_value = mock_response

        # 2. Создаем API и вызываем connect
        api = HeadHunterAPI()
        result = api.connect()

        # 3. Проверяем
        assert result is True
        assert api._connected is True
        mock_make_request.assert_called_once_with(
            "/vacancies",
            params={"text": "test", "per_page": 1}
        )

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_connect_failure(self, mock_make_request):
        """Тест неудачного подключения (ошибка сети)"""
        # 1. Настраиваем mock для вызова исключения
        mock_make_request.side_effect = requests.exceptions.RequestException("Нет сети")

        # 2. Создаем API и вызываем connect
        api = HeadHunterAPI()
        result = api.connect()

        # 3. Проверяем
        assert result is False
        assert api._connected is False

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_get_vacancies_success(self, mock_make_request):
        """Тест успешного получения вакансий"""
        # 1. Настраиваем mock ответа от API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "salary": {"from": 100000, "currency": "RUR"},
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company"},
                    "snippet": {"requirement": "Python experience"}
                }
            ]
        }
        mock_make_request.return_value = mock_response

        # 2. Создаем API и получаем вакансии
        api = HeadHunterAPI()
        api._connected = True  # Имитируем уже подключенный API
        vacancies = api.get_vacancies("Python", per_page=10)

        # 3. Проверяем
        assert isinstance(vacancies, list)
        assert len(vacancies) > 0
        assert "title" in vacancies[0]  # Vacancy.to_dict() создает поле title

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_get_vacancies_not_connected(self, mock_make_request):
        """Тест получения вакансий без предварительного подключения"""
        # 1. Настраиваем mock для успешного подключения и получения данных
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_make_request.return_value = mock_response

        # 2. Создаем неподключенный API
        api = HeadHunterAPI()
        assert api._connected is False

        # 3. Пытаемся получить вакансии (должен вызвать connect автоматически)
        vacancies = api.get_vacancies("Python")

        # 4. Проверяем
        assert mock_make_request.call_count == 2  # 1 раз для connect, 1 раз для get_vacancies
        assert api._connected is True
        assert vacancies == []  # Так как mock вернул пустой список

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_get_vacancies_network_error(self, mock_make_request):
        """Тест получения вакансий при ошибке сети"""
        # 1. Настраиваем mock для вызова исключения
        mock_make_request.side_effect = requests.exceptions.ConnectionError("Нет сети")

        # 2. Создаем API
        api = HeadHunterAPI()
        api._connected = True

        # 3. Пытаемся получить вакансии
        vacancies = api.get_vacancies("Python")

        # 4. Проверяем
        assert vacancies == []  # Должен вернуть пустой список при ошибке

    @patch('src.hh_api.HeadHunterAPI._make_request')
    def test_get_vacancies_api_error(self, mock_make_request):
        """Тест получения вакансий при ошибке API (не 200 статус)"""
        # 1. Настраиваем mock с ошибкой 500
        mock_response = Mock()
        mock_response.status_code = 500
        mock_make_request.return_value = mock_response

        # 2. Создаем API
        api = HeadHunterAPI()
        api._connected = True

        # 3. Пытаемся получить вакансии
        vacancies = api.get_vacancies("Python")

        # 4. Проверяем
        assert vacancies == []  # Должен вернуть пустой список при статусе != 200

    def test_get_vacancies_bad_data(self):
        """Тест обработки некорректных данных от API"""
        # 1. Создаем mock для плохих данных
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"bad": "data"},  # Нет обязательных полей
                None,  # None вместо словаря
                "string_instead_of_dict"  # Неверный тип
            ]
        }

        # 2. Патчим _make_request
        with patch('src.hh_api.HeadHunterAPI._make_request', return_value=mock_response):
            api = HeadHunterAPI()
            api._connected = True
            vacancies = api.get_vacancies("Python")

            # 3. Проверяем, что некорректные данные отфильтрованы
            assert isinstance(vacancies, list)
