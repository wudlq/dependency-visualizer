"""Тесты работы программы целиком (сеть подменяется)."""

import contextlib
import io
import os
import unittest
from unittest import mock

import main
from repository import PackageInfo, RepositoryError

CONFIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "configs")
PYPI = {
    "flask": ["blinker>=1.9.0", "jinja2>=3.1.2",
              'asgiref>=3.2; extra == "async"'],
    "blinker": [],
    "jinja2": ["MarkupSafe>=2.0"],
    "markupsafe": [],
}


def fake_fetch(*args):
    """Поддельный fetch_package(repository, name, opener) из словаря PYPI."""
    name = args[1]
    if name not in PYPI:
        raise RepositoryError("пакет «{}» не найден".format(name))
    return PackageInfo(name, "1.0", PYPI[name])


def run_main(config):
    """Запускает main с конфигурацией config, возвращает код и вывод."""
    out, err = io.StringIO(), io.StringIO()
    patch = mock.patch("repository.fetch_package", fake_fetch)
    with patch, contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(err):
        code = main.main([os.path.join(CONFIGS, config)])
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Проверка вывода графа зависимостей и обработки ошибок."""

    def test_pypi_graph(self):
        """Граф строится транзитивно, extra-зависимости не входят."""
        code, out, _ = run_main("valid_url.csv")
        self.assertEqual(code, 0)
        self.assertIn("Пакетов в графе: 4", out)
        self.assertIn("flask -> blinker, jinja2", out)
        self.assertIn("jinja2 -> markupsafe", out)
        self.assertNotIn("asgiref", out)

    def test_repository_error(self):
        """Корневого пакета нет в репозитории: ошибка и код 1."""
        code, _, err = run_main("pypi_not_found.csv")
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("не найден", err)

    def test_config_error(self):
        """Ошибка конфигурации."""
        code, _, err = run_main("bad_url.csv")
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("Ошибка конфигурации", err)

    def test_test_repo(self):
        """Граф из тестового репозитория."""
        code, out, _ = run_main("graph_simple.csv")
        self.assertEqual(code, 0)
        self.assertIn("A -> B, C", out)
        self.assertIn("D -> (нет)", out)
        self.assertIn("Циклических зависимостей нет", out)

    def test_test_repo_cycle(self):
        """Цикл выводится отдельно, программа завершается без ошибки."""
        code, out, _ = run_main("graph_cycle.csv")
        self.assertEqual(code, 0)
        self.assertIn("A -> B -> C -> A", out)

    def test_test_repo_missing_package(self):
        """Неизвестная зависимость: граф строится, ошибка выводится."""
        code, out, err = run_main("graph_missing.csv")
        self.assertEqual(code, 0)
        self.assertIn("A -> B, X", out)
        self.assertIn("X: пакет X не найден", err)

    def test_test_repo_errors(self):
        """Ошибки в файле тестового репозитория и неизвестный корень."""
        for config in ("graph_bad_format.csv", "graph_bad_name.csv",
                       "graph_duplicate.csv", "graph_unknown_root.csv"):
            code, _, err = run_main(config)
            self.assertEqual(code, main.EXIT_ERROR, config)
            self.assertIn("Ошибка репозитория", err)


if __name__ == "__main__":
    unittest.main()
