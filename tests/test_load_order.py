"""Тесты порядка загрузки зависимостей."""

import unittest

from graph import build_graph
from load_order import broken_dependencies, load_order


def graph_of(packages, root="A"):
    """Граф зависимостей пакета root по словарю packages."""
    return build_graph(root, lambda name: packages[name])


class LoadOrderTest(unittest.TestCase):
    """Проверка load_order и broken_dependencies."""

    def assert_dependencies_first(self, packages, order):
        """Каждая зависимость стоит раньше зависящего от неё пакета."""
        for name, deps in packages.items():
            for dep in deps:
                self.assertLess(order.index(dep), order.index(name))

    def test_single(self):
        """Пакет без зависимостей."""
        self.assertEqual(load_order(graph_of({"A": []})), ["A"])

    def test_chain(self):
        """Цепочка загружается с конца."""
        packages = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(load_order(graph_of(packages)), ["C", "B", "A"])

    def test_diamond(self):
        """Общая зависимость загружается один раз и раньше всех."""
        packages = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        order = load_order(graph_of(packages))
        self.assertEqual(order, ["D", "B", "C", "A"])
        self.assert_dependencies_first(packages, order)

    def test_root_last(self):
        """Анализируемый пакет загружается последним."""
        packages = {"A": ["B", "C"], "B": ["C"], "C": []}
        order = load_order(graph_of(packages))
        self.assertEqual(order[-1], "A")
        self.assert_dependencies_first(packages, order)

    def test_no_broken_without_cycles(self):
        """Без циклов все зависимости загружаются раньше."""
        packages = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        graph = graph_of(packages)
        self.assertEqual(broken_dependencies(graph, load_order(graph)), [])

    def test_cycle(self):
        """В цикле один пакет неизбежно загружается раньше зависимости."""
        packages = {"A": ["B"], "B": ["C"], "C": ["A"]}
        graph = graph_of(packages)
        order = load_order(graph)
        self.assertEqual(order, ["C", "B", "A"])
        self.assertEqual(broken_dependencies(graph, order), [("C", "A")])

    def test_each_package_once(self):
        """Каждый пакет графа ровно один раз, даже при циклах."""
        packages = {"A": ["B", "C", "D"], "B": ["E", "F"], "C": ["F", "G"],
                    "D": ["A", "H"], "E": [], "F": ["G"], "G": ["C"],
                    "H": ["E"]}
        order = load_order(graph_of(packages))
        self.assertEqual(sorted(order), sorted(packages))


if __name__ == "__main__":
    unittest.main()
