from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов с вакансиями"""

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Функция получает вакансии по поисковому запросу и
        возвращает список словарей с данными о вакансиях
        """
        pass

    @abstractmethod
    def _validate_response(self, response) -> bool:
        """
        Валидация ответа от API и возвращает булево значение True если ответ валидный, иначе False
        """
        pass
