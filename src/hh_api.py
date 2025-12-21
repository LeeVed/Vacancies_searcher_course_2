import requests
from typing import List, Dict, Any
from src.base_vacancy import VacancyAPI
from src.vacancy import Vacancy


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    # Константы для кодов регионов
    RUSSIA_AREA_ID = 113

    def __init__(self):
        super().__init__(
            base_url="https://api.hh.ru",
            headers={"User-Agent": "MyVacancyParser/1.0"}
        )
        self._connected = False

    def connect(self) -> bool:
        """
        Подключение к API HeadHunter.
        Проверяет доступность API.
        """
        try:
            response = self._make_request("/vacancies", params={
                "text": "test",
                "per_page": 1
            })
            self._connected = response.status_code == 200
            return self._connected
        except Exception:
            self._connected = False
            return False

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получение вакансий с HH.ru по поисковому запросу"""

        # Проверка подключения
        if not self._connected:
            if not self.connect():
                return []  # API недоступно

        params = {
            "text": search_query,
            "area": self.RUSSIA_AREA_ID,  # Поиск по России
            "per_page": min(kwargs.get("per_page", 50), 100),  # Макс. 100 для HH
            "page": kwargs.get("page", 0)
        }

        try:
            # Выполняем запрос
            response = self._make_request("/vacancies", params=params)

            if response.status_code != 200:
                return []  # API вернуло ошибку

            # Парсим ответ
            data = response.json()
            vacancies_data = data.get("items", [])

            # Преобразуем в формат приложения
            vacancies_result = []

            for vacancy_data in vacancies_data:
                # Проверяем что это данные API
                if not isinstance(vacancy_data, dict):
                    continue

                if 'name' not in vacancy_data and 'id' not in vacancy_data:
                    continue

                try:
                    vacancy = Vacancy.from_hh_data(vacancy_data)
                    vacancies_result.append(vacancy.to_dict())
                except Exception:
                    # Пропускаем некорректные вакансии
                    continue

            return vacancies_result

        except requests.exceptions.RequestException:
            # Ошибка сети
            return []
        except Exception:
            # Любая другая ошибка
            return []
