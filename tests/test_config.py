"""Тесты чтения и проверки конфигурационного файла."""

import os
import tempfile
import unittest

from config import ConfigError, load_config

TESTS = os.path.dirname(os.path.abspath(__file__))
CONFIGS = os.path.join(TESTS, "configs")


def config_path(name):
    """Путь к файлу из папки tests/configs."""
    return os.path.join(CONFIGS, name)


class LoadConfigTest(unittest.TestCase):
    """Проверка load_config на верных и ошибочных файлах."""

    def errors_of(self, name):
        """Список ошибок, которые даёт файл конфигурации name."""
        with self.assertRaises(ConfigError) as context:
            load_config(config_path(name))
        return context.exception.errors

    def test_valid_url(self):
        """Верный файл для работы с URL репозитория."""
        config = load_config(config_path("valid_url.csv"))
        self.assertEqual(config.package_name, "flask")
        self.assertEqual(config.repository, "https://pypi.org/pypi")
        self.assertFalse(config.test_repo_mode)
        self.assertTrue(config.ascii_tree)

    def test_valid_test_repo(self):
        """Путь к тестовому репозиторию берётся от папки конфигурации."""
        config = load_config(config_path("valid_test_repo.csv"))
        self.assertTrue(config.test_repo_mode)
        self.assertTrue(os.path.isfile(config.repository))

    def test_items_order(self):
        """Параметры выводятся в порядке описания."""
        config = load_config(config_path("valid_url.csv"))
        names = [name for name, _ in config.items()]
        self.assertEqual(names, ["package_name", "repository",
                                 "test_repo_mode", "ascii_tree"])

    def test_missing_file(self):
        """Несуществующий файл конфигурации."""
        self.assertIn("не найден", self.errors_of("nope.csv")[0])

    def test_empty_file(self):
        """Пустой файл."""
        self.assertIn("пуст", self.errors_of("empty.csv")[0])

    def test_bad_header(self):
        """Неверная строка заголовка."""
        self.assertIn("parameter,value", self.errors_of("bad_header.csv")[0])

    def test_bad_columns(self):
        """Строка с лишним столбцом."""
        self.assertIn("2 столбца", self.errors_of("bad_columns.csv")[0])

    def test_missing_params(self):
        """Не заданы три параметра из четырёх."""
        self.assertEqual(len(self.errors_of("missing_params.csv")), 3)

    def test_unknown_param(self):
        """Неизвестный параметр."""
        self.assertIn("color", self.errors_of("unknown_param.csv")[0])

    def test_duplicate_param(self):
        """Параметр задан дважды."""
        self.assertIn("повторно", self.errors_of("duplicate_param.csv")[0])

    def test_package_errors(self):
        """Пустое и недопустимое имя пакета."""
        self.assertIn("пустым", self.errors_of("empty_package.csv")[0])
        self.assertIn("недопустимое", self.errors_of("bad_package.csv")[0])

    def test_repository_errors(self):
        """Пустой адрес, неверный URL, нет файла тестового репозитория."""
        self.assertIn("пустым", self.errors_of("empty_repository.csv")[0])
        self.assertIn("URL", self.errors_of("bad_url.csv")[0])
        self.assertIn("не найден",
                      self.errors_of("missing_test_repo.csv")[0])

    def test_bool_errors(self):
        """Неверные значения режимов работы."""
        self.assertIn("test_repo_mode",
                      self.errors_of("bad_test_mode.csv")[0])
        self.assertIn("ascii_tree", self.errors_of("bad_ascii_tree.csv")[0])

    def test_many_errors(self):
        """Все ошибки значений выводятся сразу."""
        self.assertEqual(len(self.errors_of("many_errors.csv")), 3)

    def test_bool_forms(self):
        """Режимы принимают true/false, yes/no, 1/0 в любом регистре."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "config.csv")
            with open(path, "w", encoding="utf-8") as file:
                file.write("parameter,value\npackage_name,requests\n"
                           "repository,https://pypi.org/pypi\n"
                           "test_repo_mode,NO\nascii_tree,1\n")
            config = load_config(path)
        self.assertFalse(config.test_repo_mode)
        self.assertTrue(config.ascii_tree)


if __name__ == "__main__":
    unittest.main()
