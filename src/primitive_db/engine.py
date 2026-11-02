import shlex

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит справку по командам."""

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
            print(
                f"Функции {command} нет. "
                "Попробуйте снова."
            )