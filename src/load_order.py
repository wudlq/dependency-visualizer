"""Порядок загрузки (установки) зависимостей пакета.

Пакет можно загрузить только после всех его зависимостей, поэтому
порядок загрузки — это топологическая сортировка графа: пакеты
выписываются в момент выхода из них при обходе в глубину (DFS),
то есть после всех их зависимостей. Обход выполняется без рекурсии,
с явным стеком.
"""

ENTER, EXIT = "enter", "exit"


def load_order(graph):
    """Список пакетов графа в порядке загрузки, корневой пакет последний.

    Зависимости пакета загружаются раньше него. Если пакеты образуют
    цикл, строгого порядка для них нет: цикл разрывается в месте, где
    обход вернулся к пакету, который ещё обрабатывается.
    """
    order, seen = [], set()
    stack = [(ENTER, graph.root)]
    while stack:
        action, name = stack.pop()
        if action == EXIT:
            order.append(name)
            continue
        if name in seen:
            continue
        seen.add(name)
        stack.append((EXIT, name))
        deps = graph.edges.get(name, [])
        stack.extend((ENTER, dep) for dep in reversed(deps))
    return order


def broken_dependencies(graph, order):
    """Пары (пакет, зависимость), где зависимость загружается позже.

    Такие пары возможны только в циклах: там пакет неизбежно
    загружается раньше одной из своих зависимостей.
    """
    position = {name: index for index, name in enumerate(order)}
    return [(name, dep) for name in order
            for dep in graph.edges.get(name, [])
            if position[dep] > position[name]]
