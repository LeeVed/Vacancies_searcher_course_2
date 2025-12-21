from typing import Optional, Dict, Any
import re


class Vacancy:
    """Класс для представления вакансии с 4 атрибутами"""

    __slots__ = ('title', 'url', 'salary', 'description')

    def __init__(self, title: str, url: str, salary: Optional[float] = None,
                 description: str = ""):
        """Инициализация вакансии"""

        self.title = self._validate_title(title)
        self.url = self._validate_url(url)
        self.salary = self._validate_salary(salary)
        self.description = self._validate_description(description)

    # Методы валидации
    def _validate_title(self, title: str) -> str:
        """Валидация названия вакансии."""
        if not title or not isinstance(title, str):
            return "Без названия"
        return title.strip() or "Без названия"

    def _validate_url(self, url: str) -> str:
        """Валидация URL вакансии."""
        if not url or not isinstance(url, str):
            return ""
        url = url.strip()
        return url if url.startswith(('http://', 'https://')) else ""

    def _validate_salary(self, salary: Optional[float]) -> float:
        """Валидация зарплаты."""
        if salary is None:
            return 0.0
        try:
            salary_float = float(salary)
            return salary_float if salary_float >= 0 else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _validate_description(self, description: str) -> str:
        """Валидация описания вакансии."""
        if not description or not isinstance(description, str):
            return "Описание отсутствует"
        description = description.strip()
        if not description:
            return "Описание отсутствует"
        description = re.sub(r'\s+', ' ', description)
        return description[:500] + "..." if len(description) > 500 else description

    # Методы сравнения по зарплате
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return False
        return self.salary == other.salary

    def __lt__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary < other.salary

    def __le__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary <= other.salary

    def __gt__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary > other.salary

    def __ge__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary >= other.salary

    # Представление для пользователя
    def __str__(self) -> str:
        """Строковое представление для пользователя."""
        salary_str = f"{self.salary:,.0f} руб.".replace(",", " ") if self.salary > 0 else "Не указана"
        desc_preview = self.description[:100] + "..." if len(self.description) > 100 else self.description

        return (f"Должность: {self.title}\n"
                f"Зарплата: {salary_str}\n"
                f"Описание: {desc_preview}\n"
                f"Ссылка: {self.url if self.url else 'Нет ссылки'}")

    def __repr__(self) -> str:
        return f"Vacancy('{self.title}', salary={self.salary})"

    # Преобразование в словарь
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения."""
        return {
            "title": self.title,
            "url": self.url,
            "salary": self.salary,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создание Vacancy из словаря"""

        # Поддержка разных форматов данных
        title = data.get("title") or data.get("name") or ""
        description = data.get("description") or data.get("responsibility") or ""
        url = data.get("url") or data.get("alternate_url") or ""
        salary = data.get("salary")

        return cls(
            title=title,
            url=url,
            salary=salary,
            description=description
        )

    @classmethod
    def from_hh_data(cls, hh_vacancy: Dict[str, Any]) -> 'Vacancy':
        """Создание Vacancy из данных HH API"""

        # Извлечение данных из API HH
        title = hh_vacancy.get("name", "")
        url = hh_vacancy.get("alternate_url", "")

        # Извлечение зарплаты
        salary = None
        salary_data = hh_vacancy.get("salary")
        if salary_data and isinstance(salary_data, dict):
            salary_from = salary_data.get("from")
            salary_to = salary_data.get("to")
            if salary_from is not None:
                salary = float(salary_from)
            elif salary_to is not None:
                salary = float(salary_to)

        # Извлечение и очистка описания
        description = ""
        snippet = hh_vacancy.get("snippet", {})
        if isinstance(snippet, dict):
            description = snippet.get("requirement", "") or snippet.get("responsibility", "")
            if description:
                description = re.sub(r'<[^>]+>', '', description)

        return cls(
            title=title,
            url=url,
            salary=salary,
            description=description
        )
