from pathlib import Path

BASE_DIR = Path(__file__).parent
print(f"BASE_DIR: {BASE_DIR}")

DATA_DIR = BASE_DIR / "data"
print(f"DATA_DIR: {DATA_DIR}")
DATA_DIR.mkdir(exist_ok=True)

VACANCIES_JSON = DATA_DIR / "vacancies.json"
print(f"VACANCIES_JSON: {VACANCIES_JSON}")
print(f"Файл существует? {VACANCIES_JSON.exists()}")