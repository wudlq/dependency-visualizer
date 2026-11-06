#!/bin/sh
# Визуализация зависимостей трёх реальных пакетов и тестового графа:
# описание на D2, изображение (открывается) и ASCII-дерево.
cd "$(dirname "$0")/.."

for config in tests/configs/viz_requests.csv tests/configs/viz_flask.csv \
              tests/configs/viz_pandas.csv \
              tests/configs/viz_test_complex.csv; do
    echo "=== $config ==="
    ./run.sh "$config"
    echo
done
