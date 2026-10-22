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


def run_main(config, fetch=None):
    """Запускает main с конфигурацией config, возвращает код и вывод."""
    out, err = io.StringIO(), io.StringIO()
    patch = mock.patch("main.fetch_package", fetch or mock.Mock())
    with patch, contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(err):
        code = main.main([os.path.join(CONFIGS, config)])
    return code, out.getvalue(), err.getvalue()


class MainTest(unittest.TestCase):
    """Проверка вывода прямых зависимостей и обработки ошибок."""

    def test_dependencies(self):
        """Выводятся только обязательные прямые зависимости."""
        package = PackageInfo("Flask", "3.1.3", [
            "blinker>=1.9.0", 'asgiref>=3.2; extra == "async"'])
        code, out, _ = run_main("valid_url.csv",
                                mock.Mock(return_value=package))
        self.assertEqual(code, 0)
        self.assertIn("Пакет: Flask 3.1.3", out)
        self.assertIn("Прямые зависимости (1):", out)
        self.assertIn("blinker >=1.9.0", out)
        self.assertNotIn("asgiref", out)

    def test_no_dependencies(self):
        """Пакет без зависимостей."""
        package = PackageInfo("six", "1.17.0", [])
        _, out, _ = run_main("pypi_six.csv",
                             mock.Mock(return_value=package))
        self.assertIn("Прямых зависимостей нет", out)

    def test_repository_error(self):
        """Ошибка репозитория выводится, код завершения 1."""
        fetch = mock.Mock(side_effect=RepositoryError("пакет не найден"))
        code, _, err = run_main("pypi_not_found.csv", fetch)
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("пакет не найден", err)

    def test_config_error(self):
        """Ошибка конфигурации: в репозиторий не обращаемся."""
        fetch = mock.Mock()
        code, _, err = run_main("bad_url.csv", fetch)
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("Ошибка конфигурации", err)
        fetch.assert_not_called()

    def test_test_repo_mode(self):
        """Режим тестового репозитория пока не поддерживается."""
        code, _, err = run_main("valid_test_repo.csv")
        self.assertEqual(code, main.EXIT_ERROR)
        self.assertIn("тестового репозитория", err)


if __name__ == "__main__":
    unittest.main()
