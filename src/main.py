"""Инструмент визуализации графа зависимостей пакетов: точка входа."""

import argparse
import sys

from ascii_tree import tree_lines
from config import ConfigError, load_config
from diagram import RenderError, render, save_d2, show
from file_repository import file_dependencies, load_repository
from graph import build_graph
from repository import RepositoryError, pypi_dependencies
from requirements import normalize_name

DEFAULT_CONFIG = "config.csv"
OUTPUT_FOLDER = "output"
EXIT_ERROR = 1


def parse_args(argv=None):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Python")
    parser.add_argument(
        "config", nargs="?", default=DEFAULT_CONFIG,
        help="путь к конфигурационному файлу CSV "
             "(по умолчанию " + DEFAULT_CONFIG + ")")
    parser.add_argument(
        "--no-show", action="store_true",
        help="только сохранить изображение графа, не открывать его")
    return parser.parse_args(argv)


def print_error(title, messages):
    """Печатает заголовок ошибки и список сообщений в stderr."""
    print(title, file=sys.stderr)
    for message in messages:
        print("  - " + message, file=sys.stderr)


def dependency_source(config, versions):
    """Имя корневого пакета и функция получения зависимостей.

    В режиме тестового репозитория зависимости и версии берутся
    из файла, иначе — из репозитория пакетов по URL.
    """
    if config.test_repo_mode:
        packages, file_versions = load_repository(config.repository)
        versions.update(file_versions)
        return config.package_name, file_dependencies(packages)
    root = normalize_name(config.package_name)
    return root, pypi_dependencies(config.repository, versions)


def print_graph(graph):
    """Выводит граф зависимостей и найденные циклы."""
    print("Граф зависимостей пакета {}".format(graph.label(graph.root)))
    print("Пакетов в графе: {}".format(len(graph.edges)))
    for name, deps in graph.edges.items():
        print("  {} -> {}".format(graph.label(name),
                                  ", ".join(deps) or "(нет)"))
    if graph.cycles:
        print("Циклические зависимости:")
        for cycle in graph.cycles:
            print("  " + " -> ".join(cycle))
    else:
        print("Циклических зависимостей нет")


def print_errors(graph):
    """Выводит пакеты, зависимости которых получить не удалось."""
    if graph.errors:
        print_error("Не удалось получить зависимости пакетов:",
                    ["{}: {}".format(name, reason)
                     for name, reason in graph.errors.items()])


def visualize(graph, open_image=True):
    """Сохраняет граф на D2, делает изображение и показывает его.

    Возвращает False, если изображение получить не удалось.
    """
    d2_path = save_d2(graph, OUTPUT_FOLDER)
    print("Описание графа на D2: " + d2_path)
    try:
        image = render(d2_path)
        print("Изображение графа: " + image)
        if open_image:
            show(image)
    except RenderError as err:
        print_error("Ошибка визуализации:", [str(err)])
        return False
    return True


def main(argv=None):
    """Строит граф зависимостей и выводит его изображение и дерево."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print_error("Ошибка конфигурации (" + args.config + "):", err.errors)
        return EXIT_ERROR
    versions = {}
    try:
        root, get_dependencies = dependency_source(config, versions)
        graph = build_graph(root, get_dependencies, RepositoryError)
    except RepositoryError as err:
        print_error("Ошибка репозитория:", [str(err)])
        return EXIT_ERROR
    graph.versions = versions
    print_graph(graph)
    print_errors(graph)
    shown = visualize(graph, not args.no_show)
    if config.ascii_tree:
        print("ASCII-дерево зависимостей:")
        print("\n".join(tree_lines(graph)))
    return 0 if shown else EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
