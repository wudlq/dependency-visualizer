"""Вывод зависимостей в виде ASCII-дерева.

Дерево обходится в глубину без рекурсии, с явным стеком. Общая
зависимость показывается под каждым пакетом, которому она нужна,
как в штатных инструментах. Если пакет уже есть на пути от корня,
это цикл: он отмечается, и его зависимости повторно не выводятся.
"""

BRANCH, LAST = "├── ", "└── "
PIPE, SPACE = "│   ", "    "
CYCLE_MARK = " (цикл)"


def tree_lines(graph):
    """Строки ASCII-дерева зависимостей корневого пакета графа."""
    lines = [graph.label(graph.root)]
    stack = children(graph, graph.root, "", (graph.root,))
    while stack:
        name, prefix, last, path = stack.pop()
        line = prefix + (LAST if last else BRANCH) + graph.label(name)
        if name in path:
            lines.append(line + CYCLE_MARK)
            continue
        lines.append(line)
        inner = prefix + (SPACE if last else PIPE)
        stack.extend(children(graph, name, inner, path + (name,)))
    return lines


def children(graph, name, prefix, path):
    """Элементы стека для зависимостей name, первая — наверху стека."""
    deps = graph.edges.get(name, [])
    items = [(dep, prefix, index == len(deps) - 1, path)
             for index, dep in enumerate(deps)]
    return list(reversed(items))
