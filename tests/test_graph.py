"""Тесты построения графа зависимостей (DFS без рекурсии)."""

import unittest

from graph import build_graph


def lookup(packages):
    """Функция получения зависимостей из словаря packages."""
    def get_dependencies(name):
        """Зависимости name; KeyError, если пакета нет."""
        return packages[name]
    return get_dependencies


class BuildGraphTest(unittest.TestCase):
    """Проверка build_graph на разных формах графа."""

    def test_single(self):
        """Пакет без зависимостей."""
        graph = build_graph("A", lookup({"A": []}))
        self.assertEqual(graph.edges, {"A": []})
        self.assertEqual(graph.cycles, [])

    def test_transitive(self):
        """Учитываются зависимости зависимостей."""
        graph = build_graph("A", lookup({"A": ["B"], "B": ["C"], "C": []}))
        self.assertEqual(list(graph.edges), ["A", "B", "C"])

    def test_dfs_order(self):
        """Обход в глубину: сначала вся ветка B, потом C."""
        packages = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
        graph = build_graph("A", lookup(packages))
        self.assertEqual(list(graph.edges), ["A", "B", "D", "C"])

    def test_shared_dependency(self):
        """Общая зависимость запрашивается один раз и не считается циклом."""
        calls = []
        packages = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}

        def get_dependencies(name):
            """Запоминает, какие пакеты запрашивались."""
            calls.append(name)
            return packages[name]
        graph = build_graph("A", get_dependencies)
        self.assertEqual(sorted(calls), ["A", "B", "C", "D"])
        self.assertEqual(graph.cycles, [])

    def test_cycle(self):
        """Цикл A -> B -> C -> A найден, обход завершается."""
        packages = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph = build_graph("A", lookup(packages))
        self.assertEqual(graph.cycles, [["A", "B", "C", "A"]])
        self.assertEqual(len(graph.edges), 3)

    def test_self_cycle(self):
        """Пакет зависит сам от себя."""
        graph = build_graph("A", lookup({"A": ["A"]}))
        self.assertEqual(graph.cycles, [["A", "A"]])

    def test_several_cycles(self):
        """Несколько циклов в одном графе."""
        packages = {"A": ["B", "C"], "B": ["A"], "C": ["D"], "D": ["C"]}
        graph = build_graph("A", lookup(packages))
        self.assertIn(["A", "B", "A"], graph.cycles)
        self.assertIn(["C", "D", "C"], graph.cycles)

    def test_missing_dependency(self):
        """Ошибка для зависимости запоминается, обход продолжается."""
        graph = build_graph("A", lookup({"A": ["X", "B"], "B": []}),
                            KeyError)
        self.assertIn("X", graph.errors)
        self.assertEqual(graph.edges["X"], [])
        self.assertIn("B", graph.edges)

    def test_missing_root(self):
        """Ошибка для корневого пакета передаётся дальше."""
        with self.assertRaises(KeyError):
            build_graph("Z", lookup({}), KeyError)

    def test_deep_chain(self):
        """Длинная цепочка не упирается в предел рекурсии Python."""
        size = 5000
        packages = {i: [i + 1] for i in range(size)}
        packages[size] = []
        graph = build_graph(0, lookup(packages))
        self.assertEqual(len(graph.edges), size + 1)


if __name__ == "__main__":
    unittest.main()
