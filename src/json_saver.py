import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from unittest.mock import Mock

from config import VACANCIES_JSON
from src.vacancy import Vacancy


class BaseSaver(ABC):
    """Абстрактный класс для работы с хранилищем вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавить вакансию в хранилище"""

        pass

    @abstractmethod
    def get_vacancies(self, criteria: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """Получить вакансии по критериям"""

        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удалить вакансию из хранилища"""

        pass

    # ЗАГЛУШКИ для интеграции с БД
    @abstractmethod
    def get_vacancy_by_id(self, vacancy_id: str) -> Optional[Vacancy]:
        """
        Получить вакансию по ID.
        Заглушка для будущей интеграции с БД.
        """
        pass

    @abstractmethod
    def delete_vacancy_by_id(self, vacancy_id: str) -> bool:
        """
        Удалить вакансию по ID.
        Заглушка для будущей интеграции с БД.
        """
        pass


class JSONSaver(BaseSaver):
    """Класс для сохранения вакансий в JSON файл"""

    def __init__(self, filename: Path = VACANCIES_JSON):
        """Инициализация JSONSaver"""

        self._filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создать файл если он не существует."""

        if not self._filename.exists():
            self._write_data([])

    def _read_data(self) -> List[Dict[str, Any]]:
        """Прочитать данные из файла"""

        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Файл есть, но содержит некорректный JSON
            # Возвращаем пустой список и перезаписываем файл
            self._write_data([])
            return []

    def _write_data(self, data: List[Dict[str, Any]]) -> None:
        """Записать данные в файл"""

        self._filename.parent.mkdir(parents=True, exist_ok=True)

        with open(self._filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """
        Добавить вакансию в JSON файл.
        Проверяет на дубликаты по URL.
        """
        data = self._read_data()
        vacancy_dict = vacancy.to_dict()

        # Проверка на дубликат по URL
        for existing_vacancy in data:
            if existing_vacancy.get('url') == vacancy_dict['url']:
                return  # Вакансия уже существует

        data.append(vacancy_dict)
        self._write_data(data)

    def get_vacancies(self, criteria: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """Получить вакансии по критериям."""

        data = self._read_data()
        vacancies = [Vacancy.from_dict(v) for v in data]

        if not criteria:
            return vacancies

        filtered_vacancies = []
        for vacancy in vacancies:
            matches_all = True

            for key, value in criteria.items():
                if key == 'keyword':
                    # Поиск ключевого слова в названии или описании
                    keyword = value.lower()
                    if (keyword not in vacancy.title.lower() and
                            keyword not in vacancy.description.lower()):
                        matches_all = False
                        break

                elif key == 'min_salary':
                    # Минимальная зарплата
                    if vacancy.salary < value:
                        matches_all = False
                        break

                elif key == 'max_salary':
                    # Максимальная зарплата
                    if vacancy.salary > value:
                        matches_all = False
                        break

                elif key == 'with_salary_only':
                    # Только с зарплатой
                    if value and vacancy.salary <= 0:
                        matches_all = False
                        break

                elif hasattr(vacancy, key):
                    # Проверка других атрибутов
                    vacancy_value = getattr(vacancy, key)
                    if isinstance(vacancy_value, str) and isinstance(value, str):
                        if value.lower() not in vacancy_value.lower():
                            matches_all = False
                            break
                    elif vacancy_value != value:
                        matches_all = False
                        break

            if matches_all:
                filtered_vacancies.append(vacancy)


        return filtered_vacancies

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удалить вакансию из файла"""

        data = self._read_data()
        vacancy_url = vacancy.url

       # Фильтруем вакансии, оставляя только те, у которых URL не совпадает
        filtered_data = [
            v for v in data
            if v.get('url') != vacancy_url
        ]

        self._write_data(filtered_data)

    # ЗАГЛУШКИ для методов БД
    def get_vacancy_by_id(self, vacancy_id: str) -> Optional[Vacancy]:
        """
        Получить вакансию по ID.
        Заглушка для БД - в JSON файле нет ID.
        """
        # В JSON файле нет ID, это заглушка для БД
        return None

    def delete_vacancy_by_id(self, vacancy_id: str) -> bool:
        """
        Удалить вакансию по ID.
        Заглушка для БД - в JSON файле нет ID.
        """
        # В JSON файле нет ID, это заглушка для БД
        return False

    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ (опционально)
    def add_vacancies(self, vacancies: List[Vacancy]) -> None:
        """Добавить несколько вакансий"""

        for vacancy in vacancies:
            self.add_vacancy(vacancy)

    def get_top_n_by_salary(self, n: int) -> List[Vacancy]:
        """Получить топ N вакансий по зарплате."""

        vacancies = self.get_vacancies()
        vacancies_with_salary = [v for v in vacancies if v.salary > 0]

        # Сортировка по убыванию зарплаты
        sorted_vacancies = sorted(vacancies_with_salary, key=lambda v: v.salary, reverse=True)

        return sorted_vacancies[:n]

    def clear_all(self) -> None:
        """Очистить все вакансии из файла"""
        self._write_data([])

    def test_clear_all(self):
        """Тест очистки всех вакансий"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            saver = JSONSaver(tmp_path)

            # Добавляем вакансию
            vacancy = Mock(spec=Vacancy)
            vacancy.to_dict.return_value = {
                "title": "Python Developer",
                "salary": 100000,
                "url": "https://hh.ru/vacancy/1"
            }
            saver.add_vacancy(vacancy)

            # Очищаем
            saver.clear_all()

            # Проверяем, что файл пустой
            with open(tmp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == []

            vacancies = saver.get_vacancies()
            assert vacancies == []

            print("✓ Все вакансии успешно очищены")

        finally:
            if tmp_path.exists():
                tmp_path.unlink()