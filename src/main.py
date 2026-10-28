"""Инструмент визуализации графа зависимостей пакетов: точка входа."""

import argparse
import sys

from config import ConfigError, load_config
from file_repository import file_dependencies, load_repository
from graph import build_graph
from repository import RepositoryError, pypi_dependencies
from requirements import normalize_name

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


def dependency_source(config):
    """Имя корневого пакета и функция получения зависимостей.

    В режиме тестового репозитория зависимости берутся из файла,
    иначе — из репозитория пакетов по URL.
    """
    if config.test_repo_mode:
        packages = load_repository(config.repository)
        return config.package_name, file_dependencies(packages)
    root = normalize_name(config.package_name)
    return root, pypi_dependencies(config.repository)


def print_graph(graph):
    """Выводит граф зависимостей, найденные циклы и ошибки."""
    print("Граф зависимостей пакета {}".format(graph.root))
    print("Пакетов в графе: {}".format(len(graph.edges)))
    for name, deps in graph.edges.items():
        print("  {} -> {}".format(name, ", ".join(deps) or "(нет)"))
    if graph.cycles:
        print("Циклические зависимости:")
        for cycle in graph.cycles:
            print("  " + " -> ".join(cycle))
    else:
        print("Циклических зависимостей нет")
    if graph.errors:
        print_error("Не удалось получить зависимости пакетов:",
                    ["{}: {}".format(name, reason)
                     for name, reason in graph.errors.items()])


def main(argv=None):
    """Загружает конфигурацию, строит и выводит граф зависимостей."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print_error("Ошибка конфигурации (" + args.config + "):", err.errors)
        return EXIT_ERROR
    try:
        root, get_dependencies = dependency_source(config)
        graph = build_graph(root, get_dependencies, RepositoryError)
    except RepositoryError as err:
        print_error("Ошибка репозитория:", [str(err)])
        return EXIT_ERROR
    print_graph(graph)
    return 0


if __name__ == "__main__":
    sys.exit(main())
