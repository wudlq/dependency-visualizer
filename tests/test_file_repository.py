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
        packages, versions = parse_repository("A: B C\n\nB: C\nC:\n")
        self.assertEqual(packages, {"A": ["B", "C"], "B": ["C"], "C": []})
        self.assertEqual(versions, {})

    def test_versions(self):
        """Версия после имени пакета необязательна."""
        packages, versions = parse_repository("A 2.1.0: B\nB 1.4:\nC: B\n")
        self.assertEqual(packages, {"A": ["B"], "B": [], "C": ["B"]})
        self.assertEqual(versions, {"A": "2.1.0", "B": "1.4"})

    def test_bad_version(self):
        """Версия только из чисел через точку, не больше одной."""
        for text in ("A 1.x: B", "A 1.0 2.0:", "A v1:", "A 1.:"):
            with self.assertRaises(RepositoryError, msg=text):
                parse_repository(text)

    def test_load_file(self):
        """Файлы из tests/repos читаются."""
        packages, versions = load_repository(
            os.path.join(REPOS, "complex.txt"))
        self.assertEqual(packages["A"], ["B", "C", "D"])
        self.assertEqual(versions["A"], "5.0")

    def test_bad_format(self):
        """Строка без двоеточия."""
        with self.assertRaisesRegex(RepositoryError, "строка 2"):
            parse_repository("A: B\nB C\n")

    def test_bad_name(self):
        """Имена только из больших латинских букв."""
        for text in ("a: B", "A: b", "A1:", "A: B-C", "Б:", ": B"):
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
