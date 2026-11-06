"""Визуализация графа зависимостей на языке диаграмм D2.

Текст D2 строится программой. Изображение (SVG) из него делает
внешняя программа d2 (https://d2lang.com). Для показа рядом
создаётся HTML-страница с этим изображением, и она открывается
в браузере по умолчанию.
"""

import html
import os
import shutil
import subprocess
import webbrowser
from pathlib import Path

D2_PROGRAM = "d2"
ROOT_COLOR = "#cfe8ff"
ERROR_COLOR = "#ffd6d6"
DASHED = 3
PAGE = """<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>{title}</title></head>
<body style="margin:24px;font-family:sans-serif">
<h1 style="font-size:20px">Граф зависимостей: {title}</h1>
<img src="{image}" alt="{title}" style="max-width:100%">
</body>
</html>
"""


def quote(text):
    """Строка в двойных кавычках для D2 (кавычки и \\ экранируются)."""
    return '"{}"'.format(text.replace("\\", "\\\\").replace('"', '\\"'))


def node_lines(graph):
    """Описание узлов: подпись с версией, выделение корня и ошибок."""
    lines = []
    for name in graph.edges:
        key = quote(name)
        lines.append("{}: {}".format(key, quote(graph.label(name))))
        if name == graph.root:
            lines.append("{}.style.fill: {}".format(key, quote(ROOT_COLOR)))
            lines.append("{}.style.bold: true".format(key))
        if name in graph.errors:
            lines.append("{}.style.fill: {}".format(key, quote(ERROR_COLOR)))
            lines.append("{}.style.stroke-dash: {}".format(key, DASHED))
    return lines


def edge_lines(graph):
    """Описание рёбер «пакет -> зависимость»."""
    return ["{} -> {}".format(quote(name), quote(dep))
            for name, deps in graph.edges.items() for dep in deps]


def d2_text(graph):
    """Текстовое представление графа на языке D2."""
    lines = ["direction: down", ""]
    lines += node_lines(graph) + [""] + edge_lines(graph)
    return "\n".join(lines) + "\n"


def save_d2(graph, folder):
    """Сохраняет текст D2 в папку folder, возвращает путь к файлу."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, graph.root + ".d2")
    with open(path, "w", encoding="utf-8") as file:
        file.write(d2_text(graph))
    return path


class RenderError(Exception):
    """Не удалось получить изображение графа."""


def render(d2_path):
    """Делает из файла D2 изображение SVG программой d2."""
    if shutil.which(D2_PROGRAM) is None:
        raise RenderError("программа d2 не найдена; установите её: "
                          "brew install d2 (macOS) или "
                          "https://d2lang.com/tour/install")
    image = os.path.splitext(d2_path)[0] + ".svg"
    result = subprocess.run([D2_PROGRAM, d2_path, image],
                            capture_output=True, text=True, check=False)
    if result.returncode:
        raise RenderError("d2 завершилась с ошибкой: "
                          + result.stderr.strip())
    return image


def write_page(image):
    """Создаёт HTML-страницу с изображением, возвращает путь к ней."""
    name = os.path.basename(image)
    title = html.escape(os.path.splitext(name)[0])
    page = os.path.splitext(image)[0] + ".html"
    with open(page, "w", encoding="utf-8") as file:
        file.write(PAGE.format(title=title, image=html.escape(name)))
    return page


def show(image):
    """Показывает изображение SVG в браузере по умолчанию.

    Открывается HTML-страница с изображением, а не сам файл SVG:
    файл .svg система может отдать графическому редактору (например,
    Illustrator), а страница .html всегда открывается в браузере,
    который показывает SVG со встроенными шрифтами d2.
    """
    url = Path(write_page(image)).resolve().as_uri()
    if not webbrowser.open(url):
        raise RenderError("не удалось открыть изображение в браузере, "
                          "откройте файл вручную: " + image)
