import time


def handle_db_errors(func):
    """Перехватывает типичные ошибки БД."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name):
    """Просит подтверждения."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            question = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            if input(question).strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Показывает время выполнения функции."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return wrapper


def create_cacher():
    """Возвращает cache_result(key, value_func) с кэшем в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear():
        cache.clear()

    cache_result.clear = clear

    return cache_result
