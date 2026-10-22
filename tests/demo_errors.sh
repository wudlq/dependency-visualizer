#!/bin/sh
# Демонстрация работы с конфигурацией: верные файлы и все виды ошибок.
cd "$(dirname "$0")/.."

for config in tests/configs/valid_*.csv tests/configs/nope.csv \
              tests/configs/empty.csv tests/configs/bad_*.csv \
              tests/configs/missing_*.csv tests/configs/unknown_param.csv \
              tests/configs/duplicate_param.csv \
              tests/configs/empty_*.csv tests/configs/many_errors.csv; do
    echo "=== $config ==="
    ./run.sh "$config"
    echo "(код завершения: $?)"
    echo
done
