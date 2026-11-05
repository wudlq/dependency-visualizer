#!/bin/sh
# Демонстрация режима вывода порядка загрузки зависимостей.
cd "$(dirname "$0")/.."

for name in single chain simple cycle self_cycle complex complex_from_c \
            missing; do
    config="tests/configs/graph_$name.csv"
    repo=$(grep '^repository,' "$config" | cut -d, -f2)
    echo "=== $config ($(basename "$repo")) ==="
    cat "tests/repos/$(basename "$repo")"
    echo "---"
    ./run.sh --order "$config"
    echo
done
