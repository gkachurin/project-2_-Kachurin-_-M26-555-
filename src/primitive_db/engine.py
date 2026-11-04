import re
import shlex

from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_condition,
    parse_insert_values,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> .. - создать таблицу"
    )
    print(
        "<command> list_tables - показать список всех таблиц"
    )
    print(
        "<command> drop_table <имя_таблицы> - удалить таблицу"
    )

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

    print("\n***Операции с данными***")

    print(
        "insert into <имя_таблицы> "
        "values (<значение1>, <значение2>, ...) "
        "- создать запись."
    )

    print(
        "select from <имя_таблицы> "
        "- прочитать все записи."
    )

    print(
        "select from <имя_таблицы> "
        "where <столбец> = <значение> "
        "- прочитать записи по условию."
    )

    print(
        "update <имя_таблицы> "
        "set <столбец> = <новое_значение> "
        "where <столбец> = <значение> "
        "- обновить запись."
    )

    print(
        "delete from <имя_таблицы> "
        "where <столбец> = <значение> "
        "- удалить запись."
    )

    print(
        "info <имя_таблицы> "
        "- вывести информацию о таблице."
    )


def run():
    print_help()

    while True:
        user_input = input(">>>Введите команду: ").strip()

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(
                f"Некорректное значение: {user_input}. "
                "Попробуйте снова."
            )
            continue

        command = args[0].lower()

        if command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            if len(args) < 2:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
                continue

            table_name = args[1]
            columns = args[2:]

            metadata = load_metadata(METADATA_FILE)
            old_metadata = metadata.copy()

            metadata = create_table(
                metadata,
                table_name,
                columns,
            )

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
                continue

            table_name = args[1]

            metadata = load_metadata(METADATA_FILE)
            old_metadata = metadata.copy()

            metadata = drop_table(metadata, table_name)

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)

        elif command == "list_tables":
            if len(args) != 1:
                print(
                    f"Некорректное значение: {user_input}. "
                    "Попробуйте снова."
                )
                continue

            metadata = load_metadata(METADATA_FILE)
            list_tables(metadata)

        else:
            metadata = load_metadata("db_meta.json")

            try:
                handle_data_command(
                user_input,
                metadata,
            )
            except ValueError as error:
                print(f"Ошибка: {error}")


def print_records(records, columns):
    table = PrettyTable()
    table.field_names = [
        column["name"]
        for column in columns
    ]
    for record in records:
        table.add_row([
            record.get(column["name"])
            for column in columns
        ])
    print(table)

def handle_data_command(command, metadata):
    insert_match = re.match(
        r"^insert\s+into\s+(\w+)\s+values\s*\(.*\)\s*$",
        command,
        re.IGNORECASE,
    )

    if insert_match:
        table_name = insert_match.group(1)

        if table_name not in metadata:
            raise ValueError(
                f'Таблица "{table_name}" не существует.'
            )

        values = parse_insert_values(command)
        table_data = load_table_data(table_name)

        table_data = insert(
            metadata,
            table_name,
            values,
            table_data,
        )

        save_table_data(table_name, table_data)
        return

    select_match = re.match(
        r"^select\s+from\s+(\w+)"
        r"(?:\s+where\s+(.+))?$",
        command,
        re.IGNORECASE,
    )

    if select_match:
        table_name = select_match.group(1)
        condition = select_match.group(2)

        if table_name not in metadata:
            raise ValueError(
                f'Таблица "{table_name}" не существует.'
            )

        table_data = load_table_data(table_name)

        where_clause = (
            parse_condition(condition)
            if condition
            else None
        )

        if where_clause:
            validate_clause(
                where_clause,
                metadata[table_name],
            )

        records = select(
            table_data,
            where_clause,
        )

        print_records(
            records,
            metadata[table_name],
        )

        return

    update_match = re.match(
        r"^update\s+(\w+)\s+set\s+(.+?)"
        r"\s+where\s+(.+)$",
        command,
        re.IGNORECASE,
    )

    if update_match:
        table_name = update_match.group(1)
        set_condition = update_match.group(2)
        where_condition = update_match.group(3)

        if table_name not in metadata:
            raise ValueError(
                f'Таблица "{table_name}" не существует.'
            )

        set_clause = parse_condition(set_condition)
        where_clause = parse_condition(where_condition)

        validate_clause(
            set_clause,
            metadata[table_name],
            )

        validate_clause(
            where_clause,
            metadata[table_name],
        )

        if "ID" in set_clause:
            raise ValueError("Нельзя изменять ID записи.")

        table_data = load_table_data(table_name)

        table_data, updated_records = update(
            table_data,
            set_clause,
            where_clause,
        )

        if updated_records:
            save_table_data(table_name, table_data)

            for record in updated_records:
                print(
                    f'Запись с ID={record["ID"]} '
                    f'в таблице "{table_name}" '
                    "успешно обновлена."
                )
        else:
            print("Записи по условию не найдены.")

        return

    delete_match = re.match(
        r"^delete\s+from\s+(\w+)\s+where\s+(.+)$",
        command,
        re.IGNORECASE,
    )

    if delete_match:
        table_name = delete_match.group(1)
        condition = delete_match.group(2)

        if table_name not in metadata:
            raise ValueError(
                f'Таблица "{table_name}" не существует.'
            )

        where_clause = parse_condition(condition)

        validate_clause(
            where_clause,
            metadata[table_name],
        )
        table_data = load_table_data(table_name)

        table_data, deleted_records = delete(
            table_data,
            where_clause,
        )

        if deleted_records:
            save_table_data(table_name, table_data)

            for record in deleted_records:
                print(
                    f'Запись с ID={record["ID"]} '
                    "успешно удалена."
                )
        else:
            print("Записи по условию не найдены.")

        return

    info_match = re.match(
        r"^info\s+(\w+)$",
        command,
        re.IGNORECASE,
    )

    if info_match:
        table_name = info_match.group(1)

        if table_name not in metadata:
            raise ValueError(
                f'Таблица "{table_name}" не существует.'
            )

        columns = metadata[table_name]
        table_data = load_table_data(table_name)

        columns_description = ", ".join(
            f'{column["name"]}:{column["type"]}'
            for column in columns
        )

        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns_description}")
        print(f"Количество записей: {len(table_data)}")

        return

    raise ValueError(
        f"Неизвестная команда: {command}"
    )


def validate_clause(clause, columns):
    column_names = {
        column["name"]
        for column in columns
    }

    for column_name in clause:
        if column_name not in column_names:
            raise ValueError(
                f'Столбец "{column_name}" не существует.'
            )
