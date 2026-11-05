#!/bin/sh
# Сравнение порядка загрузки с реальным менеджером пакетов pip.
# pip используется только здесь, для сравнения: пакеты ставятся
# во временную папку и сразу удаляются, сама программа pip не вызывает.
cd "$(dirname "$0")/.."

for package in ${*:-requests flask}; do
    config=$(mktemp)
    target=$(mktemp -d)
    printf 'parameter,value\npackage_name,%s\n' "$package" > "$config"
    printf 'repository,https://pypi.org/pypi\n' >> "$config"
    printf 'test_repo_mode,false\nascii_tree,false\n' >> "$config"
    echo "=== $package: программа ==="
    ./run.sh --order "$config"
    echo "=== $package: pip ==="
    python3 -m pip install --no-cache-dir --ignore-installed \
        --disable-pip-version-check --target "$target" "$package" \
        | grep "Installing collected packages"
    rm -rf "$config" "$target"
    echo
done
