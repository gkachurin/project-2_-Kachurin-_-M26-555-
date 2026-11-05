from .constants import INVALID_VALUE_MSG, QUOTES, WHERE_SEPARATOR


def invalid_command(text):
    """Создаёт ошибку «Некорректное значение»."""
    return ValueError(INVALID_VALUE_MSG.format(text))


def has_keywords(words, expected):
    """Проверяет, что на позициях стоят нужные слова."""
    return all(
        index < len(words) and words[index].lower() == keyword
        for index, keyword in expected.items()
    )


def parse_value(token):
    """Превращает токен в str, bool или int."""
    token = token.strip()

    if len(token) >= 2 and token[0] == token[-1] and token[0] in QUOTES:
        return token[1:-1]

    if token.lower() in ("true", "false"):
        return token.lower() == "true"

    try:
        return int(token)
    except ValueError:
        raise invalid_command(token) from None


def parse_condition(text):
    """Разбирает 'age = 28' в {'age': 28}."""
    column, separator, value = text.partition("=")
    column = column.strip()

    if not separator or not column.isidentifier():
        raise invalid_command(text.strip())

    return {column: parse_value(value)}


def split_values(values_string):
    """Делит строку значений по запятым вне кавычек и разбирает их."""
    tokens = []
    current = ""
    quote = None

    for char in values_string:
        if char in QUOTES:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

        if char == "," and quote is None:
            tokens.append(current)
            current = ""
        else:
            current += char

    if quote is not None:
        raise invalid_command(values_string.strip())

    if current.strip() or tokens:
        tokens.append(current)

    return [parse_value(token) for token in tokens]


def split_where(text):
    """Делит 'a where b' на ('a', 'b'); если where нет, возвращает None."""
    index = text.lower().find(WHERE_SEPARATOR)

    if index == -1:
        return None

    return text[:index], text[index + len(WHERE_SEPARATOR) :]


def parse_insert(user_input):
    """Разбирает insert into <таблица> values (...)."""
    head, separator, tail = user_input.partition("(")

    words = head.split()
    tail = tail.rstrip()

    if (
        len(words) != 4
        or not has_keywords(words, {0: "insert", 1: "into", 3: "values"})
        or not separator
        or not tail.endswith(")")
    ):
        raise invalid_command(user_input)

    return words[2], split_values(tail[:-1])


def parse_select(user_input):
    """Разбирает select from <таблица> [where <условие>]."""
    words = user_input.split(None, 3)

    if len(words) < 3 or not has_keywords(words, {0: "select", 1: "from"}):
        raise invalid_command(user_input)

    if len(words) == 3:
        return words[2], None

    keyword, _, condition = words[3].partition(" ")

    if keyword.lower() != "where":
        raise invalid_command(user_input)

    return words[2], parse_condition(condition)


def parse_update(user_input):
    """Разбирает update <таблица> set <поле> = <знач> where <поле> = <знач>."""
    words = user_input.split(None, 3)

    if len(words) != 4 or not has_keywords(words, {0: "update", 2: "set"}):
        raise invalid_command(user_input)

    parts = split_where(words[3])

    if parts is None:
        raise invalid_command(user_input)

    set_text, where_text = parts
    return words[1], parse_condition(set_text), parse_condition(where_text)


def parse_delete(user_input):
    """Разбирает delete from <таблица> where <условие>."""
    words = user_input.split(None, 4)

    if len(words) != 5 or not has_keywords(words, {0: "delete", 1: "from", 3: "where"}):
        raise invalid_command(user_input)

    return words[2], parse_condition(words[4])
