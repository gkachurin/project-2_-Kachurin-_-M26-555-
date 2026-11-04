ALLOWED_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not table_name:
        print("Некорректное значение: имя таблицы. Попробуйте снова.")
        return metadata

    parsed_columns = []
    column_names = set()

    for column in columns:
        if ":" not in column:
            print(
                f"Некорректное значение: {column}. "
                "Попробуйте снова."
            )
            return metadata

        column_name, column_type = column.split(":", 1)

        if not column_name or column_type not in ALLOWED_TYPES:
            print(
                f"Некорректное значение: {column}. "
                "Попробуйте снова."
            )
            return metadata

        if column_name.upper() == "ID":
            print(
                f"Некорректное значение: {column}. "
                "Столбец ID создаётся автоматически."
            )
            return metadata

        if column_name in column_names:
            print(
                f"Некорректное значение: {column_name}. "
                "Попробуйте снова."
            )
            return metadata

        column_names.add(column_name)

        parsed_columns.append({
            "name": column_name,
            "type": column_type,
        })

    metadata[table_name] = [
        {"name": "ID", "type": "int"},
        *parsed_columns,
    ]

    columns_description = ", ".join(
        f"{column['name']}:{column['type']}"
        for column in metadata[table_name]
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {columns_description}"
    )

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata):
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def insert(metadata, table_name, values, table_data):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]
    user_columns = columns[1:]

    if len(values) != len(user_columns):
        raise ValueError(
            f"Ожидалось {len(user_columns)} значений, "
            f"получено {len(values)}."
        )

    record = {}

    for column, value in zip(user_columns, values):
        column_name = column["name"]
        column_type = column["type"]

        if column_type == "int" and type(value) is not int:
            raise ValueError(
                f"Столбец {column_name} ожидает тип int."
            )

        if column_type == "str" and type(value) is not str:
            raise ValueError(
                f"Столбец {column_name} ожидает тип str."
            )

        if column_type == "bool" and type(value) is not bool:
            raise ValueError(
                f"Столбец {column_name} ожидает тип bool."
            )

        record[column_name] = value

    max_id = max(
        (row["ID"] for row in table_data),
        default=0
    )
    
    new_id = max_id + 1

    record = {"ID": new_id, **record}

    table_data.append(record)

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )

    return table_data


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    result = []

    for record in table_data:
        matches = all(
            record.get(column) == value
            for column, value in where_clause.items()
        )

        if matches:
            result.append(record)

    return result


def update(table_data, set_clause, where_clause):
    updated_records = []

    for record in table_data:
        matches = all(
            record.get(column) == value
            for column, value in where_clause.items()
        )

        if matches:
            record.update(set_clause)
            updated_records.append(record)

    return table_data, updated_records


def delete(table_data, where_clause):
    remaining_records = []
    deleted_records = []

    for record in table_data:
        matches = all(
            record.get(column) == value
            for column, value in where_clause.items()
        )

        if matches:
            deleted_records.append(record)
        else:
            remaining_records.append(record)

    return remaining_records, deleted_records
