from .constants import ID_NAME, ID_TYPE, INVALID_VALUE_MSG, VALID_TYPES
from .decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from .utils import delete_table_data

cache_result = create_cacher()


def describe_columns(columns):
    """Возвращает строку вида 'ID:int, name:str'."""
    return ", ".join(f"{column['name']}:{column['type']}" for column in columns)


def table_exists(metadata, table_name):
    """Проверяет наличие таблицы."""
    if table_name in metadata:
        return True

    print(f'Ошибка: Таблица "{table_name}" не существует.')
    return False


def validate_clause(clause, columns):
    """Проверяет, что столбцы существуют, а значения подходят по типу."""
    types = {column["name"]: column["type"] for column in columns}

    for name, value in clause.items():
        if name not in types:
            print(f'Ошибка: Столбец "{name}" не существует.')
            return False

        if type(value) is not VALID_TYPES[types[name]]:
            print(f"Ошибка: Столбец {name} ожидает тип {types[name]}.")
            return False

    return True


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие."""
    return all(record.get(name) == value for name, value in where_clause.items())


def create_table(metadata, table_name, columns):
    """Создаёт таблицу (ID:int добавляется первым)."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    if not table_name.isidentifier():
        print(INVALID_VALUE_MSG.format(table_name))
        return None

    if not columns:
        print("Ошибка: Укажите хотя бы один столбец.")
        return None

    parsed_columns = []

    for column in columns:
        name, _, column_type = column.partition(":")
        used_names = [parsed["name"] for parsed in parsed_columns]

        if (
            not name.isidentifier()
            or column_type not in VALID_TYPES
            or name.upper() == ID_NAME
            or name in used_names
        ):
            print(INVALID_VALUE_MSG.format(column))
            return None

        parsed_columns.append({"name": name, "type": column_type})

    metadata[table_name] = [
        {"name": ID_NAME, "type": ID_TYPE},
        *parsed_columns,
    ]

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {describe_columns(metadata[table_name])}"
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу и её данные."""
    if not table_exists(metadata, table_name):
        return None

    del metadata[table_name]
    delete_table_data(table_name)

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Показывает список таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавляет запись с автоматическим ID."""
    columns = metadata[table_name][1:]

    if len(values) != len(columns):
        raise ValueError(f"Ожидалось {len(columns)} значений, получено {len(values)}.")

    record = {}

    for column, value in zip(columns, values):
        if type(value) is not VALID_TYPES[column["type"]]:
            raise ValueError(f"Столбец {column['name']} ожидает тип {column['type']}.")
        record[column["name"]] = value

    new_id = max((row[ID_NAME] for row in table_data), default=0) + 1
    table_data.append({ID_NAME: new_id, **record})

    cache_result.clear()

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает все записи или только подходящие под where_clause."""

    def get_result():
        if where_clause is None:
            return table_data
        return [row for row in table_data if matches(row, where_clause)]

    cache_key = (str(table_data), str(where_clause))
    return cache_result(cache_key, get_result)


def update(table_data, set_clause, where_clause):
    """Обновляет подходящие записи."""
    updated = [row for row in table_data if matches(row, where_clause)]

    for record in updated:
        record.update(set_clause)

    if updated:
        cache_result.clear()

    return table_data, updated


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет подходящие записи."""
    remaining = [row for row in table_data if not matches(row, where_clause)]
    deleted = [row for row in table_data if matches(row, where_clause)]

    if deleted:
        cache_result.clear()

    return remaining, deleted
