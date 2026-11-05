import shlex

from prettytable import PrettyTable

from .constants import HELP_TEXT, ID_NAME, INVALID_VALUE_MSG, META_FILE, PROMPT
from .core import (
    create_table,
    delete,
    describe_columns,
    drop_table,
    insert,
    list_tables,
    select,
    table_exists,
    update,
    validate_clause,
)
from .parser import (
    invalid_command,
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def print_help():
    """Печатает справку."""
    print(HELP_TEXT)


def print_records(records, columns):
    """Печатает записи в виде таблицы PrettyTable."""
    names = [column["name"] for column in columns]
    table = PrettyTable()
    table.field_names = names

    for record in records:
        table.add_row([record.get(name) for name in names])

    print(table)


def handle_help(metadata, user_input, args):
    """Команда help."""
    print_help()


def handle_create_table(metadata, user_input, args):
    """Команда create_table."""
    if len(args) < 2:
        raise invalid_command(user_input)

    result = create_table(metadata, args[1], args[2:])

    if result is not None:
        save_metadata(META_FILE, result)


def handle_drop_table(metadata, user_input, args):
    """Команда drop_table."""
    if len(args) != 2:
        raise invalid_command(user_input)

    if not table_exists(metadata, args[1]):
        return

    result = drop_table(metadata, args[1])

    if result is not None:
        save_metadata(META_FILE, result)


def handle_list_tables(metadata, user_input, args):
    """Команда list_tables."""
    if len(args) != 1:
        raise invalid_command(user_input)

    list_tables(metadata)


def handle_insert(metadata, user_input, args):
    """Команда insert into."""
    table_name, values = parse_insert(user_input)

    if not table_exists(metadata, table_name):
        return

    result = insert(metadata, table_name, values, load_table_data(table_name))

    if result is not None:
        save_table_data(table_name, result)


def handle_select(metadata, user_input, args):
    """Команда select from"""
    table_name, where_clause = parse_select(user_input)

    if not table_exists(metadata, table_name):
        return

    columns = metadata[table_name]

    if where_clause is not None and not validate_clause(where_clause, columns):
        return

    records = select(load_table_data(table_name), where_clause)

    if records is not None:
        print_records(records, columns)


def handle_update(metadata, user_input, args):
    """Команда update"""
    table_name, set_clause, where_clause = parse_update(user_input)

    if not table_exists(metadata, table_name):
        return

    if ID_NAME in set_clause:
        print("Ошибка: Нельзя изменять ID записи.")
        return

    columns = metadata[table_name]

    if not validate_clause(set_clause, columns):
        return

    if not validate_clause(where_clause, columns):
        return

    table_data, updated = update(load_table_data(table_name), set_clause, where_clause)

    if not updated:
        print("Записи по условию не найдены.")
        return

    save_table_data(table_name, table_data)

    for record in updated:
        print(
            f'Запись с ID={record[ID_NAME]} в таблице "{table_name}" успешно обновлена.'
        )


def handle_delete(metadata, user_input, args):
    """Команда delete from"""
    table_name, where_clause = parse_delete(user_input)

    if not table_exists(metadata, table_name):
        return

    if not validate_clause(where_clause, metadata[table_name]):
        return

    result = delete(load_table_data(table_name), where_clause)

    if result is None:
        return

    table_data, deleted = result

    if not deleted:
        print("Записи по условию не найдены.")
        return

    save_table_data(table_name, table_data)

    for record in deleted:
        print(
            f'Запись с ID={record[ID_NAME]} успешно удалена из таблицы "{table_name}".'
        )


def handle_info(metadata, user_input, args):
    """Команда info"""
    if len(args) != 2:
        raise invalid_command(user_input)

    table_name = args[1]

    if not table_exists(metadata, table_name):
        return

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {describe_columns(metadata[table_name])}")
    print(f"Количество записей: {len(load_table_data(table_name))}")


COMMANDS = {
    "help": handle_help,
    "create_table": handle_create_table,
    "drop_table": handle_drop_table,
    "list_tables": handle_list_tables,
    "insert": handle_insert,
    "select": handle_select,
    "update": handle_update,
    "delete": handle_delete,
    "info": handle_info,
}


def run():
    """Главный цикл"""
    print_help()

    while True:
        try:
            user_input = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(INVALID_VALUE_MSG.format(user_input))
            continue

        command = args[0].lower()

        if command == "exit":
            print("Выход из программы.")
            break

        handler = COMMANDS.get(command)

        if handler is None:
            print(f"Функции {args[0]} нет. Попробуйте снова.")
            continue

        try:
            handler(load_metadata(META_FILE), user_input, args)
        except ValueError as error:
            print(error)
