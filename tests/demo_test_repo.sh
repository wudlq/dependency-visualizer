#!/bin/sh
# Демонстрация графа зависимостей на тестовых репозиториях.
cd "$(dirname "$0")/.."

for name in single chain simple cycle self_cycle complex complex_from_c \
            missing unknown_root bad_format bad_name duplicate; do
    config="tests/configs/graph_$name.csv"
    repo=$(grep '^repository,' "$config" | cut -d, -f2)
    echo "=== $config ($(basename "$repo")) ==="
    ./run.sh "$config"
    echo "(код завершения: $?)"
    echo
done
