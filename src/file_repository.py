"""Тестовый репозиторий: граф пакетов, описанный в текстовом файле.

Каждая непустая строка описывает один пакет и его прямые зависимости:
    A: B C
    B: D
    D:
Имена пакетов — большие латинские буквы (A, B, ..., Z, AB и т.д.).
Пакет без зависимостей записывается с пустой правой частью.
"""

import re

from repository import RepositoryError

PACKAGE_NAME = re.compile(r"^[A-Z]+$")


def check_name(name, number):
    """Проверяет имя пакета из строки number файла."""
    if not PACKAGE_NAME.match(name):
        raise RepositoryError("строка {}: имя пакета «{}» должно состоять "
                              "из больших латинских букв"
                              .format(number, name))


def parse_line(line, number):
    """Разбирает строку «ПАКЕТ: ЗАВИСИМОСТИ» в пару (имя, список)."""
    name, colon, rest = line.partition(":")
    if not colon:
        raise RepositoryError("строка {}: ожидается «ПАКЕТ: ЗАВИСИМОСТИ», "
                              "получено «{}»".format(number, line))
    name, deps = name.strip(), rest.split()
    for item in [name] + deps:
        check_name(item, number)
    return name, deps


def parse_repository(text):
    """Разбирает текст файла в словарь «пакет -> список зависимостей»."""
    packages = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        name, deps = parse_line(line, number)
        if name in packages:
            raise RepositoryError("строка {}: пакет {} описан повторно"
                                  .format(number, name))
        packages[name] = deps
    return packages


def load_repository(path):
    """Читает файл тестового репозитория."""
    try:
        with open(path, encoding="utf-8") as file:
            return parse_repository(file.read())
    except OSError as err:
        raise RepositoryError("не удалось прочитать файл тестового "
                              "репозитория: {}".format(err)) from None


def file_dependencies(packages):
    """Функция «пакет -> прямые зависимости» для тестового репозитория."""
    def get_dependencies(name):
        """Прямые зависимости пакета name из тестового репозитория."""
        if name not in packages:
            raise RepositoryError("пакет {} не найден в тестовом "
                                  "репозитории".format(name))
        return packages[name]
    return get_dependencies
