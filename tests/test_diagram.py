"""Тесты описания графа на D2 и получения изображения."""

import os
import subprocess
import tempfile
import unittest
from unittest import mock

from diagram import RenderError, d2_text, quote, render, save_d2, show
from graph import build_graph


def sample_graph():
    """Граф A -> B, C; B -> A (цикл); C не найден."""
    packages = {"A": ["B", "C"], "B": ["A"]}
    graph = build_graph("A", lambda name: packages[name], KeyError)
    graph.versions = {"A": "1.0", "B": "2.0"}
    return graph


class D2TextTest(unittest.TestCase):
    """Проверка текста на языке D2."""

    def test_nodes_and_edges(self):
        """Узлы подписаны версиями, рёбра — все связи графа."""
        text = d2_text(sample_graph())
        self.assertIn('"A": "A 1.0"', text)
        self.assertIn('"B": "B 2.0"', text)
        self.assertIn('"C": "C"', text)
        for edge in ('"A" -> "B"', '"A" -> "C"', '"B" -> "A"'):
            self.assertIn(edge, text)

    def test_styles(self):
        """Корень выделен цветом, пакет с ошибкой — пунктиром."""
        text = d2_text(sample_graph())
        self.assertIn('"A".style.bold: true', text)
        self.assertIn('"C".style.stroke-dash: 3', text)

    def test_quote(self):
        """Кавычки внутри имени экранируются."""
        self.assertEqual(quote('a"b'), '"a\\"b"')

    def test_save(self):
        """Файл сохраняется под именем корневого пакета."""
        with tempfile.TemporaryDirectory() as folder:
            path = save_d2(sample_graph(), folder)
            self.assertEqual(os.path.basename(path), "A.d2")
            with open(path, encoding="utf-8") as file:
                self.assertIn('"A" -> "B"', file.read())


class RenderTest(unittest.TestCase):
    """Проверка вызова программы d2 (сама программа подменяется)."""

    @mock.patch("diagram.shutil.which", return_value=None)
    def test_no_d2(self, _which):
        """Программа d2 не установлена."""
        with self.assertRaisesRegex(RenderError, "не найдена"):
            render("graph.d2")

    @mock.patch("diagram.subprocess.run")
    @mock.patch("diagram.shutil.which", return_value="/usr/bin/d2")
    def test_render(self, _which, run):
        """d2 вызывается с файлом D2 и именем SVG."""
        run.return_value = subprocess.CompletedProcess([], 0, "", "")
        self.assertEqual(render("out/A.d2"), "out/A.svg")
        self.assertEqual(run.call_args[0][0], ["d2", "out/A.d2", "out/A.svg"])

    @mock.patch("diagram.subprocess.run")
    @mock.patch("diagram.shutil.which", return_value="/usr/bin/d2")
    def test_render_error(self, _which, run):
        """d2 завершилась с ошибкой."""
        run.return_value = subprocess.CompletedProcess([], 1, "", "bad")
        with self.assertRaisesRegex(RenderError, "bad"):
            render("out/A.d2")

    @mock.patch("diagram.webbrowser.open", return_value=True)
    def test_show(self, browser):
        """В браузере открывается HTML-страница с изображением."""
        with tempfile.TemporaryDirectory() as folder:
            image = os.path.join(folder, "A.svg")
            show(image)
            url = browser.call_args[0][0]
            self.assertTrue(url.startswith("file://"))
            self.assertTrue(url.endswith("/A.html"))
            with open(os.path.join(folder, "A.html"), encoding="utf-8") as f:
                self.assertIn('<img src="A.svg"', f.read())

    @mock.patch("diagram.webbrowser.open", return_value=False)
    def test_show_error(self, _browser):
        """Браузер открыть не удалось."""
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RenderError, "открыть"):
                show(os.path.join(folder, "A.svg"))


if __name__ == "__main__":
    unittest.main()
