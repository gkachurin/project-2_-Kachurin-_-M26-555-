import json
import os

from .constants import DATA_DIR


def _read_json(filepath, default):
    """Читает JSON-файл."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _write_json(filepath, data):
    """Записывает данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_table_path(table_name):
    """Возвращает путь к файлу с данными таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_metadata(filepath):
    """Загружает метаданные."""
    return _read_json(filepath, {})


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    _write_json(filepath, data)


def load_table_data(table_name):
    """Загружает записи таблицы."""
    return _read_json(get_table_path(table_name), [])


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    _write_json(get_table_path(table_name), data)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он есть."""
    try:
        os.remove(get_table_path(table_name))
    except FileNotFoundError:
        pass
