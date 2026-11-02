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