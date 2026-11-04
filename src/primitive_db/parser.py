
import ast
import re


def parse_value(value):
    value = value.strip()

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ('"', "'")
    ):
        result = ast.literal_eval(value)

        if type(result) is not str:
            raise ValueError("Ожидалась строка.")

        return result

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Некорректное значение: {value}. "
            "Строки нужно передавать в кавычках."
        )


def parse_condition(condition):
    pattern = r"^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s*$"

    match = re.match(pattern, condition)

    if not match:
        raise ValueError(
            f"Некорректное условие: {condition}"
        )

    column_name = match.group(1)
    value = parse_value(match.group(2))

    return {column_name: value}


def split_values(values_string):
    values = []
    current = ""
    quote = None

    for char in values_string:
        if char in ('"', "'"):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

        if char == "," and quote is None:
            values.append(current.strip())
            current = ""
        else:
            current += char

    if quote is not None:
        raise ValueError("Не закрыты кавычки.")

    if current.strip():
        values.append(current.strip())

    return [parse_value(value) for value in values]


def parse_insert_values(command):
    pattern = (
        r"^insert\s+into\s+\S+\s+values\s*"
        r"\((.*)\)\s*$"
    )

    match = re.match(pattern, command, re.IGNORECASE)

    if not match:
        raise ValueError(
            "Некорректная команда insert."
        )

    values_string = match.group(1)

    return split_values(values_string)
