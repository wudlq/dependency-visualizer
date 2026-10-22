"""Чтение и проверка конфигурационного файла в формате CSV.

Файл состоит из строки заголовка «parameter,value» и строк вида
«имя_параметра,значение». Все четыре параметра обязательны.
"""

import csv
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

HEADER = ["parameter", "value"]
ROW_SIZE = len(HEADER)
PACKAGE = "package_name"
REPOSITORY = "repository"
TEST_MODE = "test_repo_mode"
ASCII_TREE = "ascii_tree"
PARAMETERS = [PACKAGE, REPOSITORY, TEST_MODE, ASCII_TREE]
TRUE_VALUES = ("true", "yes", "1")
FALSE_VALUES = ("false", "no", "0")
URL_SCHEMES = ("http", "https")
PACKAGE_NAME = re.compile(
    r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE)


class ConfigError(Exception):
    """Ошибка конфигурации; errors — список сообщений обо всех ошибках."""

    def __init__(self, errors):
        """Сохраняет список сообщений об ошибках."""
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass
class Config:
    """Параметры, настраиваемые пользователем."""

    package_name: str
    repository: str
    test_repo_mode: bool
    ascii_tree: bool

    def items(self):
        """Пары «ключ — значение» в порядке описания параметров."""
        return [(name, getattr(self, name)) for name in PARAMETERS]


def read_rows(path):
    """Читает CSV-файл и возвращает строки без заголовка.

    Пустые строки пропускаются. Ошибки чтения файла, неверный
    заголовок и строки с неверным числом столбцов дают ConfigError.
    """
    try:
        with open(path, encoding="utf-8", newline="") as file:
            rows = [row for row in csv.reader(file) if row]
    except FileNotFoundError:
        raise ConfigError(["файл конфигурации не найден: " + path]) from None
    except (OSError, UnicodeDecodeError, csv.Error) as err:
        raise ConfigError(["не удалось прочитать файл: " + str(err)]) from None
    if not rows:
        raise ConfigError(["файл конфигурации пуст"])
    if [cell.strip() for cell in rows[0]] != HEADER:
        raise ConfigError(["первая строка должна быть «parameter,value»"])
    for number, row in enumerate(rows[1:], start=2):
        if len(row) != ROW_SIZE:
            raise ConfigError(["строка {}: ожидается 2 столбца, получено {}"
                               .format(number, len(row))])
    return rows[1:]


def collect_values(rows):
    """Собирает словарь «параметр — значение», проверяя имена.

    Неизвестные, повторяющиеся и отсутствующие параметры считаются
    ошибками и возвращаются вторым элементом результата.
    """
    values, errors = {}, []
    for name, value in rows:
        name = name.strip()
        if name not in PARAMETERS:
            errors.append("неизвестный параметр «{}»".format(name))
        elif name in values:
            errors.append("параметр {} указан повторно".format(name))
        else:
            values[name] = value.strip()
    for name in PARAMETERS:
        if name not in values:
            errors.append("не задан параметр " + name)
    return values, errors


def parse_bool(name, text):
    """Переводит true/false (также yes/no, 1/0) в bool."""
    if text.lower() in TRUE_VALUES:
        return True
    if text.lower() in FALSE_VALUES:
        return False
    raise ValueError("{}: ожидается true или false, получено «{}»"
                     .format(name, text))


def check_package(text):
    """Проверяет имя пакета по правилам имён пакетов Python (PEP 508)."""
    if not text:
        raise ValueError(PACKAGE + ": имя пакета не может быть пустым")
    if not PACKAGE_NAME.match(text):
        raise ValueError(PACKAGE + ": недопустимое имя пакета «{}»"
                         .format(text))
    return text


def check_repository(text, test_mode, base_dir=""):
    """Проверяет URL репозитория или путь к файлу тестового репозитория.

    В обычном режиме нужен URL со схемой http или https и адресом
    сервера. В режиме тестового репозитория нужен путь к файлу;
    относительный путь отсчитывается от папки с файлом конфигурации.
    """
    if not text:
        raise ValueError(REPOSITORY + ": значение не может быть пустым")
    if test_mode:
        path = os.path.join(base_dir, text)
        if not os.path.isfile(path):
            raise ValueError(REPOSITORY + ": файл тестового репозитория "
                             "не найден: " + text)
        return os.path.normpath(path)
    url = urlparse(text)
    if url.scheme not in URL_SCHEMES or not url.netloc:
        raise ValueError(REPOSITORY + ": ожидается URL вида "
                         "https://сервер/путь, получено «{}»".format(text))
    return text


def build_config(values, base_dir=""):
    """Проверяет значения всех заданных параметров.

    Возвращает словарь проверенных значений и список ошибок. Адрес
    репозитория проверяется, только если режим работы задан верно,
    так как от режима зависит, URL это или путь к файлу.
    """
    result, errors = {}, []
    for name in (TEST_MODE, ASCII_TREE, PACKAGE, REPOSITORY):
        if name not in values:
            continue
        try:
            if name == PACKAGE:
                result[name] = check_package(values[name])
            elif name == REPOSITORY:
                if TEST_MODE in result:
                    result[name] = check_repository(
                        values[name], result[TEST_MODE], base_dir)
            else:
                result[name] = parse_bool(name, values[name])
        except ValueError as err:
            errors.append(str(err))
    return result, errors


def load_config(path):
    """Загружает конфигурацию из CSV-файла.

    Возвращает Config или выбрасывает ConfigError со списком всех
    найденных ошибок.
    """
    values, errors = collect_values(read_rows(path))
    result, value_errors = build_config(values, os.path.dirname(path))
    errors += value_errors
    if errors:
        raise ConfigError(errors)
    return Config(**result)
