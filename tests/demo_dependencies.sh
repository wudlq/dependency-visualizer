#!/bin/sh
# Демонстрация получения прямых зависимостей пакетов из PyPI.
cd "$(dirname "$0")/.."

for config in config.csv tests/configs/valid_url.csv \
              tests/configs/pypi_pandas.csv tests/configs/pypi_six.csv \
              tests/configs/pypi_not_found.csv \
              tests/configs/pypi_unreachable.csv; do
    echo "=== $config ==="
    ./run.sh "$config"
    echo "(код завершения: $?)"
    echo
done
