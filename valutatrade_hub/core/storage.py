"""Чтение и запись данных ValutaTrade Hub в JSON-файлы.

Модуль работает только с «сырыми» dict/list. Не импортирует модели —
это разделяет ответственность: модели знают, как они выглядят (to_dict),
storage знает, как положить эти данные в файл.
"""

import json
from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
PORTFOLIOS_FILE = DATA_DIR / "portfolios.json"


def _read_json(file_path: Path) -> list:
    """Прочитать JSON-список. Если файла нет - вернуть []."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exec:
        raise ValueError(f"Файл {file_path} поврежден: {exec}")


def _write_json(path: Path, data: list) -> None:
    """Записать JSON-список. Создать родительскую папку, если нужно"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_users_data() -> list[dict]:
    """Загрузить данные о пользователях из JSON-файла."""
    return _read_json(USERS_FILE)


def save_users_data(users: list[dict]) -> None:
    _write_json(USERS_FILE, users)


def load_portfolios_data() -> list[dict]:
    """Загрузить данные о портфелях из JSON-файла."""
    return _read_json(PORTFOLIOS_FILE)


def save_portfolios_data(portfolios: list[dict]) -> None:
    _write_json(PORTFOLIOS_FILE, portfolios)
