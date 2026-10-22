#!/bin/sh
# Запуск модульных тестов (unittest из стандартной библиотеки Python).
cd "$(dirname "$0")/.."
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
