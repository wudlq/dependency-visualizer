"""Тесты тестового репозитория (граф из текстового файла)."""

import os
import unittest

from file_repository import (file_dependencies, load_repository,
                             parse_repository)
from repository import RepositoryError

REPOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repos")


class FileRepositoryTest(unittest.TestCase):
    """Проверка разбора файла тестового репозитория."""

    def test_parse(self):
        """Обычный файл с пустыми строками и пакетом без зависимостей."""
        packages = parse_repository("A: B C\n\nB: C\nC:\n")
        self.assertEqual(packages, {"A": ["B", "C"], "B": ["C"], "C": []})

    def test_load_file(self):
        """Файлы из tests/repos читаются."""
        packages = load_repository(os.path.join(REPOS, "complex.txt"))
        self.assertEqual(packages["A"], ["B", "C", "D"])

    def test_bad_format(self):
        """Строка без двоеточия."""
        with self.assertRaisesRegex(RepositoryError, "строка 2"):
            parse_repository("A: B\nB C\n")

    def test_bad_name(self):
        """Имена только из больших латинских букв."""
        for text in ("a: B", "A: b", "A1:", "A: B-C", "Б:"):
            with self.assertRaises(RepositoryError, msg=text):
                parse_repository(text)

    def test_duplicate(self):
        """Пакет описан дважды."""
        with self.assertRaisesRegex(RepositoryError, "повторно"):
            parse_repository("A: B\nB:\nA: C\n")

    def test_missing_file(self):
        """Файла нет."""
        with self.assertRaises(RepositoryError):
            load_repository(os.path.join(REPOS, "nope.txt"))

    def test_dependencies(self):
        """Функция получения зависимостей."""
        get_dependencies = file_dependencies({"A": ["B"], "B": []})
        self.assertEqual(get_dependencies("A"), ["B"])
        with self.assertRaisesRegex(RepositoryError, "не найден"):
            get_dependencies("Z")


if __name__ == "__main__":
    unittest.main()
