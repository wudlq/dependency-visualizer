"""Построение графа зависимостей обходом в глубину (DFS) без рекурсии.

Вместо рекурсивных вызовов используется явный стек. Каждый пакет
попадает в стек дважды: при входе (получаем и раскладываем его
зависимости) и при выходе (пакет полностью обработан). Так всегда
известен текущий путь от корня, и по нему находятся циклы.
"""

from dataclasses import dataclass, field

ENTER, EXIT = "enter", "exit"
IN_PROGRESS, DONE = "in_progress", "done"


@dataclass
class DependencyGraph:
    """Граф зависимостей пакета root.

    edges — словарь «пакет -> список прямых зависимостей» в порядке
    обхода; cycles — найденные циклы (списки пакетов, первый пакет
    повторяется в конце); errors — пакеты, для которых не удалось
    получить зависимости, и причина.
    """

    root: str
    edges: dict = field(default_factory=dict)
    cycles: list = field(default_factory=list)
    errors: dict = field(default_factory=dict)


def load_dependencies(graph, name, get_dependencies, error_type):
    """Получает зависимости name; при ошибке запоминает её в graph."""
    try:
        return get_dependencies(name)
    except error_type as err:
        if name == graph.root:
            raise
        graph.errors[name] = str(err)
        return []


def build_graph(root, get_dependencies, error_type=Exception):
    """Строит граф всех зависимостей пакета root с учётом транзитивности.

    get_dependencies(name) возвращает список прямых зависимостей пакета.
    Ошибка error_type для корня передаётся вызывающему коду, а для
    остальных пакетов запоминается в graph.errors, и обход продолжается.
    Каждый пакет запрашивается один раз, поэтому циклы не приводят
    к бесконечному обходу; сами циклы сохраняются в graph.cycles.
    """
    graph = DependencyGraph(root)
    state, path = {}, []
    stack = [(ENTER, root)]
    while stack:
        action, name = stack.pop()
        if action == EXIT:
            state[name] = DONE
            path.pop()
            continue
        if state.get(name) == IN_PROGRESS:
            graph.cycles.append(path[path.index(name):] + [name])
            continue
        if name in state:
            continue
        state[name] = IN_PROGRESS
        path.append(name)
        deps = load_dependencies(graph, name, get_dependencies, error_type)
        graph.edges[name] = list(deps)
        stack.append((EXIT, name))
        stack.extend((ENTER, dep) for dep in reversed(deps))
    return graph
