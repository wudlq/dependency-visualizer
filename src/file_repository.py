"""Тестовый репозиторий: граф пакетов, описанный в текстовом файле.

Каждая непустая строка описывает один пакет, его версию (необязательно)
и прямые зависимости:
    A 2.1.0: B C
    B 1.4: D
    D 0.9:
Имена пакетов — большие латинские буквы (A, B, ..., Z, AB и т.д.),
версия — числа через точку. Пакет без зависимостей записывается
с пустой правой частью.
"""

import re

from repository import RepositoryError

PACKAGE_NAME = re.compile(r"^[A-Z]+$")
VERSION = re.compile(r"^\d+(\.\d+)*$")
NAME_AND_VERSION = 2


def check_name(name, number):
    """Проверяет имя пакета из строки number файла."""
    if not PACKAGE_NAME.match(name):
        raise RepositoryError("строка {}: имя пакета «{}» должно состоять "
                              "из больших латинских букв"
                              .format(number, name))


def parse_package(text, number):
    """Разбирает левую часть строки: «ИМЯ» или «ИМЯ ВЕРСИЯ»."""
    parts = text.split()
    if not parts or len(parts) > NAME_AND_VERSION:
        raise RepositoryError("строка {}: слева от двоеточия ожидается "
                              "«ПАКЕТ» или «ПАКЕТ ВЕРСИЯ»".format(number))
    check_name(parts[0], number)
    version = parts[1] if len(parts) == NAME_AND_VERSION else ""
    if version and not VERSION.match(version):
        raise RepositoryError("строка {}: неверная версия «{}», ожидаются "
                              "числа через точку".format(number, version))
    return parts[0], version


def parse_line(line, number):
    """Разбирает строку «ПАКЕТ [ВЕРСИЯ]: ЗАВИСИМОСТИ».

    Возвращает имя, версию (пустая строка, если не указана) и список
    зависимостей.
    """
    package, colon, rest = line.partition(":")
    if not colon:
        raise RepositoryError("строка {}: ожидается «ПАКЕТ: ЗАВИСИМОСТИ», "
                              "получено «{}»".format(number, line))
    name, version = parse_package(package, number)
    deps = rest.split()
    for dep in deps:
        check_name(dep, number)
    return name, version, deps


def parse_repository(text):
    """Разбирает текст файла.

    Возвращает словарь «пакет -> список зависимостей» и словарь
    «пакет -> версия» для пакетов, у которых версия указана.
    """
    packages, versions = {}, {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        name, version, deps = parse_line(line, number)
        if name in packages:
            raise RepositoryError("строка {}: пакет {} описан повторно"
                                  .format(number, name))
        packages[name] = deps
        if version:
            versions[name] = version
    return packages, versions


def load_repository(path):
    """Читает файл тестового репозитория (см. parse_repository)."""
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
