"""Разбор строк зависимостей пакетов Python (формат PEP 508).

Строка зависимости выглядит так:
    имя[доп1,доп2] спецификатор_версии ; маркер
например «PySocks!=1.5.7,>=1.5.6; extra == "socks"». Здесь разбор
сделан вручную, без сторонних библиотек.
"""

import re
from dataclasses import dataclass

NAME = re.compile(r"\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)")
EXTRA_MARKER = re.compile(r"\bextra\s*(==|!=)")
NAME_SEPARATORS = re.compile(r"[-_.]+")


class RequirementError(ValueError):
    """Строку зависимости не удалось разобрать."""


@dataclass
class Requirement:
    """Одна зависимость: имя, дополнения, версии и маркер окружения."""

    name: str
    extras: list
    specifier: str
    marker: str

    def is_optional(self):
        """Нужна ли зависимость только для дополнения (extra)."""
        return bool(EXTRA_MARKER.search(self.marker))

    def __str__(self):
        """Строка для вывода: имя, версии и маркер, если они есть."""
        text = self.name
        if self.specifier:
            text += " " + self.specifier
        if self.marker:
            text += " ; " + self.marker
        return text


def normalize_name(name):
    """Приводит имя пакета к единому виду (PEP 503): Foo_Bar -> foo-bar."""
    return NAME_SEPARATORS.sub("-", name).lower()


def split_extras(rest):
    """Отделяет список дополнений «[a,b]» от остатка строки."""
    if not rest.startswith("["):
        return [], rest
    end = rest.find("]")
    if end < 0:
        raise RequirementError("не закрыта скобка «[»")
    extras = [item.strip() for item in rest[1:end].split(",")]
    return [item for item in extras if item], rest[end + 1:].strip()


def parse_requirement(text):
    """Разбирает строку зависимости и возвращает Requirement."""
    requirement, _, marker = text.partition(";")
    match = NAME.match(requirement)
    if not match:
        raise RequirementError("не найдено имя пакета в «{}»".format(text))
    extras, rest = split_extras(requirement[match.end():].strip())
    specifier = rest.strip()
    if specifier.startswith("(") and specifier.endswith(")"):
        specifier = specifier[1:-1].strip()
    return Requirement(match.group(1), extras, specifier, marker.strip())


def direct_dependencies(requires_dist):
    """Обязательные прямые зависимости из списка строк requires_dist.

    Зависимости, нужные только для дополнений (маркер «extra == …»),
    не входят в обязательные и пропускаются. Возвращает список
    Requirement и список строк, которые не удалось разобрать.
    """
    result, bad = [], []
    for text in requires_dist:
        try:
            requirement = parse_requirement(text)
        except RequirementError:
            bad.append(text)
            continue
        if not requirement.is_optional():
            result.append(requirement)
    return result, bad
