from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов вакансий"""

    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers or {}

    @abstractmethod
    def _connect(self) -> bool:
        """Подключение к API сервиса"""

        pass

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получить вакансии по поисковому запросу"""

        pass

    def _make_request(self, endpoint: str, params: dict = None):
        """Общий метод для HTTP-запросов"""

        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()  # Проверяем статус код
            return response
        except requests.RequestException as e:
            print(f"Ошибка при запросе к {url}: {e}")
            raise
