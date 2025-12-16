import requests
import re
from typing import List, Dict, Any, Optional

# Импортируем абстрактный класс
from base_vacancy import VacancyAPI


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        """Инициализация класса для работы с API HH.ru"""
        self.base_url = "https://api.hh.ru/vacancies"
        self.headers = {
            "User-Agent": "HH-Client/1.0 (your-email@example.com)"
        }

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Получение вакансий с HH.ru по поисковому запросу

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры:
                - per_page: Количество вакансий на странице (по умолчанию 50)
                - page: Номер страницы (по умолчанию 0)
                - area: Регион поиска (по умолчанию 113 - Россия)
                - only_with_salary: Только с указанием зарплаты (по умолчанию False)
                - salary: Минимальная зарплата

        Returns:
            Список словарей с данными о вакансиях
        """
        params = {
            "text": search_query,
            "per_page": kwargs.get("per_page", 50),
            "page": kwargs.get("page", 0),
            "area": kwargs.get("area", 113),  # 113 - Россия
            "only_with_salary": kwargs.get("only_with_salary", False),
        }

        # Добавляем параметр зарплаты, если указан
        if kwargs.get("salary"):
            params["salary"] = kwargs["salary"]

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)

            if not self._validate_response(response):
                print(f"Ошибка при запросе к API: {response.status_code}")
                return []

            data = response.json()
            vacancies = data.get("items", [])

            return self._parse_vacancies(vacancies)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к API: {e}")
            return []
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return []

    def _validate_response(self, response) -> bool:
        """
        Валидация ответа от API HH.ru

        Args:
            response: Ответ от API

        Returns:
            True если ответ валидный, иначе False
        """
        return response.status_code == 200

    def _parse_vacancies(self, raw_vacancies: List[Dict]) -> List[Dict[str, Any]]:
        """
        Парсинг и нормализация данных о вакансиях

        Args:
            raw_vacancies: Сырые данные о вакансиях из API

        Returns:
            Нормализованный список вакансий
        """
        parsed_vacancies = []

        for vacancy in raw_vacancies:
            # Получаем зарплату (может быть указана от, до, или обе границы)
            salary_info = vacancy.get("salary")
            salary = None
            if salary_info:
                salary_from = salary_info.get("from")
                salary_to = salary_info.get("to")
                currency = salary_info.get("currency", "RUR")

                if salary_from and salary_to:
                    salary = (salary_from + salary_to) / 2
                elif salary_from:
                    salary = salary_from
                elif salary_to:
                    salary = salary_to
                else:
                    salary = None

                if salary and currency != "RUR":
                    # Можно добавить конвертацию валют, если нужно
                    pass

            # Формируем нормализованную вакансию
            parsed_vacancy = {
                "id": vacancy.get("id"),
                "title": vacancy.get("name"),
                "company": vacancy.get("employer", {}).get("name") if vacancy.get("employer") else "Не указано",
                "salary": salary,
                "currency": salary_info.get("currency") if salary_info else None,
                "salary_from": salary_info.get("from") if salary_info else None,
                "salary_to": salary_info.get("to") if salary_info else None,
                "url": vacancy.get("alternate_url"),
                "description": self._clean_description(vacancy.get("snippet", {}).get("requirement", "")),
                "requirements": vacancy.get("snippet", {}).get("requirement", ""),
                "responsibility": vacancy.get("snippet", {}).get("responsibility", ""),
                "experience": vacancy.get("experience", {}).get("name") if vacancy.get("experience") else "Не указано",
                "employment_type": vacancy.get("employment", {}).get("name") if vacancy.get(
                    "employment") else "Не указано",
                "schedule": vacancy.get("schedule", {}).get("name") if vacancy.get("schedule") else "Не указано",
                "published_at": vacancy.get("published_at"),
                "city": vacancy.get("area", {}).get("name") if vacancy.get("area") else "Не указано",
                "raw_data": vacancy  # Оставляем сырые данные на всякий случай
            }
            parsed_vacancies.append(parsed_vacancy)

        return parsed_vacancies

    def _clean_description(self, description: str) -> str:
        """
        Очистка описания от HTML-тегов

        Args:
            description: Описание с HTML-тегами

        Returns:
            Очищенное описание
        """
        if not description:
            return ""

        # Очистка от HTML-тегов
        clean_text = re.sub(r'<[^>]+>', '', description)
        return clean_text.strip()

    def get_vacancy_by_id(self, vacancy_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение конкретной вакансии по ID

        Args:
            vacancy_id: ID вакансии

        Returns:
            Словарь с данными о вакансии или None
        """
        try:
            url = f"{self.base_url}/{vacancy_id}"
            response = requests.get(url, headers=self.headers)

            if self._validate_response(response):
                vacancy_data = response.json()
                return self._parse_vacancies([vacancy_data])[0]
            else:
                print(f"Ошибка при получении вакансии {vacancy_id}: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к API: {e}")
            return None
