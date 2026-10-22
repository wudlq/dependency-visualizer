"""Инструмент визуализации графа зависимостей пакетов: точка входа."""

import argparse
import sys

from config import ConfigError, load_config
from repository import RepositoryError, fetch_package
from requirements import direct_dependencies

DEFAULT_CONFIG = "config.csv"
EXIT_ERROR = 1


def parse_args(argv=None):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Python")
    parser.add_argument(
        "config", nargs="?", default=DEFAULT_CONFIG,
        help="путь к конфигурационному файлу CSV "
             "(по умолчанию " + DEFAULT_CONFIG + ")")
    return parser.parse_args(argv)


def print_error(title, messages):
    """Печатает заголовок ошибки и список сообщений в stderr."""
    print(title, file=sys.stderr)
    for message in messages:
        print("  - " + message, file=sys.stderr)


def print_dependencies(package, dependencies, bad):
    """Выводит прямые зависимости пакета."""
    print("Пакет: {} {}".format(package.name, package.version))
    if not dependencies:
        print("Прямых зависимостей нет")
    else:
        print("Прямые зависимости ({}):".format(len(dependencies)))
        for requirement in dependencies:
            print("  " + str(requirement))
    if bad:
        print_error("Не удалось разобрать строки зависимостей:", bad)


def main(argv=None):
    """Загружает конфигурацию и выводит прямые зависимости пакета."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print_error("Ошибка конфигурации (" + args.config + "):", err.errors)
        return EXIT_ERROR
    if config.test_repo_mode:
        print_error("Ошибка:", ["режим тестового репозитория "
                                "пока не поддерживается"])
        return EXIT_ERROR
    try:
        package = fetch_package(config.repository, config.package_name)
    except RepositoryError as err:
        print_error("Ошибка репозитория:", [str(err)])
        return EXIT_ERROR
    dependencies, bad = direct_dependencies(package.requires_dist)
    print_dependencies(package, dependencies, bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
