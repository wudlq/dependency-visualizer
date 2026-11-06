"""Тесты работы программы целиком (сеть подменяется)."""

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import main
from diagram import RenderError
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


def run_main(config, *options, render=None, show=None):
    """Запускает main с конфигурацией config, возвращает код и вывод.

    Сеть, программа d2 и просмотр изображения подменяются, файлы
    сохраняются во временную папку.
    """
    out, err = io.StringIO(), io.StringIO()
    render = render or mock.Mock(side_effect=lambda path: path + ".svg")
    with tempfile.TemporaryDirectory() as folder, \
            mock.patch("repository.fetch_package", fake_fetch), \
            mock.patch("main.OUTPUT_FOLDER", folder), \
            mock.patch("main.render", render), \
            mock.patch("main.show", show or mock.Mock()), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main.main([*options, os.path.join(CONFIGS, config)])
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Проверка вывода графа зависимостей и обработки ошибок."""

    def test_pypi_graph(self):
        """Граф строится транзитивно, extra-зависимости не входят."""
        code, out, _ = run_main("valid_url.csv")
        self.assertEqual(code, 0)
        self.assertIn("Пакетов в графе: 4", out)
        self.assertIn("flask 1.0 -> blinker, jinja2", out)
        self.assertIn("jinja2 1.0 -> markupsafe", out)
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
        self.assertIn("A 2.1.0 -> B, C", out)
        self.assertIn("D 0.9 -> (нет)", out)
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
        self.assertIn("A 1.0 -> B, X", out)
        self.assertIn("X: пакет X не найден", err)

    def test_test_repo_errors(self):
        """Ошибки в файле тестового репозитория и неизвестный корень."""
        for config in ("graph_bad_format.csv", "graph_bad_name.csv",
                       "graph_duplicate.csv", "graph_unknown_root.csv"):
            code, _, err = run_main(config)
            self.assertEqual(code, main.EXIT_ERROR, config)
            self.assertIn("Ошибка репозитория", err)

    def test_d2_and_image(self):
        """Описание D2 сохраняется, изображение делается и открывается."""
        show = mock.Mock()
        code, out, _ = run_main("graph_simple.csv", show=show)
        self.assertEqual(code, 0)
        self.assertIn("Описание графа на D2:", out)
        self.assertIn("Изображение графа:", out)
        show.assert_called_once()

    def test_no_show(self):
        """С --no-show изображение не открывается."""
        show = mock.Mock()
        run_main("graph_simple.csv", "--no-show", show=show)
        show.assert_not_called()

    def test_ascii_tree(self):
        """ASCII-дерево выводится, только если задан параметр."""
        _, out, _ = run_main("viz_test_complex.csv")
        self.assertIn("ASCII-дерево зависимостей:", out)
        self.assertIn("├── B 1.1", out)
        self.assertIn("A 5.0 (цикл)", out)
        _, out, _ = run_main("graph_complex.csv")
        self.assertNotIn("ASCII-дерево", out)

    def test_render_error(self):
        """Нет программы d2: ошибка и код 1, дерево всё равно выводится."""
        render = mock.Mock(side_effect=RenderError("d2 не найдена"))
        code, out, err = run_main("viz_test_complex.csv", render=render)
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("d2 не найдена", err)
        self.assertIn("ASCII-дерево", out)

    def test_bad_version_file(self):
        """Неверная версия в файле тестового репозитория."""
        code, _, err = run_main("graph_bad_version.csv")
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("неверная версия", err)


if __name__ == "__main__":
    unittest.main()
