"""Получение сведений о пакете из репозитория пакетов Python.

Используется JSON API репозитория (как у PyPI): по адресу
«<repository>/<пакет>/json» сервер возвращает описание последней
версии пакета, в том числе список зависимостей requires_dist.
Запросы выполняются средствами стандартной библиотеки (urllib).
"""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

TIMEOUT_SECONDS = 20
HTTP_NOT_FOUND = 404


class RepositoryError(Exception):
    """Ошибка получения данных из репозитория."""


@dataclass
class PackageInfo:
    """Сведения о пакете: имя, версия и строки зависимостей."""

    name: str
    version: str
    requires_dist: list


def package_url(repository, package):
    """Адрес JSON-описания пакета в репозитории."""
    return "{}/{}/json".format(repository.rstrip("/"), quote(package))


def download_json(url, package, opener=urlopen):
    """Загружает и разбирает JSON по адресу url."""
    try:
        with opener(url, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as err:
        if err.code == HTTP_NOT_FOUND:
            raise RepositoryError("пакет «{}» не найден в репозитории"
                                  .format(package)) from None
        raise RepositoryError("сервер вернул ошибку {} для {}"
                              .format(err.code, url)) from None
    except URLError as err:
        raise RepositoryError("не удалось подключиться к репозиторию: {}"
                              .format(err.reason)) from None
    except (OSError, ValueError) as err:
        raise RepositoryError("не удалось получить данные: {}"
                              .format(err)) from None


def parse_package(data):
    """Достаёт из JSON-ответа имя, версию и список зависимостей."""
    info = data.get("info") if isinstance(data, dict) else None
    if not isinstance(info, dict):
        raise RepositoryError("неожиданный формат ответа: нет поля info")
    requires = info.get("requires_dist") or []
    if not isinstance(requires, list) or not all(
            isinstance(item, str) for item in requires):
        raise RepositoryError("неожиданный формат поля requires_dist")
    return PackageInfo(str(info.get("name", "")),
                       str(info.get("version", "")), requires)


def fetch_package(repository, package, opener=urlopen):
    """Получает сведения о пакете package из репозитория repository."""
    url = package_url(repository, package)
    return parse_package(download_json(url, package, opener))
