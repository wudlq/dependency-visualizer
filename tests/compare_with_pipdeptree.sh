#!/bin/sh
# Сравнение ASCII-дерева программы со штатным инструментом pipdeptree.
# pip и pipdeptree используются только здесь, для сравнения: они ставятся
# во временное виртуальное окружение, которое затем удаляется.
cd "$(dirname "$0")/.."

for package in ${*:-requests flask pandas}; do
    env=$(mktemp -d)
    echo "=== $package: программа ==="
    ./run.sh --no-show "tests/configs/viz_$package.csv" | sed -n '/ASCII-дерево/,$p'
    echo "=== $package: pipdeptree ==="
    python3 -m venv "$env"
    "$env/bin/pip" install --quiet --disable-pip-version-check \
        "$package" pipdeptree
    "$env/bin/pipdeptree" --packages "$package"
    rm -rf "$env"
    echo
done
