"""Тесты получения данных из репозитория (без обращения к сети)."""

import io
import json
import unittest
from unittest import mock
from urllib.error import HTTPError, URLError

from repository import (RepositoryError, fetch_package, package_url,
                        pypi_dependencies)

REPOSITORY = "https://pypi.org/pypi"


def answer(data):
    """Поддельный urlopen, который возвращает data в виде JSON."""
    body = io.BytesIO(json.dumps(data).encode("utf-8"))
    return mock.Mock(return_value=body)


def failure(error):
    """Поддельный urlopen, который выбрасывает исключение error."""
    return mock.Mock(side_effect=error)


class FetchPackageTest(unittest.TestCase):
    """Проверка fetch_package на верных ответах и ошибках."""

    def test_url(self):
        """Адрес JSON-описания пакета."""
        self.assertEqual(package_url(REPOSITORY + "/", "requests"),
                         "https://pypi.org/pypi/requests/json")

    def test_package(self):
        """Обычный ответ с зависимостями."""
        info = {"name": "requests", "version": "2.32.3",
                "requires_dist": ["idna<4,>=2.5"]}
        opener = answer({"info": info})
        package = fetch_package(REPOSITORY, "requests", opener)
        opener.assert_called_once_with(
            "https://pypi.org/pypi/requests/json", timeout=20)
        self.assertEqual(package.version, "2.32.3")
        self.assertEqual(package.requires_dist, ["idna<4,>=2.5"])

    def test_no_dependencies(self):
        """requires_dist равен null — зависимостей нет."""
        info = {"name": "six", "version": "1.17.0", "requires_dist": None}
        package = fetch_package(REPOSITORY, "six", answer({"info": info}))
        self.assertEqual(package.requires_dist, [])

    def test_not_found(self):
        """Пакета нет в репозитории (HTTP 404)."""
        error = HTTPError("url", 404, "Not Found", None, None)
        with self.assertRaisesRegex(RepositoryError, "не найден"):
            fetch_package(REPOSITORY, "nope", failure(error))

    def test_server_error(self):
        """Другая ошибка HTTP."""
        error = HTTPError("url", 500, "Server Error", None, None)
        with self.assertRaisesRegex(RepositoryError, "500"):
            fetch_package(REPOSITORY, "requests", failure(error))

    def test_no_connection(self):
        """Сервер недоступен."""
        with self.assertRaisesRegex(RepositoryError, "подключиться"):
            fetch_package(REPOSITORY, "requests",
                          failure(URLError("no route")))

    def test_bad_answer(self):
        """Ответ не JSON или без нужных полей."""
        not_json = mock.Mock(return_value=io.BytesIO(b"<html></html>"))
        with self.assertRaises(RepositoryError):
            fetch_package(REPOSITORY, "requests", not_json)
        with self.assertRaisesRegex(RepositoryError, "info"):
            fetch_package(REPOSITORY, "requests", answer({"x": 1}))
        with self.assertRaisesRegex(RepositoryError, "requires_dist"):
            fetch_package(REPOSITORY, "requests",
                          answer({"info": {"requires_dist": "idna"}}))


class PypiDependenciesTest(unittest.TestCase):
    """Проверка функции получения зависимостей для графа."""

    def test_names(self):
        """Имена нормализуются, повторы и extra убираются."""
        info = {"name": "pandas", "version": "3.0", "requires_dist": [
            'numpy>=2.0; python_version < "3.14"',
            'numpy>=2.3; python_version >= "3.14"',
            "python_dateutil>=2.9",
            'pytest; extra == "test"']}
        get_dependencies = pypi_dependencies(REPOSITORY,
                                             answer({"info": info}))
        self.assertEqual(get_dependencies("pandas"),
                         ["numpy", "python-dateutil"])


if __name__ == "__main__":
    unittest.main()
