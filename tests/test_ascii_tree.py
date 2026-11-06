"""Тесты вывода зависимостей в виде ASCII-дерева."""

import unittest

from ascii_tree import tree_lines
from graph import build_graph


def tree_of(packages, versions=None):
    """ASCII-дерево графа пакета A по словарю packages."""
    graph = build_graph("A", lambda name: packages[name])
    graph.versions = versions or {}
    return tree_lines(graph)


class AsciiTreeTest(unittest.TestCase):
    """Проверка tree_lines на разных графах."""

    def test_single(self):
        """Пакет без зависимостей — одна строка."""
        self.assertEqual(tree_of({"A": []}, {"A": "1.0"}), ["A 1.0"])

    def test_tree(self):
        """Ветки рисуются символами ├── └── │, порядок сохраняется."""
        packages = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
        self.assertEqual(tree_of(packages), [
            "A",
            "├── B",
            "│   └── D",
            "└── C",
        ])

    def test_shared_dependency(self):
        """Общая зависимость показывается под каждым пакетом."""
        packages = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(tree_of(packages)[-1], "    └── D")
        self.assertEqual(len(tree_of(packages)), 5)

    def test_cycle(self):
        """Цикл отмечается, дерево не бесконечно."""
        packages = {"A": ["B"], "B": ["A"]}
        self.assertEqual(tree_of(packages, {"A": "1.0"}), [
            "A 1.0",
            "└── B",
            "    └── A 1.0 (цикл)",
        ])

    def test_self_cycle(self):
        """Пакет зависит сам от себя."""
        self.assertEqual(tree_of({"A": ["A"]}), ["A", "└── A (цикл)"])


if __name__ == "__main__":
    unittest.main()
