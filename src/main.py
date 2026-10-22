"""Инструмент визуализации графа зависимостей пакетов: точка входа."""

import argparse
import sys

from config import ConfigError, load_config

DEFAULT_CONFIG = "config.csv"
EXIT_CONFIG_ERROR = 1


def parse_args(argv=None):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей пакетов Python")
    parser.add_argument(
        "config", nargs="?", default=DEFAULT_CONFIG,
        help="путь к конфигурационному файлу CSV "
             "(по умолчанию " + DEFAULT_CONFIG + ")")
    return parser.parse_args(argv)


def print_config(config):
    """Выводит все параметры в формате «ключ = значение»."""
    for name, value in config.items():
        if isinstance(value, bool):
            value = str(value).lower()
        print("{} = {}".format(name, value))


def main(argv=None):
    """Загружает конфигурацию и выводит её параметры."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print("Ошибка конфигурации (" + args.config + "):", file=sys.stderr)
        for message in err.errors:
            print("  - " + message, file=sys.stderr)
        return EXIT_CONFIG_ERROR
    print_config(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
